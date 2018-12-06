import json
import requests
import pandas as pd




class PatentView:
    def __init__(self,parameters= '', fields = '',endpoint = 'patents', num_results = 25):
        self.parameters = parameters
        self.fields = fields
        self.endpoint = endpoint
        self.num_results = num_results
        
        pass

    def num_to_pages(self,num_results):
        pages=1
        for j in range(0,num_results,10000):
            pages+=int(j/10000)
        if pages>1:
            total= json.dumps({"page":pages,"per_page":10000})
        else:
            total= json.dumps({"page":pages,"per_page":num_results})
        return "&o="+total

    def get_full_text(self): 
        base_url = "http://www.patentsview.org/api/"+self.endpoint+"/query?q="
        if not isinstance(self.parameters, str):
             self.parameters = json.dumps(self.parameters)
        
        fields = json.dumps(self.fields)
        num_result = self.num_to_pages(self.num_results)
        if len(fields) == 2:
            self.full_text = base_url+ self.parameters+num_result
        else:
            self.full_text = base_url+ self.parameters+"&f="+fields+num_result

    def get_patents(self):
        self.get_full_text()
        self.request  =requests.get(self.full_text)
        print(self.request.status_code)
        




class ListToQuery:
    '''
    "uuid"
    Example:
        query = ListToQuery()
        pars = query.list_to_query(["inventor_last_name","inventor_last_name"],[["Whitney"],["Hopper"]],["and","and"])
        data = PatentView(parameters = pars, fields = ["patent_id"])
        data.get_patents()
        data.request.text

    '''
    def __init__(self):
        #October 6, 1981 <=> 1981-10-06
        self.main_map = {"=":"_eq","!=":"_neq",">":"_gt",">=":"_gte","<":"_lt", "<=":"_lte","and":"_and", "or":"_or", "not":"_not","in":"_contains","starts":"_begins"}
        self.text_map = {"or":"_text_any", "and":"_text_all", "in":"_text_phrase"}

        pass

    def format_query(self, qKey,qValues,rule, text):
        formatted_query = []
        if text == True:
            formatted_query = json.dumps({self.text_map[rule]:[{qKey:value} for value in qValues]})
        elif text == False:
            formatted_query = json.dumps({self.main_map[rule]:[{qKey:value} for value in qValues]})
        return formatted_query

    def get_query(self,listOf_qKey,listOf_qValues,rules,text):
        carK = listOf_qKey[0]
        carR = rules[0]
        carV = listOf_qValues[0]
        carT = text[0]

        cdrK = listOf_qKey[1:]
        cdrV = listOf_qValues[1:]
        cdrR = rules[1:]
        cdrT = text[1:]

        if not cdrT:
            return self.format_query(carK,carV,carR,carT)
        else:
            return '{"_or":['+ self.format_query(carK,carV,carR,carT)+','+self.get_query(cdrK,cdrV,cdrR,cdrT)+']}'

    def list_to_query(self, listOf_qKey, listOf_qValues, rules, text = False):
        #Turn input tuple to list
        listOf_qKey = list(listOf_qKey)
        listOf_qValues = list(listOf_qValues)
        rules = list(rules)
        try:
            text = list(text)
        except:
            text = list([text])
        if not any(isinstance(el, list) for el in listOf_qValues):
            listOf_qValues = [listOf_qValues]
        assert len(listOf_qKey) == len(listOf_qValues) == len(rules), "Size of Keys, Values, and Rules must be the same."
        #Get length for cases. 
        text_len = len(text)
        keys_len = len(listOf_qKey)
        if text_len == 1 and keys_len >= 1:
            text = text*keys_len
            return self.get_query(listOf_qKey,listOf_qValues,rules,text)
        if text_len> 1 and keys_len > 1:
            return self.get_query(listOf_qKey,listOf_qValues,rules,text)

        if text_len> 1 and keys_len == 1:
            return self.get_query(listOf_qKey,listOf_qValues,rules,text)

        raise ValueError('If Text length != 1 then it must equal length of all other parameters.')

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
