# -*- coding: utf-8 -*-
"""
Created Jan 27 2017
Edited 01/06/2017 

@author: Deborah Schneider-Luftman, ICL (UK),
@contact: ds711@ic.ac.uk

"""

import pandas as pd
import bs4 #beautifulsoup4 package
import re # RegEx 
import urllib2
import numpy as np
import os
from datetime import datetime


## Required input: files location of the .csv and .html files, and number of
# subjects N
# .csv: ukb<release_code>.csv, the main data file produced after extraction from 
#       the .enc file
# .html: associated information file, generated alongside the.csv file with all
#       references to varaibles available 
## These should be defined before loading the packageas follow:
#   import __builtin__
#   __builtin__.namehtml='<file_location>.html'
#   __builtin__.namecsv='<file_location>.csv' 
#   __builtin__.N= n
##

html_file = namehtml
csv_file = namecsv
N=n

class BiobankRead():
    """ A class to parse data from UK BioBank archives.
    
    usage:
    initialise
        bb = BiobankRead(projectID, studyID, [location])

    class variables
        html_file = path to html
        soup = parsed tables from html
        Vars = all variables extracted in data frame
        Eids_all 
    
    class methods
        status()
        files_path([opt='html' or 'csv']) return path to file
        results = All_variables() read all variables in the table and return
                (used to set Vars as part of initialisation)
        
    """
    
    # needed to handle some funny variable names
    special_char = "~`!@#$%^&*()_-+={}[]:>;',</?*-+" 
    
    defloc = os.path.join('D:\\', 'Uk Biobank', 'Application ')
    sub_link  = 'http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id='
    code_link = 'http://biobank.ctsu.ox.ac.uk/crystal/coding.cgi?id='

    
    def __init__(self, location=None, N=n):
        
        # Status
        self.OK = True
        
        # Number of cases
        self.N = N
    
        # Get filepath
        self.location = BiobankRead.defloc
        if location != None:
            self.location = location
        
        # Construct the path to the html file
        self.html_file = html_file#self.files_path()
        self.csv_file = csv_file#self.files_path()
        if self.html_file == None:
            print 'error - html location', location, 'not found'
            self.OK = False
            return
        #HES file processing variables
        this_dir, this_filename = os.path.split(__file__)
        self.DATA_PATH = os.path.join(this_dir, "data", "ICD10_UKB.tsv")
        self.DATA_PATH_2 = os.path.join(this_dir, "data","ICD9_codes.csv")        
        
        
        # Parse html 
        self.soup = self.makeSoup()
        
        #Time/date variables
        self.date_format = "%Y-%m-%d"
        self.end_follow_up = "2016-02-15"
        self.start_follow_up = "2006-05-10"
        self.Time_end = datetime.strptime(self.end_follow_up, self.date_format)
        
        # Variables in table
        # Populate by calling self.All_variables()
        self.Vars = self.All_variables()['names']
        self.data_types = self.All_variables()['types']
        
        # All EIDS
        # Populate by calling self.GetEIDs(n_subjects=N)
        # QUERY - WHERE IS N SET?
        self.Eids_all = self.GetEIDs()
        # This appears clumsy but is because None can't be compared to a data frame
        # http://stackoverflow.com/questions/36217969/how-to-compare-pandas-dataframe-against-none-in-python
        self.OK = False
        if self.Eids_all is not None:
            self.OK = True
        if not self.OK:
            print 'error - failed to get Eids'
            self.OK = False
            return
        
        # All attendance dates
        # QUERY - WHERE IS N SET?
        #self.assess_dates = self.Get_ass_dates()
        
    def status(self):
        print 'html:', self.html_file
        print 'Record number', self.N
        return

    def makeSoup(self):
        """Parse the html into a nested data structure"""
        f = open(self.html_file, 'r').read()
        soup = bs4.BeautifulSoup(f, 'html.parser')
        return soup
        

    def All_variables(self):
        """Read all variable names in the table and return"""
        allrows = self.soup.findAll('tr')
        res = []
        data_type = []
        for t in allrows:
            re_string = 'nowrap;\">(.*?)</span></td><td rowspan=\"(\d+)\">(.*?)</td></tr>'
            #'</span></td><td rowspan=(.*?)>(.*?)</td></tr>'
            res1=re.search(re_string,str(t))
            if not res1 is None:
                res1 = res1.group(0)
                ## get variable data type
                x1,y1,z1=res1.partition('nowrap;\">')
                xx1,yy1,zz1=z1.partition('</span>')
                data_type.append(xx1)
                ## get variable name
                x,y,z = zz1.partition('">')
                xx,yy,zz = z.partition('</td></tr>')
                if xx.find('<br>') > -1:
                    t = xx.find('<br>')
                    xx = xx[0:t]
                res.append(xx)
        res2 = []
        for x in res:
            if x.find('<br/>') >-1:
                 t = x.find('<br/>')
                 xx = x[0:t]
                 res2.append(xx)
            else:
                 res2.append(x)
        res = res2
        return {'names':res, 'types':data_type}

    def GetEIDs(self):
        """Return all the EIDs"""
        # data frame of EIDs
        filename = self.csv_file 
        if filename == None:
            return None
        EIDs = pd.read_csv(filename, usecols=['eid'], nrows=self.N)
        return EIDs
    
    def Get_ass_dates(self):
        # data frame of EIDs
        var = 'Date of attending assessment centre'
        Ds = self.extract_variable(var)
        return Ds   

    def extract_variable(self, variable=None, baseline_only=False):
        '''
        Extracts a single specified variable  (input)
        Returns data for first visit only if baseline_only == True
        This function updated by Bill Crum 13/02/2018
        '''
        
        ### extract fields 
        allrows = self.soup.findAll('tr')
        
        ## search variable string for shitty characters
        symbols = BiobankRead.special_char
        
        # Deal with special symbols in variable name
        varlist = list(variable)
        newvar = []
        for v in varlist:
            if v in symbols:
                newvar.extend(['\\', v])
            else:
                newvar.extend([v])
        variable = ''.join(newvar)
                
        # Find variable embedded like this:
        # ... <td rowspan="1">Heel ultrasound method<br> ...
        # Or this:
        # ... <td rowspan="1">Heel ultrasound method.<br> ...
        searchvar = '>'+variable+'(.?)<'
        userrows = [t for t in allrows if re.search(searchvar,str(t))]
        if not userrows:
            raise Exception('The input variable is not in the files')
        if len(userrows) > 1:
            print 'warning - more than one variable row found'
            print 'warning - returning first instance only'
        userrows_str = str(userrows[0])

        # extract IDs related to variables
        # extract all variable names
        match1 = re.search('id=(\d+)',userrows_str)
        if match1:
            idx = match1.group(1)
        else:
            print 'warning - index for', variable, 'not found'
            return None
            
        ## Retrieve all associated columns with variables names 
        # Encoded anonymised participant ID
        key = ['eid']
        for link in self.soup.find_all('a', href=BiobankRead.sub_link+idx):
            tmp = str(link.contents[0].encode('utf-8'))
            key.append(tmp) 
        everything = pd.read_csv(self.csv_file, usecols=key, nrows=self.N)
        
        #na_filter=False)
        # drop columns of data not collected at baseline 
        if baseline_only:
            cols = everything.columns
            keep = ['0.' in x for x in cols]
            keep[0] = True # always keep eid column
            everything = everything[cols[keep]]
            
        return everything
        
        
    def illness_codes_categories(self, data_coding=6):
        """Returns data coding convention from online page"""
        
        ## Get dictionary of disease codes
        link = BiobankRead.code_link+str(data_coding)
        response = urllib2.urlopen(link)
        html = response.read()
        soup = bs4.BeautifulSoup(html,'html.parser')
        allrows = soup.findAll('tr')
        
        ## find all categories of illnesses
        userrows = [t for t in allrows if t.findAll(text='Top')]
        userrows_str = [] # convert to string
        for j in userrows:
            userrows_str.append(str(j))
        Group_codes, Group_names = [], []
        for line in userrows_str:
                match1 = re.search('class="int">(\d+)',line)
                Group_codes.append(match1.group(1))
                b,k,a = line.partition('</td><td class="txt">No')
                bb,kk,aa = b.partition('"txt">')
                Group_names.append(aa)
        Groups = pd.Series(data=Group_codes,index=Group_names)
        return Groups
        
           
    def all_related_vars(self, keyword=None, dropNaN=True):
        '''
        Extracts all variables related to a keyword variable (input)
        Returns one single df with eids and each variable
        This function updated by Bill Crum 13/02/2018
        '''
        
        if keyword is None:
            print ' (all_related_vars) supply keyword to search over'
            return None
            
        stuff = [t for t in self.Vars if keyword in t]
        stuff_var = {}
        if len(stuff) > 0:
            for var in stuff:
                DBP = self.extract_variable(variable=var)
                if dropNaN:
                    # drop subjects with no reported illness
                    tmp = list(DBP.columns.values)
                    DBP = DBP[np.isfinite(DBP[tmp[1]])]    
                stuff_var[var] = DBP
        else:
            print 'No match for', keyword, 'found'
        return stuff_var, stuff


    def extract_many_vars(self, keywords=None,
                          dropNaN=False,spaces=False,baseline_only=False):
        # extract variables for several pre-specified var. names 
        # returns one single df with eids and each variables as columns

        # Convert single argument to list
        # This because len(string) > 1
        if isinstance(keywords, basestring):
            keywords = [keywords]

        main_Df = pd.DataFrame(columns =['eid'])
        main_Df['eid'] = self.Eids_all['eid']
        for var in keywords:
            DBP = self.extract_variable(variable=var, baseline_only=baseline_only)
            if spaces:
                b,k,a = var.partition(' ')
                var = b
            DBP = self.rename_columns(DBP, var)
            if dropNaN:
            # drop subjects with no reported illness
                tmp = list(DBP.columns.values)
                DBP = DBP[np.isfinite(DBP[tmp[1]])]    
            main_Df = pd.merge(main_Df,DBP,on='eid',how='outer')
        '''
        else:
           #print stuff[0]
           main_Df = self.extract_variable(variable=keywords, baseline_only=baseline_only)
           tmp = list(main_Df.columns.values)
           if dropNaN:
               main_Df = main_Df[np.isfinite(main_Df[tmp[1]])]
        '''
        return main_Df


    def Mean_per_visit(self, df=None,dropnan=False):
        # average of one variable at each visit
        # input= df with variables of interest
        # only relevant if multiple measurements available
        Tmp = list(df.columns.tolist())
        # isolate variables
        tmp2 = list(set([x.partition('_')[0] for x in Tmp]))
        tmp2 = [y for y in tmp2 if 'eid' not in y] # remove eid column
        # initiate output
        new_df = pd.DataFrame(columns=['eid'])
        new_df['eid']=df['eid']
        # for each variable in df
        for var in tmp2:
            sub = [x for x in Tmp if var+'_' in x]
            sub_rounds = [x.partition('_')[2] for x in sub]
            rounds = [x.partition('.')[0] for x in sub_rounds]
            u=0
            df_sub = pd.DataFrame(columns=['eid'])
            df_sub['eid']=df['eid']
            # for each visit
            for t in range(int(max(rounds))+1):
                per_round = [x for x in sub if '_'+str(t) in x]
                if dropnan:
                    df_sub[var+str(u)] = df[per_round].mean(axis=1,skipna=False)
                else:
                    df_sub[var+str(u)] = df[per_round].mean(axis=1)
                u +=1
            new_df = pd.merge(new_df,df_sub,on='eid')
        return new_df
    
    def confounders_gen(self, more_vars = []):
        # creates a dictionary of conventional confounding variables
        # more can be added through the 'more_vars' input 
        # output = dictionary with dfs, 1 df per variable
        # output dfs need to be further processed before analysis

        conf_names = ['Body mass index (BMI)','Age when attended assessment centre','Ethnic background','Sex']
        # Convert single argument to list
        # This because len(string) > 1
        if isinstance(more_vars, basestring):
            more_vars = [more_vars]
            
        # Add optional extras to confound list
        for items in more_vars:
            conf_names.append(items)
            
        # Create dictionary of variable values and names
        df_new = {}
        for var in conf_names:
            tmp = self.extract_variable(variable=var)
            tmp = self.rename_columns(df=tmp,key=var)
            df_new[var] = tmp
            
        return df_new,conf_names
        
    
    def rename_conf(self, df=None):
        # rename columns of confounders df with sensible stuff
        names_in = df.columns.tolist()
        names_out = []
        for n in names_in:
            b,k,a = n.partition('_')
            res=re.search('\((.*?)\)',str(b)) # search for abbrev in brackets
            if not res is None:
                s = res.group(1)
            else: #fill spaces
                res = [m.start() for m in re.finditer(' ', b)]
                s = list(b)
                if len(res):
                    for tmp in res:
                        s[tmp] = '_'
                s = "".join(s)
            names_out.append(s)
        df.columns = names_out
        return df,names_out

    
    def df_mean(self, df=None,key=None):
        # returns mean of data values excluding eid
        cols = self.get_cols_names(df=df)
        new_df = pd.DataFrame(columns=['eid',key])
        new_df['eid'] = df['eid']
        new_df[key] = df[cols[1::]].mean(axis=1)
        return new_df
    
    def vars_by_visits(self, col_names=None,visit=0):
        # returns variables names associated with initial assessment (0), 1st (1) and 2nd (2) re-visit
        # 1st (1) and 2nd (2) re-visit
        V1 =[]
        for var in col_names:
            # \d match any decimal digit
            # . match any character
            # * match previous character 0 or more times
            # + matches one or more times
            # ? matches zero or one time
            # Matches things like 'something-X.Y or 'something-X_Y'
            # Where X == visit
            res = re.search('(.*?)-'+str(visit)+'.(\d+)',var)
            if not res is None:
                V1.append(res.group(0))
        return V1
    

    def rename_columns(self, df=None,key=None,option_str=True):
        # rename the columns of a data frame with something sensible
        col_names = df.columns.tolist()
        col_new = ['eid']
        for k in range(3):
            V0 = self.vars_by_visits(col_names,k)
            for v in V0:
                b,k,a = v.partition('-')
                if option_str:
                    col_new.append(key+'_'+a)
                else:
                    col_new.append(key)
        df_new = pd.DataFrame(columns=col_new)
        for c in range(len(col_new)):
            df_new[col_new[c]] = df[col_names[c]]
        return df_new
        
    def find_DataCoding(self, variable=None):
        ### extract fields 
        soup = self.soup
        allrows = soup.findAll('tr')
        ## search variable string for shitty characters
        symbols = BiobankRead.special_char
        
        # DOES THIS WORK THE SAME AS THE NEXT SECTION?        
        varlist = list(variable)
        lvarlist = len(varlist)
        newvar = []
        for v in range(0, lvarlist):
            if varlist[v] in symbols:
                newvar.extend(['\\', varlist[v]])
            else:
                newvar.extend([varlist[v]])
        variable = ''.join(newvar)
        
        '''
        is_symbol = False
        where =[]
        for x in symbols:
            t = variable.find(x)
            if t >-1:
                is_symbol = True
                where.append(t)
        if is_symbol:
            new_var = ""
            for i in variable:
                lim = variable.index(i)            
                if lim in where:
                    i= "\%s" % (variable[lim])
                new_var += i
            variable = new_var
        '''
        
        ##
        userrows = [t for t in allrows if re.search('>'+variable+'<',str(t))]
        row_str = str(userrows[0])
        foo = row_str.find('Uses data-coding')
        if foo is None:
            print 'No data coding associated with this variable'
            return None
        test = re.search('coding <a href=\"(.?)*\">',row_str)
        res = test.group(0)
        x,y,z=res.partition('href="')
        link,y,u=z.partition('">')
        response = urllib2.urlopen(link)
        html = response.read()
        soup = bs4.BeautifulSoup(html,'html.parser')
        allrows = soup.findAll('tr')
        rows_again = [t for t in allrows if re.search('class=\"int\">(.?)*</td><td class=\"txt\">(.?)*</td>',str(t))]
        schema = pd.DataFrame(columns=['key','value'])
        u = 0
        for item in rows_again:
            item = str(item)
            x,y,z = item.partition('</td><td class="txt">')
            xx,xy,xz = x.partition('<td class="int">') # number key
            zx,zy,zz = z.partition('</td>') # value 
            schema.loc[u] = [xz,zx]
            u += 1
        return schema
        
    def re_wildcard(self, strs=None):
        # inserts a regex wildcard between two keywords
        if not type(strs) is list:
            print 'Input not a list'
            return None
        n = len(strs)
        if n < 2:
            print 'Not enough words to collate'
            return None
        res = strs[0]
        for word in strs[1::]:
            res = res+'(.?)*'+word
        return res
        
    def Datacoding_match(self, df=None,key=None,name=None):
        # find key din df with known data coding
        # find datacoding with find_DataCoding() before using this funct.
        if type(key) == str:
            key = int(key)
        cols = self.get_cols_names(df)
        # remove eids
        cols = cols[1::]
        new_df = pd.DataFrame(columns=cols)
        new_df['eid'] = df['eid']
        for col in cols:
            res_tmp1 =[ x==key for x in df[col]]
            new_df[col]=res_tmp1
        new_df2 = pd.DataFrame(columns=['eid',name])
        new_df2[name] = new_df[cols].sum(axis=1)
        new_df2['eid'] = df['eid']
        return new_df2
        
    def remove_outliers(self, df=None,cols=None,lim=4,one_sided=False):
        # remove outliers from data frame, for each variable
        # cols= specify which variables
        # lim = how many std away
        # one_sided: trim both small/large values, or only large varlues
        if cols is None:
            cols = df.columns
            cols = cols[1::] # remove eids
        new_Df = df
        for var in cols:
            if not one_sided:
                new_Df=new_Df[((new_Df[var]-new_Df[var].mean())/new_Df[var].std()).abs()<lim]
            else:
                new_Df=new_Df[((new_Df[var]-new_Df[var].mean())/new_Df[var].std())<lim]
        return new_Df
    
###################################################################################
 ################## HES data extraction + manipulation ##############################
###################################################################################
     
    def HES_tsv_read(self,filename=None,var='All',n=None):
        ## opens HES file, usually in the form of a .tsv file
        ## outputs a pandas dataframe
        everything_HES = pd.read_csv(filename,delimiter='\t',nrows=n)
        #everything_HES=everything_HES.set_index('eid')
        if var == 'All':    
            return everything_HES
        else:
           sub_HES = everything_HES[var]
           return sub_HES

    def find_ICD10_codes(self,select=None):
        ## extract ICD10 codes from a large, complete dictionary of ICD10 codes
        ##          of all diseases known to medicine
        ## input: select - general code for one class of deseases
        ## output: icd10 - codes of all deseases associated with class
        tmp = self.HES_tsv_read(self.DATA_PATH)
        codes_all = tmp['coding']
        icd10 = []
        for categ in select:
            Ns = [categ in x for x in codes_all]
            tmp = codes_all[Ns]
            for y in tmp:
                icd10.append(y)
        icd10 = [x for x in icd10 if 'Block' not in x]
        return icd10
        
    def find_ICD9_codes(self,select=None):
        ## extract ICD9 codes from a large, complete dictionary of ICD9 codes
        ##          of all diseases known to medicine
        ## input: select - general code for one class of deseases
        ## output: icd9 - codes of all deseases associated with class
        tmp = pd.read_csv(self.DATA_PATH_2)
        codes_all = tmp['DIAGNOSIS CODE']
        icd9 = []
        for categ in select:
            Ns = [str(categ) in str(y)[0:len(str(categ))] for y in codes_all]
            tmp = codes_all[Ns]
            for y in tmp:
                icd9.append(y)
        return icd9
    
    ##### example: ICD10 codes associated with Cardiovasculas incidents
        ### input: desease classes I2, I6, I7 and G4
        ### t=['I2','I7','I6','G4']
        ### codes_icd10 = find_ICD10_codes(t)
         
    def HES_code_match(self,df=None,cols=None,icds=None,which='ICD10'):
        # find input ICDs & OPCS codes in specified columns from input HES data frame
        # USe only on'HES' extrated directly from HES.tsv file
        # which: 'diagnosis', 'oper4' or 'diag_icd9'
        if type(icds) is pd.core.series.Series:
            icds = icds.tolist()
            icds = [x for x in icds if str(x) != 'nan']
        if cols is None:
            cols = df.columns.tolist()
        # remove eids
        cols = cols[1::]
        if which == 'ICD10':
            icd = 'diag_icd10'
        elif which == 'OPCS':
            icd = 'oper4'
        elif which == 'ICD9':
            icd = 'diag_icd9'
        else:
            raise Exception('Option "which" mis-specififed')
        new_df = pd.DataFrame(columns=cols)
        new_df['eid'] = df['eid']
        df_mini = df[icd].tolist()
        #print df_mini
        res_tmp =[ x in icds for x in df_mini]
        new_df_2 = df[res_tmp]
        return new_df_2
            
        
    def OPCS_code_match(self,df=None,icds=None):
        # find input OPCS codes in input HES data frame
        HES_10 = self.HES_code_match(df,icds,which='OPCS')
        return HES_10
        
    def SR_code_match(self,df=None,cols=None,icds=None):
        # find input SR desease codes in specified columns from input dataframe
        # type = (self reported)
        # insert disease codes as numbers not as strings! ex: 1095, not '1095'
        df = df.fillna(value=0) # replace nan by a non-disease code
        if type(icds) is pd.core.series.Series:
            icds = icds.tolist()
        icds = [int(x) for x in icds if str(x) != 'nan']
        if cols is None:
            cols = df.columns.tolist()
            # remove eids
            cols = cols[1::]
        new_df = pd.DataFrame(columns=cols)
        new_df['eid'] = df['eid']
        df = df.replace(np.nan,' ', regex=True)
        for col in cols:
            res_tmp1 =[ x in icds for x in df[col]]
            new_df[col]=res_tmp1
        new_df2 = pd.DataFrame(columns=['eid','SR_res'])
        new_df2['SR_res'] = new_df[cols].sum(axis=1)
        new_df2['eid'] = df['eid']
        return new_df2
        
    def ICD_code_match(self,df=None,cols=None,icds=None):
        # find input ICD desease codes in input 'Mortality' dataframe'
        df = df.fillna(value=0) # replace nan by a non-disease code
        if type(icds) is pd.core.series.Series:
            icds = icds.tolist()
        icds = [x for x in icds if str(x) != 'nan']
        if cols is None:
            cols = df.columns.tolist()
            # remove eids
            cols = cols[1::]
        new_df = pd.DataFrame(columns=cols)
        new_df['eid'] = df['eid']
        df = df.replace(np.nan,' ', regex=True)
        for col in cols:
            res_tmp1 =[ x in icds for x in df[col]]
            new_df[col]=res_tmp1
        new_df2 = pd.DataFrame(columns=['eid','ICD_res'])
        new_df2['ICD_res'] = new_df[cols].sum(axis=1)
        new_df2['eid'] = df['eid']
        return new_df2
      
    def HES_first_time(self,df=None):
        # finds the earliest admission date in HES data for each subject
        #   df should be HES file dataframe outout from "HES_code_match"
        eids_unique = df['eid'].tolist()
        eids_unique = list(set(eids_unique))
        #cols = get_cols_names(df)
        new_Df = pd.DataFrame(columns=['eid','first_admidate'])
       #new_Df['eid']=df['eid']
        res = []
        for ee in eids_unique:
            tmp =  df[df['eid']==ee]
            res.append(len(tmp))
            #tmp['admidate'] = pd.to_datetime(tmp['admidate'])
            x = tmp['admidate'].replace(np.nan,self.end_follow_up).min()
            df2=pd.DataFrame([[ee,x]],columns=['eid','first_admidate'])
            new_Df=new_Df.append(df2)#,ignore_index=True)
        return new_Df
        
    def HES_after_assess(self,df=None,assess_dates=None):
        # returns boolean : subject had HES records after baseline
        # input dates needs to come from HES_first_time()
        #   df should be HES file dataframe
        eids = assess_dates['eid'].tolist()
        DF = pd.DataFrame(columns=['eid','After','date_aft'])
        for ee in eids:
            tmp =  df[df.index==ee]
            tmp_ass_date = assess_dates[assess_dates['eid']==ee]
            tmp_ass_date=tmp_ass_date['assess_date'].iloc[0]
            tmp2= tmp[tmp['admidate']>tmp_ass_date]
            if len(tmp2)>0:
                oo = 1
                #tmp2['admidate'] = pd.to_datetime(tmp2['admidate'])
                x = tmp2['admidate'].replace(np.nan,self.end_follow_up).min()
            else:
                oo = 0
                x = np.nan
            df2 = pd.DataFrame([[ee,oo,x]],columns=['eid','After','date_aft'])
            DF = DF.append(df2)
        return DF
        
    def HES_before_assess(self,dates=None):
        # returns boolean : subject had HES records before baseline
        # input dates needs to come from HES_first_time()
        DF = pd.DataFrame(columns=['eid','Before'])
        DF['eid'] = dates['eid']
        assess_date = dates['assess_date'].tolist()
        res=[a>b for (a,b) in zip(assess_date,dates['first_admidate'].tolist())]
        DF['Before'] = res
        return DF
    
        
    def search_in_list(self,ls=None,key=None):
        #search keyword in list
        return [x for x in ls if re.search(key,str(x))]
