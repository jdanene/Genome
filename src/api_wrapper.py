import json
import requests



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


