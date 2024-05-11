import datetime
def year():
    return str(datetime.datetime.now().year)

def copyright():
    if year() == "2023":
        return "© 2023 FoxWorld Ecosystem"
    else:
        return f"© 2023-{year()} FoxWorld Ecosystem"