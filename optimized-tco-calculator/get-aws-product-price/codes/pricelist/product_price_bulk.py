import os
import pandas as pd
import datetime as dt
import requests as req
import pricelist.config.config as conf
from typing import Dict
from typing import List
from pricelist.common.price_parameter import PriceParameter


class ProductPriceBulk:
    def __init__(self, service_code, price_params:PriceParameter):
        self.price_params = price_params
        self.service_code = service_code
        
    def get_file_name(self, service_code, region_code):
        
        file_path = self.price_params.get('tempFilePath')
        
        if service_code is None:
            service_code = self.service_code
         
        today = dt.datetime.now()   
        if region_code is None:
            file_name = "{0}/{1}_{2}.csv".format(file_path, service_code, today.strftime("%Y%m%d"))
        else:
            file_name = "{0}/{1}_{2}_{3}.csv".format(file_path, service_code, region_code, today.strftime("%Y%m%d"))
        return file_name


    def get_price_list_bulk_file(self, region_code):
        
        # get offer index file
        # ex) "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{service}/current/index.csv"
        if region_code is None:
            url = conf.get_offer_index_file().format(service=self.service_code)
        else:
            url = conf.get_offer_region_index_file().format(service=self.service_code, region=region_code)
        
        
        file_name = self.get_file_name(self.service_code, region_code)
        if os.path.isfile(file_name):
            print("The offer file for {0} is existed.\n  > Filename : {1}".format(self.service_code, file_name))
            return file_name
        
        try:
            print('Downloading... The price list offer file for {0}.\nFile : {1}'.format(self.service_code, file_name))
            file = req.get(url, allow_redirects=True)
            open(file_name, 'wb').write(file.content)
            print('Done : {0}'.format(file_name))
        
        except Exception as e:
            print("[Error] Can't not download the offer file for {0} service . \n {2}".format(self.service_code, e))
            return None
        
        return file_name
        


    def get_price_df(self, filters:Dict, cols:List, file_name, region_code):
        
        if file_name is None:
            file_name = self.get_price_list_bulk_file(region_code)
            if file_name is None:
                return None
        
        try:
            price_bulk_df = pd.read_csv(file_name, skiprows=5,low_memory=False)
        except Exception as e:
            print("[Error] Can't read the offer file : {0}\n{1}".format(file_name, e))
            return None
        
        for f in filters:
            if type(filters[f]) is list:
                price_bulk_df = price_bulk_df[price_bulk_df[f].isin(filters[f])]
            elif type(filters[f]) is str and filters[f] == 'Na':
                price_bulk_df = price_bulk_df[ price_bulk_df[f].isna() ]
            else:
                price_bulk_df = price_bulk_df[ price_bulk_df[f] == filters[f] ]

        if cols is not None:
            price_bulk_df = price_bulk_df[cols]
        
        return price_bulk_df
    
    
