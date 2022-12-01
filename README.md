# Hadoop Migration Assessment (TCO-Simulator)
This repository constains a set of hadoop migrate to Amazon EMR TCO estimator.

This tool will be part of the [**EMR Delivery Excellence program**](https://wiki.doleancloud.com/confluence/display/HMDK/Hadoop+to+EMR+Migration+Delivery+Kit) with the kit as the core asset

## Table of Contents  
   1. [Project Background](#Project-Background)
   2. [Tool capability](#Tool-capability)
   1. [About this Repo](#About-this-Repo)
   2. [yarn-log-collector](#yarn-log-collector)
   3. [yarn-log-analysis](#yarn-log-analysis)
   4. [optimized-tco-calculator](#optimized-tco-calculator)

## <a name="Project-Background"></a>Project Background
When you migrate on-premise hadoop cluster to Amazon EMR, you would start long journey to get optimized EMR. There are some ways to migrate AWS, Lift & Shift, Hybrid and Re-architect. Re-architecting your platform is inevitable to get maximized the benefits of the cloud.   
![image](/imgs/tco_comparison.png)

A re-architecture approach to migration includes the following benefits for your applications(from [AWS EMR migration guide](https://d1.awsstatic.com/whitepapers/amazon_emr_migration_guide.pdf)): 
- Independent scaling of components due to separated storage and compute resources.
- Increased productivity and lowered costs by leveraging the latest features and software.
- Ability to prototype and experiment quickly due to provisioning resources quickly. 
- Options to scale system vertically (by requesting more powerful hardware) and horizontally (by requesting more hardware units). 
- Lowered operational burden by no longer managing many aspects of cluster lifecycle, including replacing failed nodes, upgrades, patching, etc. Since clusters can be treated as transient resources, they can be decommissioned and restarted. 
- Data accessibility when using a data lake architecture, data is stored on a central storage system that can be used by a wide variety of services and tools to ingest and process the data for different use cases. For example, using services such as AWS Glue, and Amazon Athena and other services can greatly reduce operational burden and reduce costs, and can only be leveraged if data is stored on S3. 
- Ability to treat compute instances as transient resources, and only use as much as you need, when you actively need it.   


In spite of many advantage, re-architecting requires much effort and time to analyze the current workloads and assign the workloads to different clusters based on usage patterns. Therefore, Korea ProServe team creates this tool to reduce time and effort for re-architect approach. I wish it helps your migration journey to AWS EMR. 


## <a name="Tool-capability"></a>Tool capability
   1. It extracts the *application history* information using *resource manager application API*
   2. It generates the *application workload usage* (Application usage statistics) in *CSV* using a python or docker container based program generating into the local file system.
   3. It analyzes customer’s Hadoop application logs to design the EMR clusters with AWS QuickSight and then make the cluster design info excel file based on template.
   4. It calculates the *optimized TCO estimation for EMR based on hourly aggregated log files* in Macro-enabled Excel format.



## <a name="About-this-Repo"></a>About this Repo
The repo is subdivided into sections for each step to get Amazon EMR TCO(Total Cost of Ownership). 
   - hadoop yarn logs collector applications. 
   - hadoop yarn logs analysis with QuickSight. 
   - Amazon EMR TCO(Total Cost of Ownership) that you designed. 

## <a name="yarn-log-collector"></a>1. yarn-log-collector
 - Extract the application history information using resource manager application API
 - Customer can easily extract logs using provided python application or containered python apps in customer computer which can connect hadoop master node 
 - [Run instruction](https://gitlab.aws.dev/hadoop-migration/hadoop-migration-factory/hadoop-migration-assessment-tco/-/tree/main/yarn-log-collector)

## <a name="yarn-log-analysis"></a>2. yarn-log-analysis
![image](/imgs/quicksight_dashboard.png)  

 - Analize customer's hadoop application logs to design the emr custers with AWS QuickSight  
 - [Dashboard Generation] Create QuickSight dashboard automatcially in target aws account with Cloud Formation Template
 - [Deign Clusters] Design EMR clusters according analyis result and and make a clustered design info file using provided excel template manually
 - [Run instruction](https://gitlab.aws.dev/hadoop-migration/hadoop-migration-factory/hadoop-migration-assessment-tco/-/tree/main/yarn-log-analysis/quicksight/cfn-target)
 - [How to anayze the quicksight Dashboard : example guide](https://gitlab.aws.dev/hadoop-migration/hadoop-migration-factory/hadoop-migration-assessment-tco//-/wikis/How-to-analyze-yarn-applications-logs-from-Quicksight-dashbords-(ENG))

## <a name="optimized-tco-calculator"></a>3. optimized-tco-calculator
 - Calculate the optimized TCO for EMR.  
 - [Preperation] Make a houlry aggregated logs file for TCO calculation according to emr cluster design info using provided python app.   
 - [TCO calculation] Calculate and simulate optimzed TCO using provided Excel template    
![image](/imgs/tco_simulation.png)  
 - [Run instruction](https://gitlab.aws.dev/hadoop-migration/hadoop-migration-factory/hadoop-migration-assessment-tco/-/tree/main/optimized-tco-calculator)

## Getting Help
Requests issues for questions, bugs, and feature requests.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.