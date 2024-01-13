import datetime

def time():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

def year():
    return str(datetime.datetime.now().year)

def copyright():
    if year() == "2023":
        return "© 2023 FoxWorld Ecosystem"
    else:
        return f"© 2021-{year()} FoxWorld Ecosystem"