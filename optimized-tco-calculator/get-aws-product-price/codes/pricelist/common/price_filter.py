from typing import List

class PriceFilter:
    filters = []
    
    def __init__(self, filters: List=None):
        self.filters = filters
        
    def __len__(self):
        if self.filters is None:
            return 0
        else:
            return len(self.filters)

    def __str__(self):
        st = '{{"Field": "{f}", "Value": "{v}", "Type": "TERM_MATCH"}},'
        sf = '['
        
        try:
            for idx, val in enumerate(self.filters):
                sf = sf + st.format(f = val, v = self.filters[val])
        except Exception as e:
            print('Error message : ', e)
                
        sf = sf[0:len(sf)-1] + ']'
        # print(sf)
        return sf



    def set(self, field: str, value: str):
        try:
            if self.filters is None:
                self.filters = {field:value}
                return
                
            idx = 0
            for idx, val in enumerate(self.filters):
                if val == field:
                   self.filters[val] = value
                   return
               
            if idx+1 == len(self.filters):
                self.filters[field]=value

        except Exception as e:
            print('Error message : ', e)
            
    def remove(self, field: str):
        try:
            idx = 0
            for idx, val in enumerate(self.filters):
                if val == field:
                   del self.filters[val]
                   break
               
        except Exception as e:
            print('Error message : ', e)
            
            
    def get_filters(self):
        return self.filters


    def get(self, field:str):
        try:
            for val in self.filters:
                if val == field:
                    return self.filters[val]
               
        except Exception as e:
            print('Error message : ', e)
            return None




    