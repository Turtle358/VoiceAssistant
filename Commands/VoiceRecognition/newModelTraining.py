from datasets import load_dataset, Audio
from dataclasses import dataclass
from transformers import AutoProcessor
from transformers import AutoModelForCTC, TrainingArguments, Trainer
from typing import Dict, List, Union
import numpy as np
import torch

"""
References: https://huggingface.co/docs/transformers/tasks/asr
"""
# Since running in WSL, send to D:\ drive in windows, since on my computer, it has more storage available
# change depending on your PC
DOWNLOAD_CONFIG = '/mnt/d/huggingface'


class Eval:
    """
    References: https://github.com/victor369basu/End2EndAutomaticSpeechRecognition/ for WER calculations
    Class for calculating Word Error Rate (WER) using Levenshtein distance
    WER is a common metric used in Automatic Speech Recognition (ASR) tasks
    """
    def levenshteinDistance(self, reference: str, prediction: str, referenceLen: int, predictionLen: int):
        """
        Levenshtein distance is a metric used to measure the distance between 2 sequences.
        It calculates the minimum number of single-character edits required to change one sequence
        into another.
        Code inspired by: https://www.geeksforgeeks.org/introduction-to-levenshtein-distance/
        """
        if referenceLen == 0:
            return predictionLen
        if predictionLen == 0:
            return referenceLen
        if reference[referenceLen-1] == prediction[predictionLen-1]:
            return self.levenshteinDistance(reference, prediction, referenceLen-1, predictionLen-1)

        insertCost = self.levenshteinDistance(reference, prediction, referenceLen, predictionLen-1)
        removeCost = self.levenshteinDistance(reference, prediction, referenceLen-1, predictionLen)
        replaceCost = self.levenshteinDistance(reference, prediction, referenceLen-1, predictionLen-1)

        return 1 + min(insertCost, min(removeCost, replaceCost))

    def wordErrors(self, reference, prediction, delimiter: str = ' ') -> tuple:
        # This sets everything to lower case
        refWords = reference.split(delimiter)
        predWords = prediction.split(delimiter)

        # It then calculates the levenshtein distance for the WER
        levDistance = self.levenshteinDistance(refWords, predWords, len(refWords), len(predWords))
        return float(levDistance), len(refWords)

    def wer(self, reference, prediction, delimiter: str = ' ') -> dict:
        """
        Calculates the word error rate for the prediction against the target text
        """
        reference = reference.lower()
        prediction = prediction.lower()
        editDistance, refLen = self.wordErrors(reference, prediction, delimiter)

        if refLen == 0:
            raise ValueError("Reference's word number should be greater than 0.")
        wer = float(editDistance) / refLen
        print(f'WER: {wer}')
        return wer


@dataclass
class DataCollatorCTCWithPadding:
    """
    Collator - https://www.merriam-webster.com/dictionary/collator
    Data collator class for padding input and label sequences
    Used during training to handle sequences of different lengths
    """
    processor: AutoProcessor
    padding: Union[bool, str] = "longest"

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lengths and need
        # different padding methods

        inputFeatures = [{"input_values": feature["input_values"][0]} for feature in features]
        labelFeatures = [{"input_ids": feature["labels"]} for feature in features]
        batch = self.processor.pad(inputFeatures, padding=self.padding, return_tensors="pt")
        labelsBach = self.processor.pad(labels=labelFeatures, padding=self.padding, return_tensors="pt")
        
        # replace padding with -100 to ignore loss correctly
        labels = labelsBach["input_ids"].masked_fill(labelsBach.attention_mask.ne(1), -100)
        batch["labels"] = labels
        return batch


class RunModel:
    """
    Class responsible for running the ASR model training process
    it initialises dataset, processor, and handles model training
    """
    def __init__(self):
        """
        Initialises the dataset, processor, and other necessary components
        Downloads the VoxPopuli dataset and create a processor for ASR
        Preprocess' the dataset by converting text to uppercase
        """
        self.dataset = load_dataset("facebook/voxpopuli",
                                    name="en",
                                    split="train[:100]",
                                    cache_dir=DOWNLOAD_CONFIG)
        self.dataset = self.dataset.train_test_split(test_size=0.2)
        self.dataset = self.dataset.remove_columns(["audio_id", "language", "raw_text", 'gender', 'speaker_id',
                                                    'is_gold_transcript', 'accent'])

        self.processor = AutoProcessor.from_pretrained("facebook/wav2vec2-base",
                                                       cache_dir=DOWNLOAD_CONFIG)

        self.dataset = self.dataset.cast_column("audio", Audio(sampling_rate=16_000))

        dataset = self.dataset.map(self.uppercase)

        self.encodedDataset = dataset.map(self.prepareDataset, remove_columns=dataset.column_names["train"], num_proc=4)
        self.dataCollator = DataCollatorCTCWithPadding(processor=self.processor, padding="longest")

    def prepareDataset(self, batch):
        audio = batch["audio"]
        batch = self.processor(audio["array"], sampling_rate=audio["sampling_rate"], text=batch["normalized_text"])
        batch["input_length"] = len(batch["input_values"][0])
        return batch

    def uppercase(self, example):
        return {"normalized_text": example["normalized_text"].upper()}

    def computeMetrics(self, pred):
        wordErrorRates = []
        predLogits = pred.predictions
        predIds = np.argmax(predLogits, axis=-1)

        pred.label_ids[pred.label_ids == -100] = self.processor.tokenizer.pad_token_id

        predStr = self.processor.batch_decode(predIds)
        labelStr = self.processor.batch_decode(pred.label_ids, group_tokens=False)
        for i,item in enumerate(predStr):
            wordErrorRates.append(Eval().wer(reference=item, prediction=labelStr[i]))
        wordErrorRateMean = sum(wordErrorRates) / len(wordErrorRates)
        return {"wer": wordErrorRateMean}

    def train(self):
        try:
            # load the model
            model = AutoModelForCTC.from_pretrained('./savedModel')
            # load the processor
            model = model.from_pretrained('facebook/wav2vec2-base')
        except:
            model = AutoModelForCTC.from_pretrained(
                "facebook/wav2vec2-base",
                ctc_loss_reduction="mean",
                pad_token_id=self.processor.tokenizer.pad_token_id
            )
        model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        trainingArgs = TrainingArguments(
            output_dir="savedModel",
            per_device_train_batch_size=8,
            gradient_accumulation_steps=2,
            learning_rate=1e-5,
            warmup_steps=500,
            max_steps=2000,
            gradient_checkpointing=True,
            fp16=True if torch.cuda.is_available() else False,
            group_by_length=True,
            evaluation_strategy="steps",
            per_device_eval_batch_size=8,
            save_steps=1000,
            eval_steps=1000,
            logging_steps=25,
            load_best_model_at_end=True,
            metric_for_best_model="wer",
            greater_is_better=False,
            push_to_hub=False,
            num_train_epochs=int(input('Please enter the number of epochs to learn: ')))

        trainer = Trainer(
            model=model,
            args=trainingArgs,
            train_dataset=self.encodedDataset["train"],
            eval_dataset=self.encodedDataset["test"],
            tokenizer=self.processor,
            data_collator=self.dataCollator,
            compute_metrics=self.computeMetrics)

        trainer.train()
        trainer.save_model('./savedModel')


if __name__ == '__main__':
    model = RunModel()
    model.train()
