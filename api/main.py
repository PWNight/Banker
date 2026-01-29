import datetime
def year():
    return str(datetime.datetime.now().year)

def copyright():
    return f"© 2023-{year()} FoxWorld Ecosystem"