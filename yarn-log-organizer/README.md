# yarn-log-organizer
- You can parse customer-yarn-logs-json files of curl command outputs offline using yarn-log-organizer.py


## Setup your environment
Required:
- **python 2.7 or python 3(Tested on 2.7, 3.6, 3.7, 3.8)**
- Install dependencies
  - Using pip with requirements.txt
    > **pip needs to be installed.**
    ```
    pip3 install -r requirements.txt 
    ```
  - Using setup.py
    ```
    python2 setup.py install --user
    ```
    OR
    ```
    python3 setup.py install --user
    ```
    

## Usage
### Running python application on your local machine
> NOTICE: Output files will be saved in optimized-tco-calculator/data/yarn-app-logs/ directory as "cluster_yarn_log_yyyy-MM-dd-hh-mm-ss_yyyy-MM-dd-hh-mm-ss.csv"
>> Prereqsuite Python modules: pandas, requests

> **For more accurate workload analysis, at least 7 days of data are required.**
#### Parameters
- -ld: (multile logs) python3 yarn-log-organizer.py -ld /path/  (just specifiy directory name including all json logs of curl command output. This tool automatically remove  duplicated jobs logs if any)
- -l: (single log) python3 yarn-log-organizer.py -l /path/customer-yarn-logs-json.txt

For example, the following command retrieves the organized resource manager logs.
- Run example
```
python3 yarn-log-organizer.py  -ld /Users/admin/Desktop/demo/


Start yarn logs collecting from API


****************************************
Collecting condition
****************************************
directory of yarn-logs-json files from curl command: /Users/admin/Desktop/demo/
****************************************
Collecting Result
****************************************
log count from yarn resource manager: 21160
count files stored in csv: 10735
Output file created at /Users/admin/hadoop-migration-assessment-tco/optimized-tco-calculator/data/yarn-app-logs/cluster_yarn_log_2022-04-16-05-06-46_2022-05-17-12-10-44.csv
Collecting yarn logs completed
```


Result file(collected yarn logs) generated in output directory.

- Result sample:

id,user,name,queue,applicationType,startedTime,finishedTime,elapsedTime,memorySeconds,vcoreSeconds
application_1647939308243_3220,hadoop,HIVE-9728c683-c5aa-4e7d-8e9d-d251807b06f5,etl,TEZ,2022-04-01 02:34:22,2022-04-01 02:36:02,1.6527333333333334,19457970,2570
application_1647939308243_3219,hadoop,HIVE-3695dadc-b10a-4433-b4e4-3d246ea14ebe,etl,TEZ,2022-04-01 02:31:02,2022-04-01 02:32:20,1.3011666666666666,18771297,2475
application_1647939308243_3222,hadoop,HIVE-9ac85f24-bf5d-48e1-b617-19ee472a7108,etl,TEZ,2022-04-01 02:37:24,2022-04-01 02:38:54,1.4964666666666666,27741696,3651
application_1647939308243_3221,hadoop,run_sql_args.py,etl,SPARK,2022-04-01 02:36:12,2022-04-01 02:39:06,2.9078666666666666,3672268,2172
application_1647939308243_3224,hadoop,run_sql_args.py,etl,SPARK,2022-04-01 02:41:09,2022-04-01 02:44:28,3.3162333333333334,4420826,2622




