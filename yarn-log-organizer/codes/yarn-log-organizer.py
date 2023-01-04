import os
import sys 
import logging
import argparse  
import pandas as pd
import utils.timestamp as timestamp
import utils.vailidate_date_format as date_format
import datetime
import json
import glob
from pathlib import Path


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def mstoMinute(time): 
    return float(time/1000/60)

def main(argv):

    #########################
    ### Arguments Parsing ###
    #########################
    # FILE_NAME     = argv[0] # fist valus of command line arguments is file name 
    startTime = ""
    endTime = "" 
    
    parser = argparse.ArgumentParser(description='yarn log organizer')
   
    # parser.add_argument('-u', '--url', dest='url', help='yarn resource manager url', required=False)
    parser.add_argument('-start', '--start', dest='start', help='Start time you want to collect ex) 2021-12-26-00:00:00,default:now()-14 days' , required= False)
    parser.add_argument('-end', '--end', dest='end',help='end time you want to collect ex) 2021-12-30-00:00:00, default : now()', required= False)
    parser.add_argument('-l', '--log', dest='log',help='yarn logs file from curl commands, no other option needed', required= False)
    parser.add_argument('-ld', '--log_dir', dest='log_dir',help='yarn logs file directory from curl commands, no other option needed', required= False)

    # rmUrl = args.url    ## Remove resource manager url args  by sangyeon
    args = parser.parse_args()
    startTime_Request = args.start
    endTime_Request = args.end
    logs = args.log
    logs_dir = args.log_dir


    # if (rmUrl is None) and  (logs is None) and (logs_dir is None):
    #     #print("usage (HTTP) : python yarn-log-organizer.py -i yarn-resoure-manager-ip -p 8088 (optional) -start 2022-01-01-00:00:00 -end 2022-01-14-00:00:00 (default now())")
    #     print("usage: python yarn-log-organizer.py -url http://yarn-resource-manager-ip:8088 -start 2022-01-01-00:00:00 -end 2022-01-14-00:00:00 (default now())" )
    #     print("Info:start, end time is optional, if you do not input start and end time, it will request latest 14 days application logs history by default")
    #     print("Info:Recommaned days (start ~ end time) is more than 7 days ")
    #     exit(1)

    if (logs is None) and (logs_dir is None):
        #print("usage (HTTP) : python yarn-log-organizer.py -i yarn-resoure-manager-ip -p 8088 (optional) -start 2022-01-01-00:00:00 -end 2022-01-14-00:00:00 (default now())")
        print("usage: python yarn-log-organizer.py -l file.json (optional) -start 2022-01-01-00:00:00 -end 2022-01-14-00:00:00 (default now())" )
        print("Info:start, end time is optional, if you do not input start and end time, it will request latest 14 days application logs history by default")
        print("Info:Recommaned days (start ~ end time) is more than 7 days ")
        exit(1)


    # Timeformat Validation : modified by sungyoul
    now = datetime.datetime.now()
    if startTime_Request:
        date_format.validateTimeFormat(startTime_Request)
    else :  
        startTime_Request = (now - datetime.timedelta(days=14)).strftime("%Y-%m-%d-%H:%M:%S")
        date_format.validateTimeFormat(startTime_Request)
    if endTime_Request:
            date_format.validateTimeFormat(endTime_Request)
    else :   
        endTime_Request = now.strftime("%Y-%m-%d-%H:%M:%S")
        date_format.validateTimeFormat(endTime_Request)

    print("*" * 40 )
    print("Collecting condition")
    print("*" * 40 )

    # if rmUrl:
    #     print("rm_url: {}".format(rmUrl))
    #     print("start time: {}".format(startTime_Request))
    #     print("end time: {}".format(endTime_Request))
    # elif logs:
    #     print("yarn-logs-json file from curl command: {}".format(logs))
    # elif logs_dir:
    #      print("directory of yarn-logs-json files from curl command: {}".format(logs_dir))
    
    if logs:
        print("yarn-logs-json file from curl command: {}".format(logs))
    elif logs_dir:
         print("directory of yarn-logs-json files from curl command: {}".format(logs_dir))


    # make startQuery
    startTime = timestamp.toTimeStamp(startTime_Request)
    startQuery = 'startedTimeBegin=' + startTime

    endTime = timestamp.toTimeStamp(endTime_Request)  
    endQuery = 'finishedTimeEnd=' + endTime

    data = ''

    if logs:
        try: 
            data = pd.read_json(logs)
        except:
            print("Check the log file path or format again") 
            sys.exit()
    
    elif logs_dir:
        try:
           
            file_list = glob.glob(os.path.join(logs_dir , "*"))
            temp = []
            for f in file_list:
                df = pd.read_json(f)
                df_list = df['apps']['app']
                temp = df_list + temp

            data = {"apps": {"app":temp}}
            #print(data.head())
            
        except:
            print("Check the directory of logs files or log file format again") 
            sys.exit()
    
    # case of no result from resource manager
    if len(data['apps']) == 0 :
        print("no result from yarn resourcemanager")
        sys.exit()

    delimeter = ','
    extract_headers = ['id', 'user', 'name', 'queue', 'applicationType', 'startedTime', 'finishedTime',
                       'elapsedTime', 'memorySeconds', 'vcoreSeconds']
    
    '''                   
    extract_headers = ['id', 'user', 'name', 'queue', 'applicationType', 'startedTime', 'launchTime', 'finishedTime',
                      'elapsedTime', 'memorySeconds', 'vcoreSeconds', 'state', 'finalStatus']
    '''
    ## Create output dataframe
    full_list =[]    ## extracted list from yarn log json
    resp_list = []
    df_output = pd.DataFrame(resp_list, columns=extract_headers, dtype=object)

    # ## Case 1 Multi Application API
    for list in data['apps']['app']:
        cleaned_data = []
        cleaned_extract_headers = []
        append_data=cleaned_data.append
        for header in extract_headers:
            for key, val in list.items():
                if key == header:
                    append_data(val)
                    cleaned_extract_headers.append(key)
                    break
        if len(cleaned_data) == len(extract_headers):
            full_list.append(cleaned_data)
        else:
            print(cleaned_extract_headers)
            df_loop = pd.DataFrame([cleaned_data], columns=cleaned_extract_headers)
            df_output = pd.concat([df_output, df_loop])     #df_output.append(df_loop)

    ## make csv files 
    df_full = pd.DataFrame(full_list, columns=extract_headers)
    df_output = pd.concat([df_output, df_full])
    
    ## etl processing
    ## Remove new line
    def removelines(value):
        #value = value.strip()
        value = value.replace("\n","").replace("\r","").replace(",","_").replace("\t","").replace("\"","").replace("'","")
        return str(value)
    
    df_output.drop_duplicates(subset=['id','startedTime','finishedTime'],keep='first',inplace=True)

    df_output['startedTime'] = df_output['startedTime'].apply(timestamp.toDateFromTimeStamp)
    df_output['finishedTime'] = df_output['finishedTime'].apply(timestamp.toDateFromTimeStamp)
    df_output['elapsedTime'] = df_output['elapsedTime'].apply(mstoMinute)
    df_output['name'] = df_output['name'].apply(removelines)

    print("*" * 40 )
    print("Collecting Result")
    print("*" * 40 )
    
    print("log count from yarn resource manager: {}".format(len(data['apps']['app'])))
    print("count files stored in csv: {}".format(len(df_output)))
    
    work_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(work_dir)
    if os.path.isdir("../../optimized-tco-calculator") == False :
        os.mkdir("../../optimized-tco-calculator")
    if os.path.isdir("../../optimized-tco-calculator/data") == False :
        os.mkdir("../../optimized-tco-calculator/data")
    if os.path.isdir("../../optimized-tco-calculator/data/yarn-app-logs") == False :
        os.mkdir("../../optimized-tco-calculator/data/yarn-app-logs")


    # make csv file names
    #format = f"%Y%m%d%H%M%S"
    format = "%Y-%m-%d-%H-%M-%S"
    '''
    start = datetime.datetime.fromtimestamp(int(startTime)/1000).strftime(format)
    end = datetime.datetime.fromtimestamp(int(endTime)/1000).strftime(format)
    '''
    requested_days = (datetime.datetime.strptime(endTime_Request,"%Y-%m-%d-%H:%M:%S") - datetime.datetime.strptime(startTime_Request,"%Y-%m-%d-%H:%M:%S")).days
    
    # Get the start, end time from collected logs , not from input parameter
    sorted_startedTime = df_output[ df_output.startedTime > '1971-01-01 00:00:00' ].startedTime.sort_values()
    log_start = sorted_startedTime.values[0].replace(" ","-").replace(":",'-')
    log_end = sorted_startedTime.values[-1].replace(" ","-").replace(":",'-')
    collected_days = (datetime.datetime.strptime(log_end,"%Y-%m-%d-%H-%M-%S") - datetime.datetime.strptime(log_start,"%Y-%m-%d-%H-%M-%S")).days

    csvFile = "cluster_yarn_log_{}_{}.csv".format(log_start, log_end)
    
    df_output.to_csv("../../optimized-tco-calculator/data/yarn-app-logs/{}".format(csvFile), sep=delimeter, mode='w', index=False)
    abs_path = os.path.abspath("../../optimized-tco-calculator/data/yarn-app-logs/"+ csvFile)

    print("Output file created at {}".format(abs_path))
    print("Collecting yarn logs completed")
    if requested_days > collected_days + 1:
        #print(bcolors.WARNING + "Warning:  Collected days {} is less than requested days(end - start time): {}".format(collected_days,requested_days))
        print("Yarn Resource Manager has max latest {} applications history in your environment".format(len(data['apps']['app'])))

    elif collected_days < 7 and collected_days >= 1   :   
        #print(bcolors.WARNING +"Warning -  Days of collected logs : {} days".format(collected_days))
        print("You may run this application more times in future days or change the start date to get at least 7 days application logs")
        print("Minimum days for analyis is 1 day, but recommend at leat 7 days for analyzing week pattern")
    elif collected_days < 1:
        #print(bcolors.WARNING +"Warning -  Days of collected logs is less than 1 days")
        print("You may run this application more times in future days to get more than 1 days. Recommand : 7 days")
    if logs and collected_days < 7 :
        #print(bcolors.WARNING +"Warning!! -  Days of collected logs from  {} is {} days".format(logs,collected_days))
        print("You may run this application more times in future days or change the start date to get at least 7 days application logs")
        print("Minimum days for analyis is 1 day, but recommend at leat 7 days for analyzing week pattern")


if __name__ == "__main__":

    # for loging config 
    logging.basicConfig(
        format = '%(asctime)s:%(levelname)s:%(message)s',
        datefmt = '%m/%d/%Y %I:%M:%S %p',
        level = logging.INFO
    )
    # logging.info('start programs')
    print("\n")
    print("Start yarn logs organizing from yarn log json file")
   
    main(sys.argv)
