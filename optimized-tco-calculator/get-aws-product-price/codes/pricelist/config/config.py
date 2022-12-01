import datetime as dt
import math
import os

from numpy import NaN

default_file_path_name = {
    "Result" : "/data/price-data/",
    "Temp" :"/data/price-data/temp"
}

offer_region_index_file = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{service}/current/{region}/index.csv"
offer_index_file = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{service}/current/index.csv"


csv_file_info = {
    "file_name": "{0}_{1:04d}{2:02d}{3:02d}.csv"
}

service_code_name = {
    "S3":["AmazonS3","Amazon Simple Storage Service"],
    "S3Glacier":["AmazonS3GlacierDeepArchive","Amazon S3 Glacier Deep Archive"],
    "EMR":["ElasticMapReduce","Amazon Elastic MapReduce"],
    "EC2":["AmazonEC2","Amazon Elastic Compute Cloud"]
}

	
s3_conditions = {
    "Volume Type":["Standard","Standard - Infrequent Access","Amazon Glacier"],
    "Storage Class":["General Purpose","Infrequent Access","Archive"],
    "Unit":"GB-Mo"
}
	
s3_req_conditions = {
    "Group":["S3-API-GDA-Tier2", "S3-API-GLACIER-Tier1", "S3-API-GLACIER-Tier2", "S3-API-SIA-Tier1", "S3-API-SIA-Tier2", "S3-API-Tier1", "S3-API-Tier2"]
}

s3_glacier_conditions = {
    "Volume Type":["Glacier Deep Archive"],
    "Storage Class":["Archive"],
    "Unit":"GB-Mo",
    "EndingRange":math.inf
}
s3_req_glacier_conditions = {
    "operation":"PutObject"
}
	
ebs_conditions = {
    "Product Family":"Storage",
    "Unit":"GB-Mo",
    "Volume API Name":["gp3","st1"],
    "Storage Media":["SSD-backed","HDD-backed"],
    "Volume Type":["General Purpose","Throughput Optimized HDD"]
}

ec2_conditions = {
    'EndingRange':math.inf,
    'Unit':'Hrs',
    #'TermType':['Reserved','OnDemand'],
    #'LeaseContractLength':['','3 yr','3yr','1 yr','1yr'],
    #'PurchaseOption':['','No Upfront'],
    #'OfferingClass':['','standard'],
    #'Product Family':'Compute Instance',
    'Current Generation':'Yes',
    #'Instance Family':['Memory optimized','General purpose','Compute Optimized'],
    #'Storage':'EBS only',
    'Tenancy':'Shared',
    'Operating System':'Linux',
    'CapacityStatus':'Used',
    #'ClassicNetworkingSupport':False,
    #'ECU':'Na',
    'Pre Installed S/W':'Na'
}

emr_conditions_json = {
    "softwareType":"EMR",
    "unit":"Hrs",
    "endRange":"Inf",
    "Instance Family":["Memory optimized","General purpose",'Compute Optimized']
}

emr_conditions = {
    "Software Type":"EMR",
    "Instance Family":["Memory optimized","General purpose"]
}

def get_default_file_path(type:str):
    path = os.path.dirname(os.path.abspath(__file__))
    path_list = path.split('/')
    del path_list[-4:]
    output_path = '/'.join(path_list)
    
    if type == 'RESULT':
        return output_path + default_file_path_name['Result']
    elif type == 'TEMP': 
        return output_path + default_file_path_name['Temp']
    else:
        return None
    
    
def get_offer_index_file():
    return offer_index_file

def get_offer_region_index_file():
    return offer_region_index_file

def get_csv_file_name(service_name:str):
    now = dt.datetime.now()
    return  csv_file_info['file_name'].format(
                            service_name,
                            now.year,
                            now.month,
                            now.day)


def get_service_code(service:str):
    if service in service_code_name:
        return None
    else:
        return service_code_name[service][0]

def get_service_name(service:str):
    if service in service_code_name:
        return None
    else:
        return service_code_name[service][1]


def get_s3_conditions():
    return s3_conditions

def get_s3_glacier_conditions():
    return s3_glacier_conditions


def get_s3_req_conditions():
    return s3_req_conditions

def get_s3_req_glacier_conditions():
    return s3_req_glacier_conditions


def get_ec2_conditions():
    return ec2_conditions

def get_emr_conditions():
    return emr_conditions

def get_ebs_conditions():
    return ebs_conditions

