import os, sys, csv, zipfile
from api_wrapper import PatentView, ListToQuery, Json_to_DataFrame
from datetime import datetime, timedelta
import pandas as pd
#Fields that I'm currently interested in
#fields = ["assignee_organization","patent_id","app_date","app_type",
         #"inventor_id","examiner_group","patent_num_foreign_citations","patent_num_us_patent_citations",
         #"patent_num_us_application_citations","patent_num_cited_by_us_patents","cited_patent_number","pct_date"]
#fields1 = ["patent_id","pct_date","pct_kind","pct_doctype"]

def load_cpc(BASE_PATH  = "/Users/dominicanene/Box/project/"):
    '''
    Loads hand-selected CPC codes into a list

    Input:void()
      
    Returns: 
        dup_list1 ([list-of string]:) unique(CPC codes w/ atleast one duplicate)
        dup_list2 ([list-of string]:) unique(CPC codes w/ atleast two duplicate)
        dup_list3 ([list-of string]:) unique(CPC codes w/ atleast three duplicate)
        dup_list4 ([list-of string]:) unique(CPC codes w/ atleast four duplicate)
        uniq_list ([list-of string]:) unique(CPC codes w/ atleast four duplicate)
    
    Uses: We want to get patent data for gene engineering companies. The cpc codes
    in the list will do that, but the API can only take a query of a certain length.
    So if you need to cut down on the size pick a different return
    '''

    f = os.path.join(BASE_PATH,"data","cpc_data.txt")
    hold_cpc = []
    with open(f) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            hold_cpc = hold_cpc + row
    hold_cpc = [j.replace(" ","") for j in hold_cpc if ((j != '') and (j != ' ')) ]
    dup_list1 = list(set([i for i in hold_cpc if hold_cpc.count(i)>1]))
    dup_list2 = list(set([i for i in hold_cpc if hold_cpc.count(i)>2]))
    dup_list3 = list(set([i for i in hold_cpc if hold_cpc.count(i)>3]))
    dup_list4 = list(set([i for i in hold_cpc if hold_cpc.count(i)>4]))
    uniq_list = list(set(hold_cpc))
    return dup_list1, dup_list2, dup_list3, dup_list4, uniq_list

def cpcDateRange(qValues, startdate = '2015-01-01', enddate = '2018-10-31'):
    '''
    Gets in and already cleaned query and appends app-date range, and then outputs a formatted query
    
    Input:
        qValues (list) : [list-of cpc_subgroup_id]
        startdate(str) : '%Y-%m-%d' formmated string date
        startdate(str) : '%Y-%m-%d' formmated string date

    Output:
        fullq (str): A full query string that you can feed directly to PatentView(parameters = fullq)

    '''

    query = ListToQuery() 
    listOf_parameters = []
    startdate = datetime.strptime(startdate, '%Y-%m-%d')
    enddate = datetime.strptime(enddate, '%Y-%m-%d')
    startdate= startdate.strftime("%Y-%m-%d")
    enddate= enddate.strftime("%Y-%m-%d")

    q = query.list_to_query(["cpc_subgroup_id","assignee_type"],
                          [qValues,["2","3"]],["or","or"])

    #Remove E = Fixed Constructing, F = Mechanical Engineering; Lighting; Heating; Weapons; Blasting Engines; Pumps, 
    #H = Electricity,D = Textiles; paper
    cpc_filer = {} 
    examiner_filer = '{"_or": [{"_lt": {"examiner_group": "1799"}},{"_gt": {"examiner_group": "3715"}}]}'
    cpc_filter = '{"_or": [{"cpc_section_id":"G"},{"cpc_section_id":"A"},{"cpc_section_id":"C"}]},{"_neq": {"assignee_organization":"None"}}'
    fullq = '{"_and": ['+q+',{"_gte":{"app_date":"'+startdate+'"}},{"_lt":{"app_date":"'+enddate+'"}},'+examiner_filer+']}'
    return fullq

def get_BigData(pdData,BIGFILE, chunkSize=1000):
    '''
    This function is meant to read ./data/claim.tsv.zip & ./data/brf_sum_text.tsv.zip
    and then merge on "patent_id" to build a data set of text data.text

    Input:
        pdData (pd.DataFrame) : Pandas data fram w/ unique patent data identifier "patent_id"
        BIGFILE (str) : the location of the zipfile to open
        chunkSize (int) : '%Y-%m-%d' formmated string date

    Output:
        result_df (pd.DataFrame) : Merged data set w/ values from `BIGFILE`

    '''

    #Convert "Patent_id" to numeric for merge
    patentData= pdData["patent_id"].to_frame()
    patentData["patent_id"]=pd.to_numeric(patentData["patent_id"],errors='coerce')
    # Number of rows in patent data
    N = patentData.shape[0]
    #Loop of rows in zip file and merge w/ patent data
    with zipfile.ZipFile(BIGFILE) as zf:
        df_iterator = pd.read_csv(zf.open(zf.namelist()[0]), sep ="\t",chunksize= chunkSize)
        i = 0
        tot = 0
        totBags = 0
        for curr_df in df_iterator:
            tot += curr_df.shape[0]

            #Convert patent ID to numeric for merge
            curr_df["patent_id"]=pd.to_numeric(curr_df["patent_id"],errors='coerce')

            if i == 0:
                result_df = pd.merge(patentData, curr_df, how='inner', on=['patent_id'])
                merged_df = result_df
            else:
                merged_df = pd.merge(patentData, curr_df, how='inner', on=['patent_id'])
                result_df = result_df.append(merged_df, ignore_index=True)
            
            if result_df.shape[0] == N: break
            print("iter: ",i, ", chunk:", curr_df.shape,", tot seen : ", tot," merged sz:",merged_df.shape[0]," perc finish:",
                 "{:.0%}".format(result_df.shape[0]/N),"\r",end=" ")
            i =i+ 1
    sys.stdout.flush()
    return result_df

class ExtractData:
    '''
    Methods:
    get_data(void): Just run this after you define your Attributes to get the data

    Attributes: 
    BASE_PATH (str) :Base path to get data, #FixMe: Absolute path

    STARTDATE(str['%Y-%m-%d']) :Start of Interval

    ENDDATE(str['%Y-%m-%d']) :End of Interval

    APINOTE(str) :Note to put on the end of this round of API data

    CLAIM_Note(str) :Note to put for outputted claim data. 


    CLAIMS_DF (pd.DataFrame): Claims textual data
    pdData (pd.DataFrame) : Data of additional features. 
    '''
    def __init__(self):
        #ToDo: There a 200K words in the bag wtf! Need to only select on nber category also probably
        # should generalize `cpcDateRange()` to take queries so don't have to hard code it in. 

        #convert string date to another representation
        convert_date = lambda d: datetime.strptime(d, '%Y-%m-%d').strftime('%Y%m%d')

        #Base path to get data, #FixMe: Absolute path
        self.BASE_PATH = "/Users/dominicanene/Box/project/"

        #Start of Interval
        self.STARTDATE = '2007-01-01'

        #End of Interval
        self.ENDDATE = '2018-10-31'

        #Note to put on the end of this round of API data
        self.APINOTE  = "count"

        #Note for claim data. 
        self.CLAIM_Note = "claim"

        #Output file names
        OUTPUT_FILEBASE = convert_date(self.STARTDATE)+"_"+convert_date(self.ENDDATE)+".pkl"

        # API data file name
        self.API_DATA_NAME=os.path.join(self.BASE_PATH ,'data',self.APINOTE+OUTPUT_FILEBASE)

        # Count output file name
        self.CLAIM_OUTFILE_NAME=os.path.join(self.BASE_PATH ,'data',self.CLAIM_Note+OUTPUT_FILEBASE)


        # The huge ass data files from PatentView to get text data from
        self.CLAIM_FILE = os.path.join(self.BASE_PATH ,'data','claim.tsv.zip')
        self.SUMMARY_FILE = os.path.join(self.BASE_PATH ,'data','brf_sum_text.zip')

    def get_data(self):
        #If condition to check if file is alive, don't want to pull from the api too much!
        if not os.path.isfile(self.API_DATA_NAME):
            #Load CPC text file data
            qValues0,qValues1,qValues2,qValues3,qValues4 = load_cpc(self.BASE_PATH)

            #cpc codes -> query
            date_pars = cpcDateRange(qValues1, startdate = self.STARTDATE, enddate = self.ENDDATE)

            #query -> json.response
            api_data = PatentView(parameters = date_pars, 
                             fields = ["patent_id", "assignee_organization", "app_date","patent_date","patent_title","patent_abstract","patent_kind","examiner_group","cpc_subgroup_id","cpc_subgroup_title","nber_category_id","nber_category_title"], 
                             num_results = 10000)
            api_data.get_patents() #Ask PatentView for the data
            response = api_data.request #Put it into a pointer

            #json.response -> pd.DataFrame
            data = Json_to_DataFrame(response)
            data.get_df()
            pdData = data.df

            #CROSS-TAB on NBER Technology Categories
            pd.crosstab(pdData["nber_category_id"],pdData["nber_category_title"])

            #save data
            pdData.to_pickle(self.API_DATA_NAME)
        else:
            pdData = pd.read_pickle(self.API_DATA_NAME)

        #Merge claims huge data set w/ the patent_id's from API
        if not os.path.isfile(self.CLAIM_OUTFILE_NAME):
            claims_df = get_BigData(pdData,self.CLAIM_FILE)
            claims_df=claims_df.sort_values(by=["patent_id"])
            claims_df.to_pickle(self.CLAIM_OUTFILE_NAME)
        else:
            claims_df = pd.read_pickle(self.CLAIM_OUTFILE_NAME)

        self.CLAIMS_DF = claims_df
        self.pdData = pdData






