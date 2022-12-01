from datetime import datetime
import time

''''
Return timestamp ( millisecond )
'''
def toTimeStamp( date ):

    timestamp = int(time.mktime(datetime.strptime(date, '%Y-%m-%d-%H:%M:%S').timetuple()))
    timestamp = str(timestamp)+"000" ## make to the millisecond
    # print(timestamp)
    return timestamp

def toDateFromTimeStamp( timestamp ):
    
    return datetime.fromtimestamp(int(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')



# Test Main
if __name__ == "__main__":
    toTimeStamp('2021-08-01 00:00:00') # 1627743600
    toTimeStamp('2021-08-31 23:59:59') # 1630421999
