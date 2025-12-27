from datetime import datetime

def date_now():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")