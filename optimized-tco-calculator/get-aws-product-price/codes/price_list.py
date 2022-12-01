import os
import datetime
import pandas as pd
import argparse
import pricelist.config.config as conf
from pricelist.s3_price import S3Price
from pricelist.emr_price import EMRPrice
from pricelist.common.price_parameter import PriceParameter
import warnings

# ignore SettingWithCopyWarning :sungyoul
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)



def parse_args():
    parser = argparse.ArgumentParser()         
    parser.add_argument("--region-code", "-r", dest="regioncode", required=False, type=str, help = "AWS region code")
    parser.add_argument("--output-path", "-p", dest="outputpath", required=False, type=str, help = "The path of output Excel files.")
    args = parser.parse_args()
    #print(args)
    
    return args   




def remove_temp_file(temp_path):
    del_date = datetime.datetime.today() - datetime.timedelta(days=2)
    
    if os.path.exists(temp_path):
        for file in os.scandir(temp_path):
            if file.name[-12:-4].isdigit():
                if (int(file.name[-12:-4]) <= int(del_date.strftime("%Y%m%d"))):
                    os.remove(file.path)


def get_emr_s3_price_list(region_code, result_path, temp_path):
    price_param = PriceParameter({'regionCode':region_code, 'tempFilePath':temp_path,'resultFilePath':result_path})
    
    emr_price = EMRPrice(price_param)
    s3_price = S3Price(price_param)
    
    emr_price_df = emr_price.get_price_list()
    s3_price_df = s3_price.get_price_list()
    
    emr_price_df = emr_price_df[emr_price_df['Region'].isin(s3_price_df['Region'].values.tolist())]
    s3_price_df = s3_price_df[s3_price_df['Region'].isin(emr_price_df['Region'].values.tolist())]
    
    file_name = "{0}/emr_s3_pricing_table-{1}.xlsx".format(result_path, datetime.datetime.today().strftime("%Y-%m-%d"))
    
    writer = pd.ExcelWriter(file_name, 
                            engine='xlsxwriter')
    
    emr_price_df.to_excel(writer, sheet_name="emr", index=False)
    s3_price_df.to_excel(writer, sheet_name="s3-ebs", index=False)
    
    writer.save()
    
    print(f"[Done] The filename of the price list is '{file_name}'")



if __name__ == "__main__":
    args = parse_args()
    region_code = args.regioncode
    output_path = args.outputpath
    
    if output_path is None:
        result_path = conf.get_default_file_path('RESULT')
        temp_path = conf.get_default_file_path('TEMP')
    else:
        result_path = output_path
        temp_path = output_path + '/temp'
    

    if not os.path.exists(result_path):
        os.makedirs(result_path)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    
    
    remove_temp_file(temp_path)
    get_emr_s3_price_list(region_code, result_path, temp_path)
    

