# YARN Log Analysis

## CloudFormation template for deploying QuickSight resources

This template file provides an assessment solution for analyzing YARN logs through AWS QuickSight dashboards. All necessary cloud resources are modeled and deployed through this template file.

## Solution Architecture

- Data Lake: Collect and save YARN application logs
- Visualization: Display analyzed TCO metrics

![image](/yarn-log-analysis/quicksight/cfn-target/docs/asset/quicksight_dashboard_replication_architecture.jpg)

## **Prerequisites**

1.  Upload your yarn logs file(cluster_yarn_log.csv) result from [yarn-log-collector](https://gitlab.aws.dev/proserve-kr-dna/hadoop-migration-assessment/-/tree/main/yarn-log-collector) to a specific path(e.g., `s3://DOC-EXAMPLE-BUCKET/yarn-log/2022-01/`) on S3 bucket.

2.  Create a manifest(e.g., `yarn-log-manifest.json`) file about log files, and upload the manifest file to S3(e.g., `s3://DOC-EXAMPLE-BUCKET/yarn-log/manifest`).

    ```json
    {
      "fileLocations": [
        {
          "URIPrefixes": ["s3://DOC-EXAMPLE-BUCKET/yarn-log/2021-12/"]
        }
      ],
      "globalUploadSettings": {
        "format": "CSV",
        "delimiter": ",",
        "textqualifier": "'",
        "containsHeader": "true"
      }
    }
    ```

3.  Create an administrator user on QuickSight management console.
4.  To have QuickSight account with access to S3 bucket in which logs data located

   <img src="/yarn-log-analysis/quicksight/cfn-target/docs/asset/QuickSight-S3-permission.png" width="800"/>

## **Deploy using AWS CloudFormation template from the AWS Management Console**

1. Open the [AWS CloudFormation](https://console.aws.amazon.com/cloudformation) link in a new tab and log in to your AWS account.
2. Click on Create stack(With new resources if you have clicked in the top right corner).
3. In **Prepare template**, choose **Template is ready**.
4. In **Template source**, choose **Upload a template file**.
5. Click on **Choose file** button and navigate to this template directory.
6. Select this CloudFormation template file.

   <img src="/yarn-log-analysis/quicksight/cfn-target/docs/asset/create_stack.png" width="800"/>

7. Click **Next**.
8. Provide a **Stack name**, for example **cfn-quicksight**.

   <img src="/yarn-log-analysis/quicksight/cfn-target/docs/asset/specify_stack_details.png" width="800"/>

9. You can leave **Configurate stack options** default, click **Next**.

10. On the **Review** the stack page, scroll down to the bottom and click on **Create stack**.

    <img src="/yarn-log-analysis/quicksight/cfn-target/docs/asset/Review_stack.png" width="800"/>

11. You can click the **refresh** button a few times until you see in the status **CREATE_COMPLETE**.
    This step will create QuickSight dataset and dashboard in your account, and you can check the deployment results as shown in the following picture.
    To check the dataset and dashboard, move on to QuickSight.

    <img src="/yarn-log-analysis/quicksight/cfn-target/docs/asset/quicksight_first.png" height="400"/><img src="/yarn-log-analysis/quicksight/cfn-target/docs/asset/quicksight_dashboard.png" height="400" />

---

### **Destroy stack**

Follow these steps to destroy created resources:

1. In the [CloudFormation console](https://console.aws.amazon.com/cloudformation), select the stack you have created.
2. In the top right corner, click on **Delete**.
3. In the pop-up window click on **Delete stack**.
4. You can click the **refresh** button a few times until you see in the status **DELETE_COMPLETE**.
