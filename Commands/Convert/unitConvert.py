from re import fullmatch


class Convert:
    def __init__(self) -> None:
        """
        Gets base multipliers to convert imperial to metric and vice versa
        """
        # Lists of metric and imperial units
        # Using "american" spelling due to the nature of the neural network
        self.__MetricUnits = ['kilometer',
                              'km',
                              'meter',
                              'm',
                              'centimeter',
                              'cm',
                              'millimeter',
                              'mm',
                              'liter',
                              'l',
                              'milliliter',
                              'ml',
                              'gram',
                              'g',
                              'kilogram',
                              'kg',
                              'celsius',
                              'c',
                              'kilometers',
                              'meters',
                              'centimeters',
                              'millimeters',
                              'liters',
                              'milliliter',
                              'grams',
                              'kilogram']
        self.__ImperialUnits = ['yard',
                                'mile',
                                'inch',
                                'ounce',
                                'pound',
                                'stone',
                                'fl ounce',
                                'fluid ounce',
                                'pint',
                                'gallon',
                                'fahrenheit',
                                'f',
                                'yards',
                                'miles',
                                'inches',
                                'ounces',
                                'pounds',
                                'fl ounces',
                                'fluid ounces',
                                'pints',
                                'gallons']
        # Dictionary of metric unit symbols
        self.__MetricUnitSymbols = {'millimeter': 'm',
                                    'centimeter': 'cm',
                                    'meter': 'm',
                                    'kilometer': 'km',
                                    'gram': 'g',
                                    'kilogram': 'kg'}
        # Dictionary of metric unit standardisers
        self.__MetricStandardiser ={'mm': 1e-6,
                                    'cm': 1e-5,
                                    'm': 1e-3,
                                    'km': 1,
                                    'g': 1e-3,
                                    'kg': 1}
        # Defining conversion Rates
        # Length
        self.__KMToYard = 1093.613
        self.__KMToMile = 0.6213712
        self.__KMToInch = 39370.08
        # Weight
        self.__KGToOunce = 35.27396
        self.__KGToPound = 2.204623
        self.__KGToStone = 0.157473
        # Volume
        self.__LitreToFLOunce = 33.814022558919
        self.__LitreToPint = 1.759754
        self.__LitreToGallon = 0.2199693
        # Speed
        self.__KMHToMPH = 0.6213712

    def metricToStandard(self, query):
        """
        Parameters
        ----------
        query

        Returns
        -------
        Converts metric to standard Système International units (i.e. metre and kilogram)
        """

        numbers = int(''.join(x for x in query if bool(fullmatch('[0-9]', x))))
        unit = query.split(f'{str(numbers)} ')[1]
        unit = unit.split(' ')[0]
        try:
            unit = self.__MetricUnitSymbols[unit.strip(' ')]
        except KeyError:
            pass
        standardisedNumber = round(numbers * self.__MetricStandardiser.get(unit, 1), 3)
        return standardisedNumber

    def metricToImperial(self, query):
        """
        Parameters
        ----------
        query
        Returns
        -------
        Converts metric units (real units) to the imperial system (should you want to do that...)
        """
        number = ''.join(x for x in query if x.isdigit())
        if any(i in query for i in ['fahrenheit', 'f']):
            return f'{int(number)*9/5+32}°F'
        standardisedNumber = self.metricToStandard(query)

        if 'yard' in query:
            return f'{number} is {round(standardisedNumber*self.__KMToYard, 5)} Yards'

        elif 'mile' in query:
            return f'{number} is {round(standardisedNumber*self.__KMToMile, 5)} Miles'

        elif 'inch' in query:
            return f'{number} is {round(standardisedNumber*self.__KMToInch, 5)} Inches'

        elif 'ounce' in query:
            return f'{number} is {round(standardisedNumber*self.__KGToOunce, 5)} Ounce'

        elif 'pound' in query:
            return f'{number} is {round(standardisedNumber*self.__KGToPound, 5)} Pounds'

        elif 'stone' in query:
            return f'{number} is {round(standardisedNumber*self.__KGToStone, 5)} Stone'

        elif any(i in query for i in ['fl ounce', 'fluid ounce']):
            return f'{number} is {round(standardisedNumber*self.__LitreToFLOunce, 5)} fl oz'

        elif 'pint' in query:
            return f'{number} is {round(standardisedNumber*self.__LitreToPint, 5)} Pint'

        elif 'gallon' in query:
            return f'{number} is {round(standardisedNumber*self.__LitreToGallon, 5)} Gallon'

        return "Those Units are incompatible with eachother"

    def imperialToMetric(self, query):
        """
        Parameters
        ----------
        query
        Returns
        -------
        Converts Imperial units to metric units
        """
        # If number is a digit (0-9) this generator will put it into a string together

        number = ''.join(x for x in query if x.isdigit())
        if any(i in query for i in ['celsius', 'c']):
            return f'{(int(number) - 32)*5/9}°C'
        standardNumber = int(number)

        if 'yard' in query:
            return f'{round(standardNumber/self.__KMToYard, 5)} kilometre'

        elif 'mile' in query or 'miles' in query:
            return f'{round(standardNumber/self.__KMToMile, 5)} kilometre'

        elif 'inch' in query:
            return f'{round(standardNumber/self.__KMToInch, 5)} kilometre'

        elif 'ounce' in query:
            return f'{round(standardNumber/self.__KGToOunce, 5)} Kilogram'

        elif 'pound' in query:
            return f'{round(standardNumber/self.__KGToPound, 5)} Kilogram'

        elif 'stone' in query:
            return f'{round(standardNumber/self.__KGToStone, 5)} Kilogram'

        elif any(i in query for i in ['fl ounce', 'fluid ounce']):
            return f'{round(standardNumber/self.__LitreToFLOunce, 5)} Litre'

        elif 'pint' in query:
            return f'{round(standardNumber/self.__LitreToPint, 5)} Litre'

        elif 'gallon' in query:
            return f'{round(standardNumber/self.__LitreToGallon, 5)} Litre'

        return "Those Units are incompatible with each other"

    def whatTo(self, query):
        """
        Parameters
        ----------
        query
        Returns
        -------
        Finds out what the user wants to do.
        """
        # Organise the query to make all unit's singular, remove numbers
        if query[-1] == 's':
            query = query[:-1]

        query = query.strip(''.join(x for x in query if x.isdigit()))
        query = query.split(' ')

        # Check if the user wants to convert to imperial or metric
        for i in range(len(query)):
            if query[i] in self.__MetricUnits:
                for j in range(i, len(query)):
                    if query[j] in self.__ImperialUnits:
                        return "imperial"

        for x in range(len(query)):
            if query[x] in self.__ImperialUnits:
                for y in range(x, len(query)):
                    if query[y] in self.__MetricUnits:
                        return "metric"
        return None

    def converter(self, query):
        """
        Parameters
        ----------
        query
        Returns
        -------
        Simple interface to the unit conversions
        """
        if self.whatTo(query) == 'metric':
            return f':tts:{self.imperialToMetric(query)}'

        elif self.whatTo(query) == 'imperial':
            return f':tts:{self.metricToImperial(query)}'

        else:
            return ':tts:That is not a valid unit'
Convert = Convert()

if __name__ == '__main__':
    print(Convert.converter(input('What would you like to convert?: ')))
