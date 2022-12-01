from typing import Dict



class PriceParameter:
    
    def __init__(self, params:Dict):
        self.params = {}
        if params is not None:
            self.set_params(params)
    
    def __str__(self):
        sp = ''
        keyList = self.params.keys()

        try:
            for item in keyList:
               sp = sp + '{k}\t: {v}\n'.format(k = item, v = self.params[item])
               
        except Exception as e:
            print('Error message : ', e)
                
        print(sp)
        return sp
    

    def set(self, param: str, value: str):
        try:
            self.params[param.lower()] = value
        except Exception as e:
            print('Error message : ', e)
            
    def set_params(self, params:Dict):
        for key in params:
            self.set( param=key, value=params[key])
        
    
    def get(self, param:str):
        try:
            return self.params[param.lower()]
            
        except Exception as e:
            print('Error Message : ', e)
            return None
        

    def get_parameters(self):
        return self.params
    
    
    def remove(self, param: str):
        try:
            self.params.pop(param.lower())
            
        except KeyError:
            print('Not exists the paramter.')
        except Exception as e:
            print('Error message : ', e)

