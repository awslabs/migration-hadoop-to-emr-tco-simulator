import pandas as pd
import numpy as np
import math
import pricelist.config.config as conf
from pricelist.product_price_bulk import ProductPriceBulk
from pricelist.common.price_parameter import PriceParameter


class S3Price():
    SERVICE_CODE_VALUE = 'AmazonS3'


    def __init__(self, price_params:PriceParameter):
        self.price_params = price_params
        self.region_code = price_params.get('regionCode')


    def get_price_list(self):
        
        # get S3 price list
        conditions = conf.get_s3_conditions()
        s3_bulk = ProductPriceBulk(self.SERVICE_CODE_VALUE, self.price_params)
        cols = ['Region Code','Location','serviceCode','Volume Type','PricePerUnit','Storage Class','Unit','EndingRange']
        
        s3_df = s3_bulk.get_price_df(conditions, cols, file_name=None, region_code=self.region_code)

        
        # filtering : S3 Standard
        s3_standard_df = s3_df.loc[ (s3_df['Volume Type'] == 'Standard') & 
                                    (s3_df['Storage Class'] == 'General Purpose' ) &
                                    (s3_df['Unit'] == 'GB-Mo') &
                                    (s3_df['Region Code'].str.match('[a-z]+-[a-z]+-[1-9]+$')) ]

        s3_standard_merge_df = s3_standard_df.loc[ (s3_standard_df['EndingRange']==51200) & 
                                                   (s3_standard_df['Volume Type']=='Standard') ]
        
        s3_standard_merge_df.rename(columns={'PricePerUnit':'First 50TB/Month'}, inplace=True)
        
        s3_standard_merge_df = pd.merge(left=s3_standard_merge_df,
                                        right=s3_standard_df.loc[ s3_standard_df['EndingRange'] == 512000 ][['Location','PricePerUnit']], 
                                        how='left', 
                                        on='Location')
        
        s3_standard_merge_df.rename(columns={'PricePerUnit':'Next 450TB/Month'}, inplace=True)
        
        s3_standard_merge_df = pd.merge(left=s3_standard_merge_df,
                                        right=s3_standard_df.loc[ s3_standard_df['EndingRange'] == math.inf ][['Location','PricePerUnit']], 
                                        how='left', 
                                        on='Location')
        
        s3_standard_merge_df.rename(columns={'PricePerUnit':'Over 500TB/Month'}, inplace=True)
        
        
        # filtering : S3 Standard - Infrequent Access
        s3_ia_df = s3_df.loc[ (s3_df['Volume Type'] == 'Standard - Infrequent Access') & 
                              (s3_df['Storage Class'] == 'Infrequent Access' ) &
                              (s3_df['Unit'] == 'GB-Mo') & 
                              (s3_df['EndingRange'] ==  math.inf) ]

        s3_ia_df.rename(columns={'PricePerUnit':'First 50TB/Month'}, inplace=True)
        s3_ia_df['Next 450TB/Month'] = s3_ia_df.loc[ s3_ia_df['EndingRange'] == math.inf ]['First 50TB/Month']
        s3_ia_df['Over 500TB/Month'] = s3_ia_df.loc[ s3_ia_df['EndingRange'] == math.inf ]['First 50TB/Month']
        
        
        # filtering : S3 Glacier
        s3_glacier_df = s3_df.loc[ (s3_df['Volume Type'] == 'Amazon Glacier') & 
                                   (s3_df['Storage Class'] == 'Archive' ) &
                                   (s3_df['Unit'] == 'GB-Mo') & 
                                   (s3_df['EndingRange'] == math.inf) ]
        
        s3_glacier_df.rename(columns={'PricePerUnit':'First 50TB/Month'}, inplace=True)
        s3_glacier_df['Next 450TB/Month'] = s3_glacier_df.loc[ s3_glacier_df['EndingRange'] == math.inf ]['First 50TB/Month']
        s3_glacier_df['Over 500TB/Month'] = s3_glacier_df.loc[ s3_glacier_df['EndingRange'] == math.inf ]['First 50TB/Month']
        
        
        # get S3 Request (Put/Get) price
        conditions = conf.get_s3_req_conditions()
        cols = ['Location','Group','operation','PricePerUnit']
        s3_req_df = s3_bulk.get_price_df(filters=conditions, 
                                         cols=cols, 
                                         file_name=s3_bulk.get_file_name(self.SERVICE_CODE_VALUE,region_code=self.region_code), 
                                         region_code=self.region_code)
        s3_req_df['PricePerUnit'] = s3_req_df['PricePerUnit'] * 1000
        
        
        # merge usage price and request price
        s3_standard_merge_df = pd.merge(left=s3_standard_merge_df,
                                        right=s3_req_df.loc[ s3_req_df['Group'] == 'S3-API-Tier1' ][['Location','PricePerUnit']],
                                        how='left', on='Location')
        s3_standard_merge_df.rename(columns={'PricePerUnit':'PUT, COPY, POST, LIST requests (per 1,000 requests)'}, inplace=True)
        
        s3_standard_merge_df = pd.merge(left=s3_standard_merge_df,
                                        right=s3_req_df.loc[ s3_req_df['Group'] == 'S3-API-Tier2' ][['Location','PricePerUnit']],
                                        how='left', on='Location')
        s3_standard_merge_df.rename(columns={'PricePerUnit':'GET, SELECT, and all other requests (per 1,000 requests)'}, inplace=True)
        
        
        s3_ia_df = pd.merge(left=s3_ia_df, 
                            right=s3_req_df.loc[ s3_req_df['Group'] == 'S3-API-SIA-Tier1' ][['Location','PricePerUnit']],
                            how='left', on='Location')
        s3_ia_df.rename(columns={'PricePerUnit':'PUT, COPY, POST, LIST requests (per 1,000 requests)'}, inplace=True)
        
        s3_ia_df = pd.merge(left=s3_ia_df, 
                            right=s3_req_df.loc[ s3_req_df['Group'] == 'S3-API-SIA-Tier2' ][['Location','PricePerUnit']],
                            how='left', on='Location')
        s3_ia_df.rename(columns={'PricePerUnit':'GET, SELECT, and all other requests (per 1,000 requests)'}, inplace=True)
        
        
        s3_glacier_df = pd.merge(left=s3_glacier_df, 
                                 right=s3_req_df.loc[ (s3_req_df['Group'] == 'S3-API-GLACIER-Tier1') & (s3_req_df['operation'] == 'PutObject') ][['Location','PricePerUnit']],
                                 how='left', on='Location')
        s3_glacier_df.rename(columns={'PricePerUnit':'PUT, COPY, POST, LIST requests (per 1,000 requests)'}, inplace=True)
        
        s3_glacier_df = pd.merge(left=s3_glacier_df, 
                                right=s3_req_df.loc[ s3_req_df['Group'] == 'S3-API-GLACIER-Tier2' ][['Location','PricePerUnit']],
                                how='left', on='Location')
        s3_glacier_df.rename(columns={'PricePerUnit':'GET, SELECT, and all other requests (per 1,000 requests)'}, inplace=True)
        
        



        # S3 Glacier Deep Archive
        conditions = conf.get_s3_glacier_conditions()
        cols = ['Location','serviceCode','Volume Type','PricePerUnit','Storage Class','Unit','EndingRange']
        s3_bulk = ProductPriceBulk('AmazonS3GlacierDeepArchive', self.price_params)
        s3_df = s3_bulk.get_price_df(conditions, 
                                     cols, 
                                     file_name=None, 
                                     region_code=self.region_code)
        
        s3_archive_df = s3_df.loc[ (s3_df['Volume Type'] == 'Glacier Deep Archive') & 
                                   (s3_df['Storage Class'] == 'Archive' ) &
                                   (s3_df['Unit'] == 'GB-Mo') & 
                                   (s3_df['EndingRange'] == math.inf) ]
        
        s3_archive_df.rename(columns={'PricePerUnit':'First 50TB/Month'}, inplace=True)
        s3_archive_df['Next 450TB/Month'] = s3_archive_df.loc[ s3_archive_df['EndingRange'] == math.inf ]['First 50TB/Month']
        s3_archive_df['Over 500TB/Month'] = s3_archive_df.loc[ s3_archive_df['EndingRange'] == math.inf ]['First 50TB/Month']
        
        #s3_archive_df.to_csv('/Users/heejoung/Workspace/Hadoop_Mig/hadoop-migration-assessment/optimized-tco-calculator/aws-product-price/data/s3_archive_df.csv')
        
        
        # S3 Deep archive - Get
        s3_archive_df = pd.merge(left=s3_archive_df,
                                 right=s3_req_df.loc[ s3_req_df['Group'] == 'S3-API-GDA-Tier2' ][['Location','PricePerUnit']],
                                 how='left', 
                                 on='Location')
        s3_archive_df.rename(columns={'PricePerUnit':'GET, SELECT, and all other requests (per 1,000 requests)'}, inplace=True)
        

        # S3 Deep archive - Put
        conditions = conf.get_s3_req_glacier_conditions()
        s3_req_df = s3_bulk.get_price_df(conditions, 
                                         cols, 
                                         file_name=s3_bulk.get_file_name('AmazonS3GlacierDeepArchive', region_code=self.region_code), 
                                         region_code=self.region_code)
        
        s3_req_df['PricePerUnit'] = s3_req_df['PricePerUnit'] * 1000
        
        s3_archive_df = pd.merge(left=s3_archive_df,
                                 right=s3_req_df[['Location','PricePerUnit']],
                                 how='left', 
                                 on='Location')
        s3_archive_df.rename(columns={'PricePerUnit':'PUT, COPY, POST, LIST requests (per 1,000 requests)'}, inplace=True)
        
        
        # concatenate price data set
        s3_price_df = pd.concat([s3_standard_merge_df,s3_ia_df])
        s3_price_df = pd.concat([s3_price_df, s3_glacier_df])
        s3_price_df = pd.concat([s3_price_df, s3_archive_df])
        
        s3_price_df.rename(columns={'Location':'Region'}, inplace=True)
        s3_price_df['Storage'] = 'S3'
        s3_price_df.rename(columns={'Volume Type':'Type'}, inplace=True)
        s3_price_df['Type'] = s3_price_df['Type'].str.replace(pat='Standard - Infrequent Access', repl='Standard-IA', regex=False)
        s3_price_df['Type'] = s3_price_df['Type'].str.replace(pat='Amazon Glacier', repl='S3 Glacier', regex=False)
        s3_price_df['Type'] = s3_price_df['Type'].str.replace(pat='Glacier Deep Archive', repl='S3 Glacier Deep Archive', regex=False)
        s3_price_df['GB/Month'] = np.NaN
        
        region_df = s3_standard_df[['Region Code']]
        region_df = region_df.drop_duplicates(['Region Code'])
        region_list = region_df['Region Code'].values.tolist()
        
        s3_price_df = s3_price_df[["Region", "Storage", "Type", 
                                   "GB/Month", 
                                   "First 50TB/Month", 
                                   "Next 450TB/Month", 	
                                   "Over 500TB/Month", 
                                   "PUT, COPY, POST, LIST requests (per 1,000 requests)", 
                                   "GET, SELECT, and all other requests (per 1,000 requests)" ]]
    
    
    
        # get EBS price
        ebs_bulk = ProductPriceBulk('AmazonEC2', self.price_params)
        conditions = conf.get_ebs_conditions()
        cols = ['PricePerUnit','Product Family','Storage Media','Unit','Volume API Name','Volume Type','Location','Region Code']

        for region_code in region_list:
            ebs_df = ebs_bulk.get_price_df(conditions, cols, file_name=ebs_bulk.get_file_name('AmazonEC2',region_code=region_code), region_code=region_code)
            ebs_df.rename(columns={'Location':'Region'}, inplace=True)
            ebs_df['Storage'] = 'EBS'
            ebs_df.rename(columns={'Storage Media':'Type'}, inplace=True)
            ebs_df['Type'] = ebs_df['Type'].str.slice(start=0, stop=3) + "(" + ebs_df['Volume API Name'].str.upper() + ")"
            ebs_df.rename(columns={'PricePerUnit':'GB/Month'}, inplace=True)
            ebs_df['First 50TB/Month'] = np.NAN
            ebs_df['Next 450TB/Month'] = np.NAN
            ebs_df['Over 500TB/Month'] = np.NAN
            ebs_df['PUT, COPY, POST, LIST requests (per 1,000 requests)'] = np.NAN
            ebs_df['GET, SELECT, and all other requests (per 1,000 requests)'] = np.NAN
            
            ebs_df = ebs_df[["Region", "Storage", "Type", 
                             "GB/Month", 
                             "First 50TB/Month", 
                             "Next 450TB/Month", 	
                             "Over 500TB/Month", 
                             "PUT, COPY, POST, LIST requests (per 1,000 requests)", 
                             "GET, SELECT, and all other requests (per 1,000 requests)" ]]
            
            s3_price_df = pd.concat([s3_price_df, ebs_df])
        
        
        s3_price_df['sort_key'] = s3_price_df['Type'].apply(lambda x : 1 if x == 'Standard' 
                                                                 else (2 if x == 'Standard-IA' 
                                                                 else (3 if x == 'S3 Glacier' 
                                                                 else (4 if x == 'S3 Glacier Deep Archive' 
                                                                 else (5 if x == 'HDD(ST1)' else 6 )))))
 
        s3_price_df = s3_price_df.sort_values(by=['Region','sort_key'])
        s3_price_df = s3_price_df.drop(['sort_key'], axis=1)
        
        return s3_price_df
       