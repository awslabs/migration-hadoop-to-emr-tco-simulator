import pandas as pd
import numpy as np
import pricelist.config.config as conf
from pricelist.product_price_bulk import ProductPriceBulk
from pricelist.spot_price import SpotPrice
from pricelist.common.price_parameter import PriceParameter

class EMRPrice():
    SERVICE_CODE_VALUE = 'ElasticMapReduce'

    def __init__(self, price_params:PriceParameter):
        self.price_params = price_params
        self.region_code = price_params.get('regionCode')
        self.ec2_region_price_df = pd.DataFrame()
        return
        

    def get_ec2_price_list(self, instance_list, region_code):
        
        # For EC2
        ec2_bulk = ProductPriceBulk('AmazonEC2', self.price_params)
        
        conditions = conf.get_ec2_conditions()
        conditions['Instance Type'] = instance_list
        conditions['Region Code'] = region_code
        
        cols = ['PricePerUnit','Instance Type','LeaseContractLength','vCPU','Memory','ECU','Pre Installed S/W','TermType','Location','EndingRange',\
            'PurchaseOption','OfferingClass','Product Family','Instance Family','Storage','Tenancy','Operating System','CapacityStatus','ClassicNetworkingSupport']

        ec2_df = ec2_bulk.get_price_df(conditions, cols, file_name=None, region_code=region_code)

   
        # For OnDemand EC2 Instance
        ondemand_df = ec2_df[ec2_df['TermType'] == 'OnDemand']
        ondemand_df = ondemand_df[['PricePerUnit','Instance Type','vCPU','Memory','Location']]


        # For Reserved EC2 Instance (1yr) 
        reserved1_df = ec2_df.loc[ (ec2_df['TermType'] == 'Reserved') & (ec2_df['PurchaseOption'] == 'No Upfront' ) \
                                    & (ec2_df['OfferingClass'] == 'standard') & (ec2_df['LeaseContractLength'] == '1yr') ]
        
        reserved1_df = reserved1_df[['PricePerUnit','Instance Type']]
        reserved1_df.rename(columns={'PricePerUnit':'1 year RI'}, inplace=True)


        # For Reserved EC2 Instance (3yr)
        reserved3_df = ec2_df.loc[ (ec2_df['TermType'] == 'Reserved') & (ec2_df['PurchaseOption'] == 'No Upfront' ) \
                                    & (ec2_df['OfferingClass'] == 'standard') & (ec2_df['LeaseContractLength'] == '3yr') ]
     
        reserved3_df = reserved3_df[['PricePerUnit','Instance Type']]
        reserved3_df.rename(columns={'PricePerUnit':'3 year RI'},inplace=True)



        # Merge DataFrame (OnDemand & Reserved 1yr & Reserved 3yr)
        merged_df = pd.merge(left=ondemand_df, right=reserved1_df, how = 'inner', on='Instance Type')
        merged_df = pd.merge(left=merged_df, right=reserved3_df, how='inner', on='Instance Type')
        

        
        # For Spot Instance
        spot = SpotPrice(region_code)
        spot_df = spot.get_product_list(merged_df['Instance Type'].tolist())
        
        if spot_df is not None:
            merged_df = pd.merge(left=merged_df, right=spot_df, how='inner', on='Instance Type')
        else:
            merged_df['SPOT'] = np.NaN
        
        merged_df = merged_df[['Location','Instance Type','vCPU','Memory','PricePerUnit','3 year RI','1 year RI','SPOT']]
        merged_df.columns=['Region', 'Type', 'vcpu', 'mem', 'On demand', '3 year RI', '1 year RI', 'SPOT']

        # change memory column value type to intger : 256 Gib -> 256 : sungyoul.
        merged_df['mem'] = merged_df['mem'].str.split(' ').str[0]
        merged_df = merged_df.astype({'mem':float})
        ########################################################################
        
        merged_df = merged_df.sort_values(by=['Region','Type'])
        
        self.ec2_price_df = pd.concat([self.ec2_price_df, merged_df])
        

        
        
        
        


    def get_price_list(self):
        
        # For EMR
        conditions = conf.get_emr_conditions()
        cols = ['PricePerUnit','Instance Type','Location','Region Code']
        
        emr_bulk = ProductPriceBulk(self.SERVICE_CODE_VALUE, self.price_params)
        emr_df = emr_bulk.get_price_df(filters=conditions, 
                                       cols=cols, 
                                       file_name=None, 
                                       region_code=self.region_code)
        
        emr_df = emr_df.dropna(subset=['Region Code'])
        
        #filtering data that only include region code and exclude local zone code.
        emr_df = emr_df.loc[ emr_df['Region Code'].str.match('[a-z]+-[a-z]+-[1-9]+$') ]
        
        instance_df = emr_df.drop_duplicates(['Instance Type'])
        instance_list = instance_df['Instance Type'].values.tolist()
        
        region_df = emr_df.drop_duplicates(['Region Code'])
        region_list = region_df['Region Code'].values.tolist()
        
         
        self.ec2_price_df = pd.DataFrame()
        for region_code in region_list:
            self.get_ec2_price_list(instance_list, region_code)
    
        emr_df.rename(columns={'Instance Type':'Type', 'Location':'Region', 'PricePerUnit':'EMR Service'}, inplace=True)
        emr_df = emr_df[['Region','Type','EMR Service']]
        emr_df = pd.merge(left=emr_df, right=self.ec2_price_df, how='inner', on=['Type','Region'])


        emr_df = emr_df.dropna(subset=['SPOT'])
        emr_df = emr_df[['Region', 'Type', 'vcpu', 'mem', 'On demand', '3 year RI', '1 year RI', 'SPOT', 'EMR Service']]
        emr_df = emr_df.sort_values(by=['Region','Type'])
        
        return emr_df



