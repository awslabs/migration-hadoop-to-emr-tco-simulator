import boto3
import pandas as pd
from typing import List
from datetime import datetime,timedelta

class SpotPrice:
    
    def __init__(self, region_code):
        self.client = boto3.client('ec2', region_name=region_code)
        

    def get_product_list(self, InstanceList:List):

        if len(InstanceList) == 0:
            return None
                
        FilterEndTime = datetime.now()
        FilterStartTime = FilterEndTime - timedelta(hours=6)

        try:
            response = self.client.describe_spot_price_history(StartTime=FilterStartTime,
                                                               EndTime=FilterEndTime,
                                                               InstanceTypes=InstanceList,
                                                               ProductDescriptions=['Linux/UNIX'],
                                                               )
        except Exception as e:
            return None
        
        spot_df = pd.DataFrame(response['SpotPriceHistory'])
        spot_df['RN'] =  spot_df.sort_values(['Timestamp'], ascending=False).groupby(['InstanceType']).cumcount() + 1
        spot_df = spot_df.loc[spot_df['RN']==1]
        spot_df = spot_df[['InstanceType', 'SpotPrice']]
        spot_df = spot_df.astype({'SpotPrice':'float64'})

        spot_df.rename(columns={'SpotPrice':'SPOT'},inplace=True)
        spot_df.rename(columns={'InstanceType':'Instance Type'},inplace=True)

        return spot_df 
    



