'''
Created on Jan 15, 2013

@author: a0868443
'''
platforms_list = {}
 
class EquipmentInfo:
    #class to define equipment information.
    name =  None
    buildId = None
    driver_class_name = None
    init_info = None
    params = None
    
    def __init__(self,name, builId = None):
        self.name = name
        self.buildId = builId
        platforms_list[name] = self	

