# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import pandas as pd
import argparse
from datetime import date
import re
import os
import warnings
import numpy as np

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

warnings.filterwarnings(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None



def get_input_file():
    parser = argparse.ArgumentParser()         
    parser.add_argument("--customer", "-c", type=str, help = "input customer name",required=False)                                  
    parser.add_argument("--logs", "-l", type=str, help = "input yarn-logs-file", required=True)
    parser.add_argument("--design","-d", type=str, help = "input cluster design file(xlsx)",required=True)
    args = parser.parse_args()
    return args   

def add_day_hour_columns(df):
    df['startedTime'] = pd.to_datetime(df['startedTime'], infer_datetime_format=True)
    df['hour'] = df['startedTime'].dt.hour
    df['date'] =df['startedTime'].dt.date
    df['hour'] = pd.to_numeric(df['hour']) 
    return(df)

def custom_split(sepr_list, str_to_split):
    # create regular expression dynamically
    regular_exp = '|'.join(map(re.escape, sepr_list))
    temp = re.split(regular_exp, str_to_split)
    result = [x for x in temp if x]
    return result

def log_filter_by_cluter_deisign(cluster_df,temp_logs_df,order,cluster_type):

    global new_row_count
    separators = ":", ";", ",", " ", "\n","|","  "

    #print(cluster_df)

    filter_queue =[s.strip() for s in custom_split(separators, cluster_df.queue[order])]
    filter_user = [s.strip() for s in custom_split(separators, cluster_df.user[order])]
    filter_apptype = [s.strip() for s in cluster_df.appType[order].split(",")]
    if cluster_type == 'T':
        filter_start =pd.to_numeric(cluster_df.startHour[order])
        filter_end = pd.to_numeric(cluster_df.endHour[order])
    #print(filter_start, filter_end)
 
    if cluster_df.user[order]!= 'ALL':
            if check_filter_is_valid(logs_unique_user, filter_user,"user"):
                is_filter_user = temp_logs_df['user'].isin(filter_user)
                df1_list = temp_logs_df[is_filter_user].id
            else :
                df1_list = temp_logs_df.id 
                print(bcolors.WARNING + "Cluster Name: {} --> User name(s) {} in cluster-deising-input file does not match to name of users in yarn-logs file..\n \
                    Please check name of users in cluster design excel sheet".format(cluster_df.clusterName[order], filter_user))
                exit(1)
    else : 
        df1_list = temp_logs_df.id 

    if cluster_df.queue[order] != 'ALL': 
        if check_filter_is_valid(logs_unique_queue, filter_queue,"queue") :
            is_filter_queue = temp_logs_df['queue'].isin(filter_queue)
            df2_list = temp_logs_df[is_filter_queue].id 
        else :
            df2_list = temp_logs_df.id
            print(bcolors.WARNING + "Cluster Name: {} --> queue names(s) {} in cluster-deising-input file does not match to name of queues in yarn-logs file..\n \
            Please check name of queue in cluster design excel sheet".format(cluster_df.clusterName[order], filter_queue))
            exit(1)
    else:
        df2_list = temp_logs_df.id
        
    if cluster_df.appType[order] != 'ALL':    
        
        if check_filter_is_valid(logs_unique_apptype, filter_apptype,"apptype"):
            is_filter_appType = temp_logs_df['applicationType'].isin(filter_apptype)
            df3_list = temp_logs_df[is_filter_appType].id
        else:
            df3_list = temp_logs_df.id
            print(bcolors.WARNING + "Cluster Name: {} --> appType names(s) {} in cluster-deising-input file does not match to name of appType in yarn-logs file..\n \
            Please check name of appType in cluster design excel sheet".format(cluster_df.clusterName[order], filter_apptype))
            exit(1)
    else :
        df3_list = temp_logs_df.id

    filters = pd.merge(pd.merge(df1_list, df2_list,on=['id'],how='inner'),df3_list,on=['id'],how='inner')

    if cluster_type == 'T':
        if filter_start > filter_end:
            mask = (temp_logs_df.hour >= filter_start) | (temp_logs_df.hour <= filter_end)
        else:
            mask = (temp_logs_df.hour >= filter_start) & (temp_logs_df.hour <= filter_end)
        is_filter_start_end = temp_logs_df[mask].id
        filters = pd.merge(filters,is_filter_start_end,how='inner')

    df = temp_logs_df[temp_logs_df['id'].isin(filters.id)]

    temp = pd.DataFrame()
    for d in df['date'].unique():
        temp = pd.DataFrame(df[df.date == d])
    '''
    if temp.shape[0] > 0:  
        for h in range(0,24):
            if ~temp.hour.isin([h]).any():
                s = pd.Series({'id': str(d)+" "+ str(h), 'name': 'NA', 'queue': 'NA','applicationType':'NA',\
                        "finishedTime":"NA",'elapsedTime':0.1,'memorySeconds':0.1,'vcoreSeconds':0.1,'date':d,'hour':h}, name=len(df))
                df = df.append(s)
                new_row_count = new_row_count + 1
    '''
    return(df) 

def check_and_make_dir(file_name):
    directory = os.path.dirname(file_name)
    if not os.path.exists(directory):
        os.makedirs(directory)

def check_filter_is_valid(logs_unique, filters,type):
        for f in filters:
            #print(f)
            if logs_unique.isin([f]).any().bool() == False:
                print(bcolors.WARNING + "Error!!: {} value of {} column in cluster design excel doesn't match to one of {} columns in yarn logs : {}." \
                                                .format( f, type, type,logs_unique.values.tolist()))
                exit(1)
                
        return(1)

if __name__ == '__main__':
    
    args = get_input_file()
    customer_name = args.customer
    yarn_log_input = args.logs
    cluster_design = args.design

    new_row_count =0 
    
    logs_df = pd.read_csv(yarn_log_input)

  
    # exclude unfinshed jobs...

    # covert sting to uppercase
    logs_df = logs_df.apply(lambda x: x.str.upper() if x.dtype == "object" else x)  

    logs_unique_queue = pd.DataFrame(logs_df['queue'].unique())
    logs_unique_user = pd.DataFrame(logs_df['user'].unique())
    logs_unique_apptype = pd.DataFrame(logs_df['applicationType'].unique())
    
    logs_df = logs_df[logs_df.startedTime <= logs_df.finishedTime]
    #logs_df = logs_df[logs_df.elapsedTime < 70]
    
    logsCount = logs_df.shape[0]
    
    cluster_df = pd.read_excel(cluster_design,sheet_name='EMR Design Info')
    cluster_df.sort_values(by='clusterOrder',ignore_index=True,inplace=True)
    cluster_df[['queue', 'user', 'appType']] = cluster_df[['queue', 'user', 'appType']].fillna('ALL')
    cluster_df=cluster_df.apply(lambda x: x.str.upper() if x.dtype == "object" else x)

# seperate yanlogs according to cluster design info 
    emr_cluster = pd.DataFrame()
    temp_df = pd.DataFrame()
    final_input_tco_cluster = pd.DataFrame()
    temp_logs_df = logs_df.copy()
    temp_logs_df = add_day_hour_columns(temp_logs_df)

    for order in range(0, len(cluster_df.clusterOrder)):     
        if cluster_df.clusterType[order] == 'P' : 
            #print(temp_logs_df.head())
            filtered_logs_df = log_filter_by_cluter_deisign(cluster_df,temp_logs_df,order,"P")
            
            filtered_logs_df['clusterType'] = cluster_df.clusterType[order]
            filtered_logs_df['clusterName'] = cluster_df.clusterName[order]
            emr_cluster = pd.concat([emr_cluster,filtered_logs_df])
         
            temp_logs_df = temp_logs_df[~logs_df['id'].isin(filtered_logs_df.id)]
       
        
        elif cluster_df.clusterType[order] == 'T' :
            filtered_logs_df = log_filter_by_cluter_deisign(cluster_df,temp_logs_df,order,"T")
            # filtered_logs_df.head(10)
            filtered_logs_df['clusterType'] = cluster_df.clusterType[order]
            filtered_logs_df['clusterName'] = cluster_df.clusterName[order]
            emr_cluster = pd.concat([emr_cluster,filtered_logs_df]) 
         
            temp_logs_df = temp_logs_df[~logs_df['id'].isin(filtered_logs_df.id)]
            

    if True : #emr_cluster.shape[0] == logs_df.shape[0]
        
        # P-Type Cluster aggreation by hour
        #emr_cluster = generate
        p_emr_cluster = emr_cluster[emr_cluster['clusterType']=='P']
        #print("shape of P-emr :",p_emr_cluster.shape[0])


        if p_emr_cluster.shape[0] > 0 : 
            print("starting hourly agg. - Persistent type")
            for name in list(set(p_emr_cluster.clusterName)):
                print("EMR Cluster Name - {}".format(name))
                temp_p_df  = p_emr_cluster[p_emr_cluster['clusterName']==name]

                temp_p_df2 =  temp_p_df.groupby(['clusterType','clusterName','date','hour'],as_index=False).\
                                agg({'memorySeconds':'sum','vcoreSeconds':'sum','elapsedTime':'mean'})
                
                input_tco_cluster = temp_p_df2.groupby(['clusterType','clusterName','hour'],as_index=False).\
                                agg({'memorySeconds':'mean','vcoreSeconds':'mean','elapsedTime':'mean'})

                final_input_tco_cluster = pd.concat([final_input_tco_cluster, input_tco_cluster])

        # T Type cluster aggreation from starhour - end hour
        t_emr_cluster = emr_cluster[emr_cluster['clusterType']=='T']
        if t_emr_cluster.shape[0] > 0 :
            print("starting hourly agg. - Transient type")
            
            for name in list(set(t_emr_cluster.clusterName)):
                    print("EMR Cluster Name - {}".format(name))
                  
                    temp_df  = t_emr_cluster[t_emr_cluster['clusterName']==name]
                    temp_df2  = temp_df.groupby(['clusterType','clusterName','date'],as_index=False).\
                            agg({'memorySeconds':'sum','vcoreSeconds':'sum','elapsedTime':'sum'})
                    #print(temp_df2)
                    temp_df3 =  temp_df2.groupby(['clusterType','clusterName'],as_index=False).\
                            agg({'memorySeconds':'mean','vcoreSeconds':'mean','elapsedTime':'mean'}) 
                    #print(temp_df3)
                    startHour = cluster_df[cluster_df['clusterName']== name ].startHour.values[0]
                    endHour = cluster_df[cluster_df['clusterName']== name ].endHour.values[0]
                    print("starthour, endhour ",startHour,endHour)
                    if startHour > endHour:
                        hours = (24-startHour) + endHour
                    else: hours  = endHour - startHour + 1
            
                    mean_memory_usage = round(temp_df3.memorySeconds[0] / hours,2)
                    mean_vcore_usage =  round(temp_df3.vcoreSeconds[0]  / hours ,2)
                    mean_elapsed_time = round(temp_df3.elapsedTime[0]/ hours,2)
              
                    hours = np.arange(24)
                    for h in np.roll(hours, -int(startHour)):
                        row = {'clusterType':'T', 'clusterName':name,'hour':h,'memorySeconds':mean_memory_usage,\
                                'vcoreSeconds':mean_vcore_usage,"elapsedTime":mean_elapsed_time}
                        df_row = pd.DataFrame(row, index = [0])
                        final_input_tco_cluster = pd.concat([final_input_tco_cluster, df_row], ignore_index=True)
                      
                        if h == int(endHour) : break

        # if missing hour is existed ,then add missing hour , set mem,vcore,elpased to 0.1
        
        for c in final_input_tco_cluster['clusterName'].unique():
            temp = final_input_tco_cluster[final_input_tco_cluster['clusterName']==c]
            if temp.clusterType.iloc[0] == 'P':            
                for h in range(0,24):
                    if ~temp.hour.isin([h]).any():
                        print(h)
                        s = pd.Series({'clusterType': temp.clusterType.iloc[0],'clusterName': c,\
                            'elapsedTime':0.1,'memorySeconds':0.1,'vcoreSeconds':0.1,'hour':h}, name=len(temp_df))
                        print("s.head:",s.head())
                        final_input_tco_cluster = pd.concat([final_input_tco_cluster, s])
                        new_row_count = new_row_count + 1

        final_input_tco_cluster.sort_values(by=['clusterType','clusterName','hour'],ignore_index=True,inplace=True)

        today = date.today()
        work_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(work_dir)
        outputfile ="../../data/hourly-aggregated-app-logs/{}-hourly-aggregated-app-logs-tco-input-{}.xlsx".format(customer_name,today)

        check_and_make_dir(outputfile)
    
        final_input_tco_cluster.to_excel(outputfile,sheet_name="tco-input-logs",index=False)
   
        print( final_input_tco_cluster)
        print("\nSuccess..... {}".format(os.path.abspath(outputfile)))
    
    if emr_cluster.shape[0] - new_row_count +1 < logs_df.shape[0] :
        variance = round((1-(emr_cluster.shape[0]-new_row_count)/logs_df.shape[0])*100,2)
        print(bcolors.WARNING + "Warning! : Orginal Log counts is not equal to log number after mapping to new emr cluster design, Please Chek Cluster Design Excel File again!!!" + bcolors.ENDC)
        print("Original Log number : {}, hourly Aggreated logs #accoridng to cluster design excel file: {}, Variance : {}%"\
             .format(bcolors.WARNING + str(logs_df.shape[0]) + bcolors.ENDC, bcolors.FAIL + \
                  str(emr_cluster.shape[0]-new_row_count) + bcolors.ENDC,bcolors.OKBLUE+ str(variance)))
