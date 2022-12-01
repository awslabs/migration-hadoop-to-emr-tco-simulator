

from datetime import datetime

def validateTimeFormat( input_date ):
    
    # Timeformat Validation 
    # initializing format
    format = "%Y-%m-%d-%H:%M:%S"
    res = True
   
    try:
        res = bool(datetime.strptime(input_date, format))
    except ValueError:
        res = False
    if(res == False):
        print("invalid input date format please use this format ex) 2021-12-26-00:00:00")
        exit(1)


