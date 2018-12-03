import json
import requests



class PatentView:
    def __init__(self,parameters= '', fields = '',endpoint = 'patents', num_results = 25):
        self.parameters = parameters
        self.fields = fields
        self.endpoint = endpoint
        self.num_results = num_results
        pass

    def get_patents(self):
        base_url = "http://www.patentsview.org/api/"+self.endpoint+"/query?q="
        parameters = json.dumps(self.parameters)
        fields = json.dumps(self.fields)
        num_result = self.num_to_pages(self.num_results)
        if len(fields) == 2:
            full_text = base_url+parameters+num_result
        else:
            full_text = base_url+parameters+"&f="+fields+num_result

        self.request  =requests.get(full_text)
        print(self.request.status_code)
        

    def num_to_pages(self,num_results):
        pages=0
        for j in range(0,num_results,10000):
            pages+=1%10000
        if pages>1:
            total= json.dumps({"page":pages,"per_page":10000})
        else:
            total= json.dumps({"page":1,"per_page":num_results})
        return "&o="+total


