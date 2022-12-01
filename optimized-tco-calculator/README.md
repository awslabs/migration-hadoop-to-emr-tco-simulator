# optimized-emr-calculator
- Help calculate and simulate optimized TCO of post-migration EMR from on-premise hadoop 


## How to get TCO result
#### 1. Open [emr-cluster-design-input-test.xlsx](data/cluster-design/emr-cluster-design-input-test.xlsx) file and write EMR design information as you designed result from QuickSight analysis.
###### emr cluster design input file instruction.   
- [**clusterOrder, clusterName**] columns are used for indentify clusters.
- [**clusterType**] cluster types used by EMR: Persistent clusters as 'P' or transient clusters as 'T'.  
- [**queue, user, appType, startHour, endHour**] columns are filtering options from collected yarn logs. **Blank cell means 'ALL'**   
    - **queue**: Choose yarn queues want to include this cluster jobs.(If you left cell as blank, all queues are selected)
    - **user**: Choose user want to include this cluster jobs.(If you left cell as blank, all users are selected)
    - **appType**: Choose application types want to include this cluster jobs.(If you left cell as blank, all application types are selected)
        - Example: _SPARK, TEZ, MAPREDUCE_, etc.(case-insensitive)
    - **startHour, endHour**: Choose jobs hour range. **_startedTime_** value in yarn logs is criteria. 
        - Support only integer(Invalid: 0.5, 2.15)  	
        - **startHour, endHour** are **not required for persistent cluster type**.   
- Example
	| clusterOrder | clusterType | clusterName | queue | user | appType | startHour | endHour |
	| ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
	| 1 | P | DW1 | ad-hoc | user1, user2, user3 |  |  |  |
	| 2 |	T |	BATCH1 | etl | hadoop | spark | 0 | 4 |
	| 3 | T | BATCH2 | etl | hadoop | tez | 1 | 3 | 


#### 2. Aggregate yarn logs into hourly by running tco-input-generator.py
##### Setup your environment
Required:
- linux does not support.
- python 3(Tested on 3.7)
- Install dependencies
  > Required packages: 
  >   - pandas
  >   - openpyxl   
  - Using pip with requirements.txt
    > **pip needs to be installed.**
    ```
    pip3 install -r requirements.txt 
    ```
  - Using setup.py
    > **setuptools(python module) to be installed**
    ```
    python3 setup.py install --user
    ```

- Run command   
  Move to _1.hourly-agg-logs-generator_ directory and run below command
    ```
    $ hourly-agg-log-generator.py -c <customer name> -l <yarn input logs> -d <emr cluster design input file>
    ```
- Parameters
    - `-c`: customer name(optional)
    - `-l`: logs of customer yarn application collected by yarn-log-collector.py (CSV file)
    - `-d`: [design infomration of emr cluster](#1.-Open-emr-cluster-design-input-test.xlsx-file-and-write-EMR-design-information-as-you-designed-result-from-QuickSight-analysis.) after analysis of customer's yarn app logs (Excel File)

- Example: 
    ```
    $ python code/hourly-agg-log-generator.py -l ../data/yarn-app-logs/cluster_yarn_log.csv -d ../data/cluster-design/emr-cluster-design-input-test.xlsx -c test
    starting hourly agg. - Persistent type
    EMR Cluster Name - DW1
    starting hourly agg. - Transient type
    EMR Cluster Name - BATCH2
    EMR Cluster Name - BATCH1

    Success..... /hadoop-migration-assessment/optimized-tco-calculator/data/hourly-aggregated-app-logs/test-hourly-aggregated-app-logs-tco-input-2022-03-04.xlsx
    ```

- Result   
    <img src="/uploads/a6e3bdb25137bfb8570f4b5a0a1dd985/image.png" height="420"/>


#### 3. Open excel template file 
> **NOTICE**   
> REQUIREMENTS: Hourly aggregated Logs file that created from tco-input-generator.py
1. Open [excel template file](https://gitlab.aws.dev/proserve-kr-dna/hadoop-migration-assessment/-/blob/main/optimized-tco-calculator/excel-tco-calculators(excel)/optimzed-emr-tco-calculator-template-v1.1.xlsm) with macro enabled.  
    <img src="/uploads/9203bdff562b45684020542b671ef63d/image.png" height="150"/>

2. Enter your values to green cells    
   - Customer Hadoop Cluster Information (Ask customer about on-premise cluster infomration : HDFS size, Data Nose Spec(mem, vcore))

     Enter customer hadoop information HDFS size(TB) and cluster Hardware spec. (This is example way  how customer can get their cluster infomration)
     - HDFS size(TB): Enter original data size(Do NOT include storage overhead size(copy data or erasure coding data)    
       - Use `hdfs dfs -df -h` command    
         <img src="/uploads/13bb9b8705415993548710163f2f38d8/image.png" width="700"/>    
         (This sample cluster has 200% storage overhead. Thus it should be divided by 3)
       
       - Access HDFS Name Node UI    
         <img src="/uploads/ecb753ea7ce0624da4f31959412c9c72/image.png" width="700"/>    
         (This sample cluster has 200% storage overhead. Thus it should be divided by 3)
         
     - Hardware specification: Get namenodes and datanodes hardware information and enter the average of all namenodes and datanodes.
       > If your Name node and Data node have different specification, enter average value.   
       > Example: 3 Name nodes with 32 cores and 256GB memory, 10 Data nodes with 16 cores and 128GB memory.
       > <img src="/uploads/e949a581438677fc58da3d461866a105/image.png" height="70"/>    
   - Load Input Data   
     - Click and select hourly aggregated logs as you [created above](#2.-Aggregate-yarn-logs-into-hourly-by-running-tco-input-generator.py)
       ![image](/uploads/b00acb7b3ab9c84a5cce768ac950856f/image.png)   
     - (Optional)Get up-to-date EMR and S3 price list([Detail instruction](https://gitlab.aws.dev/proserve-kr-dna/hadoop-migration-assessment/-/tree/main/optimized-tco-calculator/get-aws-product-price))   
       **Default price table already loaded** in optimzed-emr-tco-calculator-test.xlsm    
       If you want to renew price data follow this and load new price table file.    
       `$ python3 price_list.py --region-code ap-northeast-2`   
   - EMR TCO Simulation Variables          
     **Set the variables**: _Region, EC2 Types, Disk Size(GB), EMR High Availabilty, Hive to Spark Conv. Effect, EC2 and EBS Discount(EDP), S3 Volume Discount, Local Currency Rate_ and **_EMR EC2 Task/Core Pricing Ratio and Price / Hour_**
      - EC2 Type : Consider R type for spark, Consider M type for Hive, MAPREDUCE
      - EC2 Size : Consider similiar size of on-premise node spec first, and change the instance size smaller or larger until TCO will be reduced to minimum
      - Hive to Spark Conv Effect : Use just in case customer want to migrate hive to spark (if there are mixed spark, hive workloads, the value should be 0%)
      - EMR HA : Yes -> 3 name nodes will be counted in TCO simulation. If no, 1 name node ...
      - EC2, EBS Discount(EDP), S3 Volume Discount: Get discount number(%) from Account Manager or who has a ownership in EDP prgroam
      - Local currency rate : Set the exchange rate of a currency according to your region( Set 1 --> USD)
     > NOTICE: 
     > Below the **Check cell value must have 100%**.    
     > <img src="/uploads/c8332ab85c1070a40e2d98146c10ce6c/image.png" height="200"/>

3. TCO simulation results
   Optimzed TCO (EC2, Storage) will be automatically calculated including lift-and-shift mirgation cost(EC2)
   Daily required Nodes/hour graph also automatically displayed.
   ![image](/uploads/b717fe92052b49de1170748f7ffa72e7/image.png)
