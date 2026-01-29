import datetime
from datetime import timezone, timedelta

def year():
    return str(datetime.datetime.now().year)

def copyright():
    return f"© 2023-{year()} FoxWorld Ecosystem"

def get_timestamp():
    tzinfo = timezone(timedelta(hours=+3))
    date = str(datetime.datetime.now(tzinfo)).split('.')[0]
    date_format = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    return f"<t:{int(str(datetime.datetime.timestamp(date_format)).split('.')[0])}:f>"
