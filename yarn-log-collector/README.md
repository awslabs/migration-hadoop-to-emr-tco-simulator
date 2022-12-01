# yarn-log-collector
- Obtain a collection of the yarn Application Objects by HTTP request
- https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/ResourceManagerRest.html#Cluster_Applications_API
- Responded object
  - ["id", "user", "name", "queue", "state", "finalStatus", "progress", "trackingUI", "trackingUrl", "diagnostics", "clusterId", "applicationType", "applicationTags", "priority", "startedTime", "finishedTime", "elapsedTime", "amContainerLogs", "amHostHttpAddress", "allocatedMB", "allocatedVCores", "runningContainers", "memorySeconds", "vcoreSeconds", "queueUsagePercentage", "clusterUsagePercentage", "preemptedResourceMB", "preemptedResourceVCores", "numNonAMContainerPreempted", "numAMContainerPreempted", "logAggregationStatus", "unmanagedApplication", "appNodeLabelExpression", "amNodeLabelExpression", "resourceRequests"]


## Check list before running
- [ ] Client machine that running this application can access yarn resource manager (HTTP : 8088 or HTTPS: 8090)
- [ ] Timeline server(yarn historyserver) must be enabled(Support only Timeline Server v1).
- [ ] Check Resource manager retention period to define collecting inverval

## Usage
#### Parameters
- -m: mode [1] HTTPS with Kerberos Case [2] HTTPS Case [3] HTTP Case ex) -m 3
- -u: yarn resource manager url (http or https) ex) https://xx.xx.xx.xx:8090, http://xx..xx.xx:8088

- Run example 
```
sh start-collector.sh -m 3 -u http://10.10.160.64:8088
Start yarn logs collecting from curl.
HTTP Secure-Mode: 3
YARN-RM URL: http://10.10.160.64:8088
Yarn Cluter API target: http://10.10.160.64:8088/ws/v1/cluster/apps
HTTP Case
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 18.0M    0 18.0M    0     0  22.0M      0 --:--:-- --:--:-- --:--:-- 22.0M
Collecting yarn logs completed.
```
Result file(collected yarn logs) generated in output running directory.


> **For more accurate workload analysis, at least 7 days of data are recommended.**
Most of cluster have default yarn.resourcemanager.max-completed-applications value(hadoop2: 10,000 or hadoop3: 1,000) and running more than thousands of application a day, thus it should be collected periodically for analyzing more than 7 days. 
Set up a cron job by checking the log retention period so that no logs are dropped within the range you want to collect.
- Example 
  - Situation
    There's a hadoop 2 cluster running on on-premises with yarn.resourcemanager.max-completed-applications value is 10,000. 
    In this cluster, 30,000 jobs are executed per day.
  - Cron
    Set Cron service like this
    ```
    00 */4 * * * /home/hadoop/start-collector.sh -m 3 -u http://10.10.160.64:8088
    ```
  - Description
    Since the production cluster is busy at specific times such as batch jobs, it is recommended to set enough margin for the execution cycle.  Therefore, though 30,000 jobs are executed a day, but the log is collected every 4 hours. After collecting logs with duplicates, it's going to be removed with orgarnizer application.

- Result sample:

```{
  "apps":
  {
    "app":
    [
      {
        "id": "application_1476912658570_0002",
        "user": "user2",
        "name": "word count",
        "queue": "default",
        "state": "FINISHED",
        "finalStatus": "SUCCEEDED",
        "progress": 100,
        "trackingUI": "History",
        "trackingUrl": "http://host.domain.com:8088/cluster/app/application_1476912658570_0002",
        "diagnostics": "...",
        "clusterId": 1476912658570,
        "applicationType": "MAPREDUCE",
        "applicationTags": "",
        "priority": -1,
        "startedTime": 1476913457320,
        "finishedTime": 1476913761898,
        "elapsedTime": 304578,
        "amContainerLogs": "http://host.domain.com:8042/node/containerlogs/container_1476912658570_0002_02_000001/user2",
        "amHostHttpAddress": "host.domain.com:8042",
        "allocatedMB": 0,
        "allocatedVCores": 0,
        "runningContainers": 0,
        "memorySeconds": 206464,
        "vcoreSeconds": 201,
        "queueUsagePercentage": 0,
        "clusterUsagePercentage": 0,
        "preemptedResourceMB": 0,
        "preemptedResourceVCores": 0,
        "numNonAMContainerPreempted": 0,
        "numAMContainerPreempted": 0,
        "logAggregationStatus": "DISABLED",
        "unmanagedApplication": false,
        "appNodeLabelExpression": "",
        "amNodeLabelExpression": "",
        "resourceRequests": [
        {
            "capability": {
                "memory": 4096,
                "virtualCores": 1
            },
            "nodeLabelExpression": "",
            "numContainers": 0,
            "priority": {
                "priority": 0
            },
            "relaxLocality": true,
            "resourceName": "*"
        },
        {
            "capability": {
                "memory": 4096,
                "virtualCores": 1
            },
            "nodeLabelExpression": "",
            "numContainers": 0,
            "priority": {
                "priority": 20
            },
            "relaxLocality": true,
            "resourceName": "host1.domain.com"
        },
        {
            "capability": {
                "memory": 4096,
                "virtualCores": 1
            },
            "nodeLabelExpression": "",
            "numContainers": 0,
            "priority": {
                "priority": 20
            },
            "relaxLocality": true,
            "resourceName": "host2.domain.com"
        }]
      },
      {
        "id": "application_1476912658570_0001",
        "user": "user1",
        "name": "Sleep job",
        "queue": "default",
        "state": "FINISHED",
        "finalStatus": "SUCCEEDED",
        "progress": 100,
        "trackingUI": "History",
        "trackingUrl": "http://host.domain.com:8088/cluster/app/application_1476912658570_0001",
        "diagnostics": "...",
        "clusterId": 1476912658570,
        "applicationType": "YARN",
        "applicationTags": "",
        "priority": -1,
        "startedTime": 1476913464750,
        "finishedTime": 1476913863175,
        "elapsedTime": 398425,
        "amContainerLogs": "http://host.domain.com:8042/node/containerlogs/container_1476912658570_0001_02_000001/user1",
        "amHostHttpAddress": "host.domain.com:8042",
        "allocatedMB": 0,
        "allocatedVCores": 0,
        "runningContainers": 0,
        "memorySeconds": 205410,
        "vcoreSeconds": 200,
        "queueUsagePercentage": 0,
        "clusterUsagePercentage": 0,
        "preemptedResourceMB": 0,
        "preemptedResourceVCores": 0,
        "numNonAMContainerPreempted": 0,
        "numAMContainerPreempted": 0,
        "logAggregationStatus": "DISABLED",
        "unmanagedApplication": false,
        "appNodeLabelExpression": "",
        "amNodeLabelExpression": "",
        "resourceRequests": [
        {
            "capability": {
                "memory": 4096,
                "virtualCores": 1
            },
            "nodeLabelExpression": "",
            "numContainers": 0,
            "priority": {
                "priority": 0
            },
            "relaxLocality": true,
            "resourceName": "*"
        },
        {
            "capability": {
                "memory": 4096,
                "virtualCores": 1
            },
            "nodeLabelExpression": "",
            "numContainers": 0,
            "priority": {
                "priority": 20
            },
            "relaxLocality": true,
            "resourceName": "host3.domain.com"
        },
        {
            "capability": {
                "memory": 4096,
                "virtualCores": 1
            },
            "nodeLabelExpression": "",
            "numContainers": 0,
            "priority": {
                "priority": 20
            },
            "relaxLocality": true,
            "resourceName": "host4.domain.com"
        }]
      }
    ]
  }
}
```
