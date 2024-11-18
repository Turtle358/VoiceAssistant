import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import timedelta


class GCalendar:
    """
    Class for interacting with Google Calendar API.
    Reference: https://developers.google.com/calendar/
    """
    def __init__(self):
        self.__SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.__MONTH = {'01': 'January',
                        '02': 'February',
                        '03': 'March',
                        '04': 'April',
                        '05': 'May',
                        '06': 'June',
                        '07': 'July',
                        '08': 'August',
                        '09': 'September',
                        '10': 'October',
                        '11': 'November',
                        '12': 'December'}

    def auth(self, path: str = './Commands/GCalendar/'):
        """
        Parameters
        ----------
        path

        Returns
        -------
        Authenticates with Google services.
        """
        creds = None
        if os.path.exists(f'{path}token.json'):
            creds = Credentials.from_authorized_user_file(f'{path}token.json', self.__SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f'{path}credentials.json', self.__SCOPES)
                creds = flow.run_local_server(port=0)

            with open(f'{path}/token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def getInfo(self, path: str = './Commands/GCalendar/', days: int = 7) -> str:
        """
        Parameters
        ----------
        path
        days
        Returns
        -------
        Gets calendar information from the Google API
        """
        try:
            service = build('calendar', 'v3', credentials=self.auth(path))

            # Call Calendar API
            currentTime = datetime.datetime.now().isoformat() + 'Z'  # 'Z' for UTC time

            # Getting 10 upcoming events, within 1 week
            now = datetime.datetime.now()
            endDate = (now + timedelta(days=days)).date()
            endDateStr = endDate.isoformat() + 'T23:59:59Z'
            eventsResult = service.events().list(calendarId='primary',
                                                  timeMin=currentTime,
                                                  maxResults=10,
                                                  singleEvents=True,
                                                  orderBy='startTime',
                                                  timeMax=endDateStr).execute()
            events = eventsResult.get('items', [])

            if not events:
                return ":tts:No upcoming event's found."

            calendarEvents = ':tts:Your upcoming events:'

            for event in events:
                start = event['start'].get('dateTime',event['start'].get('date'))

                if len(start) >= 11 and start[10] == 'T':
                    start = self.__ifNotAllDay(start)
                else:
                    start = self.__ifAllDay(start)
                summary = event['summary']
                calendarEvents += f'\non {start} you have {summary}'
            return calendarEvents
        except HttpError as error:
            print(f'An error occurred: {error}')

    def __ifNotAllDay(self, time: str) -> str:
        print(time)
        """
        Parameters
        ----------
        time
        Returns
        -------
        A private function that cleans up the formatting of the time (if it is not an all day
        event), it achieves this by splitting the date and time, removing the GMT offset,
        adding the gmt offset to the hour (and minute if necessary), and adds st, nd or th
        depending on the day of the month
        """

        date, time = time.split('T')

        offset = time.split('Z')[-1]
        if offset == '':
            hourOffset = 0
            minuteOffset = 0
        else:
            hourOffset = int(offset.split(':')[0])
            minuteOffset = int(offset.split(':')[-1])

        hour = int(time.split(':')[0])
        minute = int(time.split(':')[1])

        hour = str(hour + hourOffset).zfill(2)
        minute = str(minute + minuteOffset).zfill(2)

        time = f'{hour}:{minute}'
        month = self.__MONTH[date.split('-')[1]]
        day = str(int(date.split('-')[-1]))

        if day[-1] == '1':
            title = 'st'

        elif day[-1] == '2':
            title = 'nd'

        else:
            title = 'th'

        return f'{day}{title} of {month} at {time}'

    def __ifAllDay(self, date):
        """
        Parameters
        ----------
        date
        Returns
        -------
        A private function that functions similarly to __ifNotAllDay
        to make the outputted information look nicer
        """
        day = str(int(date.split('-')[-1]))
        month = self.__MONTH[date.split('-')[1]]

        if day[-1] == '1':
            title = 'st'

        elif day[-1] == '2':
            title = 'nd'

        else:
            title = 'th'
        return f'{day}{title} of {month}'


if __name__ == '__main__':
    print(GCalendar().getInfo('./', days=30))
