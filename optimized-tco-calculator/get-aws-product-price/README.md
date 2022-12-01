## Get list - AWS Product price
This python program provides CSV file that lists price of AWS services(S3 and EMR) to TCO calculator.

## Usage
> #### Dependencies
> - Pandas
> - Boto3
> - Numpy
> - XlsxWriter
> - Tables
> - Requests

- Run command
  ```
  $ price_list.py --region-code <AWS Region code> --output-path <output path>
  ```
- Parameters
  - `--region-code`(Optional): AWS Region code. You can find the region code on the [AWS EC2 document page](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-regions). Default value is None, it generate all regions price.
  - `--output-path`(Optional): Output path you want to your path.(Default path: hadoop-migration-assessment/optimized-tco-calculator/data/price-data/)

- Example:
  To run and generate latest price data into default path
  ```
  python3 price_list.py --region-code ap-northeast-2 
  Downloading... The price list offer file for ElasticMapReduce.
  File : /Users/test/hadoop-migration-assessment/optimized-tco-calculator/data/price-data/temp/ElasticMapReduce_ap-northeast-2_20220304.csv
  Done : /Users/test/hadoop-migration-assessment/optimized-tco-calculator/data/price-data/temp/ElasticMapReduce_ap-northeast-2_20220304.csv
  Downloading... The price list offer file for AmazonEC2.
  File : /Users/test/hadoop-migration-assessment/optimized-tco-calculator/data/price-data/temp/AmazonEC2_ap-northeast-2_20220304.csv
  Done : /Users/test/hadoop-migration-assessment/optimized-tco-calculator/data/price-data/temp/AmazonEC2_ap-northeast-2_20220304.csv
  Downloading... The price list offer file for AmazonS3.
  File : /Users/test/hadoop-migration-assessment/optimized-tco-calculator/data/price-data/temp/AmazonS3_ap-northeast-2_20220304.csv
  Done : /Users/test/hadoop-migration-assessment/optimized-tco-calculator/data/price-data/temp/AmazonS3_ap-northeast-2_20220304.csv
  Downloading... The price list offer file for AmazonS3GlacierDeepArchive.
  File : /Users/test/hadoop-migration-assessment/optimized-tco-calculator/data/price-data/temp/AmazonS3GlacierDeepArchive_ap-northeast-2_20220304.csv
  Done : /Users/test/hadoop-migration-assessment/optimized-tco-calculator/data/price-data/temp/AmazonS3GlacierDeepArchive_ap-northeast-2_20220304.csv
  [Done] The filename of the price list is '/Users/test/hadoop-migration-assessment/optimized-tco-calculator/data/price-data/emr_s3_pricing_table-2022-03-04.xlsx'
  ```

## How it works

### 1. Get price lists
This program requests the URL to get the AWS price list through the [AWS Price List Bulk APIs](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-ppslong.html). It uses Requests library to download price CSV file in temp directory. If you run the program, it deletes each service's price files more than 2 days from your temp directory(hadoop-migration-assessment/optimized-tco-calculator/data/price-data/temp).

URLs for the price list
  - EMR(https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/ElasticMapReduce/current/index.csv)
  - EC2(https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.csv)
  - S3(https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/index.csv)(
  - S3 Glacier Deep Archive(https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3GlacierDeepArchive/current/index.csv)
  - EC2 Spot Instances   
    AWS Price List API currently does not support for Amazon EC2 Spot Instances.
    As a workaround, it uses the [describe_spot_price_history() method](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_spot_price_history) to get the price of spot instance.


### 2. Filtering
Apply conditions to the price list datasets(CSV files) to extract the sub-datasets required for TCO calculator.

- EMR and EC2
  - Instance name
  - vCPU	
  - Memory
  - On-Demand hourly rate
  - 3 year RI hourly rate
  - 1 year RI hourly rate
  - SPOT hourly rate
  - EMR Service hourly rate
  
- S3 price
  - Standard (First 50TB/Month)
  - Standard (Next 450TB/Month)
  - Standard (Over 500TB/Month)
  - Standard-IA
  - S3 Glacier
  - S3 Glacier Deep Archive
  - PUT, COPY, POST, LIST requests
  - GET, SELECT, and all other requests
  - EBS - HDD(ST1)
  - EBS - SSD(GP3)
  
 

### 3. Generate the result excel file
Result file(`emr_s3_pricing_table-yyyy-MM-dd.xlsx`) is created by merging from sub-datasets. Result file is being stored in the default location which is in a `price-data` folder under `hadoop-migration-assessment/optimized-tco-calculator/data/` or you specified by `--output-path`.
  - Example of EMR(EC2) price   
  
    ![image](/optimized-tco-calculator/get-aws-product-price/imgs/price_emr.png)


  - Example of S3 price    
    ![image](/optimized-tco-calculator/get-aws-product-price/imgs/price_s3.png)




