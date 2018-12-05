import pandas as pd
import json


class Json_to_DataFrame:
    '''input is a legit response only'''
    def __init__(self,response):
        self.json_data = json.loads(response.content)
        self.data = self.json_data['patents']
        self.raw_groups = ["cited_patents","inventors","application_citations",
                "applications", "assignees","citedby_patents","coinventors",
                "cpc_subgroups", "cpc_subsections", "cpcs", "IPCs", 
                "locations", "nber_subcategories","nbers","patents",
                "uspc_mainclasses", "uspc_subclasses","uspcs","years", 
                "rawinventors","wipos","gov_interests","examiners","cited_patents"]
        self.groups = [g for g in self.raw_groups if g in self.data[0].keys()]
        self.df = pd.DataFrame()
    def get_df(self):
        if not self.groups:
            self.data_dict = self.raw_groups
        else:
            self.data_dict = self.get_data(dict(), self.data)
        self.df = pd.DataFrame(self.data_dict)

    def add_to_dict(self,orginal_dict,key,val):
        if key in orginal_dict.keys():
            orginal_dict[key] = orginal_dict[key] + [val]
        else:
            orginal_dict[key]= [val]
        return orginal_dict

    def single_fields(self, data_dict,a_dict):
        data_dict_= data_dict.copy()
        a_dict_= a_dict.copy()
        key = list(a_dict_.keys())[0]
        val = a_dict_[key]
        if len(a_dict_)==1: 
            return self.add_to_dict(data_dict_,key,val)
        else:
            data_dict_=self.add_to_dict(data_dict_,key,val)
            a_dict_.pop(key, None)
            return self.single_fields(data_dict_, a_dict_)        

    def unravel_fields(self,entry_data):
        item_to_tuple = lambda key,value: (key,value)
        i = 0
        return_vals = []
        for d in entry_data:
            if (i == 0):
                _ = [item_to_tuple(key,val) for key,val in d.items()]
            else:
                _ = [item_to_tuple(key+str(i),val) for key,val in d.items()]
            return_vals+=_
            i+=1
        return dict(return_vals)

    def get_columns(self,entry,data_dict):
        
        for g in entry.keys():
            field_data = entry[g] 
            if g in self.groups:
                if len(field_data)>1:
                    data_dict = self.single_fields(data_dict,self.unravel_fields(field_data))
                else:
                    data_dict = self.single_fields(data_dict,field_data[0])
            else:
                data_dict = self.add_to_dict(data_dict,g,field_data)
        return data_dict

    def same_size_adjustment(self, data_dict, i):
        entries = i+1
        for key, val in data_dict.items():
            if len(val)< entries:
                n=len(val)
                diff = entries-n
                val = [None]*diff + val
                data_dict[key]=val
        return data_dict

    def get_data(self, data_dict, data):
        i = 0
        data_dict = dict()
        for entry in data:
            data_dict = self.get_columns(entry,data_dict)
            if i != 0:
                data_dict= self.same_size_adjustment(data_dict,i)
            i+=1
        return data_dict

    def add_to_df(newdf):
        self.df = pd.concat([self.df, newdf], ignore_index=True)

