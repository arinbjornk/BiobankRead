# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 15:15:46 2016

@author: Deborah
"""
import pandas as pd
#sys.path.append('C:\Users\Deborah\Google Drive\Postdoc\python')
import bs4 #beautifulsoup4 package
import re # RegEx 
import urllib2
import numpy as np
import datetime

def convert_to_str(projectID,studyID):
    if isinstance(projectID,int):
        projectID = str(projectID)
    if isinstance(studyID,int):
        studyID= str(studyID)
    return projectID,studyID
    
def files_path(x=None,y=None,opt='html'):
    #x = project ID
    #y = study ID
    #opt = html or csv
    return 'D:\Uk Biobank\Application '+x+'\R'+y+'\ukb'+y+'.'+opt
    
    
def makeSoup(projectID=None,
                    studyID=None):
    html_file = files_path(x=projectID,y=studyID)
    f =  open(html_file,'r').read()
    soup = bs4.BeautifulSoup(f,'html.parser')
    return soup

def All_variables(projectID=None,
                    studyID=None):
    projectID,studyID = convert_to_str(projectID,studyID)
    soup = makeSoup(projectID,studyID)
    allrows = soup.findAll('tr')
    res = []
    for t in allrows:
        res1=re.search('</span></td><td rowspan=(.*?)>(.*?)</td></tr>',str(t))
        if not res1 is None:
            res1 = res1.group(0)
            x,y,z = res1.partition('">')
            xx,yy,zz = z.partition('</td></tr>')
            if xx.find('<br>') > -1:
                t = xx.find('<br>')
                xx = xx[0:t]
            res.append(xx)
    return res

def GetEIDs(projectID=None,
            studyID=None,
            n_subjects = 1000):
    # data frame of EIDs
    projectID,studyID = convert_to_str(projectID,studyID)
    filename = files_path(x=projectID,y=studyID,opt='csv')
    EIDs = pd.read_csv(filename,usecols=['eid'],nrows=n_subjects)
    return EIDs

def extract_variable(projectID=None,
                    studyID=None,
                     variable=None,
                     n_subjects = 1000):
    projectID,studyID = convert_to_str(projectID,studyID)
    filename = files_path(x=projectID,y=studyID,opt='csv')
    ### extract fields 
    soup = makeSoup(projectID,studyID)
    allrows = soup.findAll('tr')
    ## search variable string for shitty characters
    symbols = special_char()
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
    ##
    userrows = [t for t in allrows if re.search('>'+variable+'<',str(t))]
    if not userrows:
        userrows = [t for t in allrows if re.search('>'+variable+'.<',str(t))]
    #print userrows
    userrows_str = str(userrows[0])
    #x,y,z=userrows.partition('</span></td><td rowspan=')
   # userrows_str = use
    IDs = [] # extract IDs related to variables
    var_names = [] # extract all variable names 
    #for line in userrows_str:
    match1 = re.search('id=(\d+)',userrows_str)
    if match1:
        IDs.append(match1.group(1))
    '''before,key,after = userrows_str.partition(variable)
    bb,kk,aa = after.partition('<')
    var_names.append(key+bb)'''
    var_names = variable
    ## Retreive all associated columsn with variables names 
    sub_link = 'http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id='
    Sub_list = {}
    for idx in IDs:
        key = []
        x = IDs.index(idx)
        for link in soup.find_all('a', href=sub_link+idx):
            tmp = str(link.contents[0].encode('utf-8'))
            key.append(tmp)
        Sub_list[var_names]=key
    ###
    df_dict = {}
    my_range = []
    #for name in var_names:
    my_range = Sub_list[var_names]
    my_range.append('eid') # Encoded anonymised participant ID
    everything = pd.read_csv(filename,usecols=my_range,nrows=n_subjects)#na_filter=False)
    #everything.dropna(axis=1, how='all', inplace=True)
    #everything.dropna(axis=0, how='all', inplace=True)
    #everything = pd.concat([everything,EIDs])
    df_dict = everything
    return df_dict,var_names
    
def illness_codes_categories(data_coding=6):
    ## Get dictionary of disease codes
    link = 'http://biobank.ctsu.ox.ac.uk/crystal/coding.cgi?id='+str(data_coding)
    response = urllib2.urlopen(link)
    html = response.read()
    soup = bs4.BeautifulSoup(html,'html.parser')
    allrows = soup.findAll('tr')
    ## find all categories of illnesses
    userrows = [t for t in allrows if t.findAll(text='Top')]
    userrows_str =[] # convert to string
    for j in userrows:
        userrows_str.append(str(j))
    Group_codes = []
    Group_names = []
    for line in userrows_str:
            match1 = re.search('class="int">(\d+)',line)
            Group_codes.append(match1.group(1))
            b,k,a = line.partition('</td><td class="txt">No')
            bb,kk,aa = b.partition('"txt">')
            Group_names.append(aa)
    Groups = pd.Series(data=Group_codes,index=Group_names)
    return Groups
    
def all_the_vars_I_want(keyword=None,projectID=None,
                    studyID=None,n_subjects=1000,dropNaN=True):
    # lists of variables 
    Vars = All_variables(projectID,studyID)
    stuff = [t for t in Vars if re.search(keyword[1::],t)]#t.find(keyword[1::]) > -1]
    if len(stuff) >1:
        stuff_var = {}
        for var in stuff:
            DBP, DBP_names = extract_variable(projectID,studyID,var,n_subjects)
            if dropNaN:
            # drop subjects with no reported illness
                tmp = list(DBP.columns.values)
                DBP = DBP[np.isfinite(DBP[tmp[1]])]    
            stuff_var[var] = DBP
    else:
       #print stuff[0]
       stuff_var = extract_variable(projectID,studyID,stuff[0],n_subjects)
       stuff_var = stuff_var[0]
       tmp = list(stuff_var.columns.values)
       if dropNaN:
           stuff_var = stuff_var[np.isfinite(stuff_var[tmp[1]])]  
    return stuff_var, stuff

def BP_aver_visit(df=None,Type='Systolic'):
    # average BP at each visit 
    # Only work with blood pressure data
    Tmp = list(df.columns.values)
    vists_rnd = [1,3,5]
    visits = ['visit-1', 'visit-2', 'visit-3']
    visits = [Type+'_'+v for v in visits]
    cols = visits.append('eid')
    new_df = pd.DataFrame(columns=cols)
    u = 0
    new_df['eid']=df['eid']
    for k in vists_rnd:
        tmp = df[[Tmp[k],Tmp[k+1]]].mean(axis=1)
        new_df[visits[u]] = tmp
        u +=1 
    return new_df
    
def confounders_gen(projectID=None,
                    studyID=None,
                    more_vars = [],
                    n_subjects=1000):
    conf_names = ['Body mass index (BMI)','Year of birth','Ethnic background','Sex']
    if len(more_vars)>0:
        if len(more_vars)>1:
            for items in more_vars:
                conf_names.append(items)
        else:
            conf_names.append(more_vars[0])
    df_new = {}
    #print conf_names
    for var in conf_names:
        tmp,names = extract_variable(projectID,studyID,var,n_subjects)
        if var == 'Year of birth': # substract from 2016 to get Age
            now = datetime.datetime.now()
            this_yr = now.year
            tmp['34-0.0'] -= this_yr
            tmp['34-0.0'] *= -1
            var = 'Age'
        tmp = rename_columns(df=tmp,key=var)
        df_new[var] = tmp
    conf_names.remove('Year of birth')
    conf_names.append('Age')
    return df_new,conf_names
    
def rename_conf(df=None):
    # rename columns of confounders df with sensible stuff
    names_in = get_cols_names(df)
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
    
def special_char():
    # needed to handle some funny variable names
    return "~`!@#$%^&*()_-+={}[]:>;',</?*-+"
    
def get_cols_names(df=None):
    #returns columns names of pandas df in list
    cols = df.columns.values
    Cols = []
    for c in cols:
        Cols.append(c)
    return Cols
    
def df_mean(df=None,key=None):
    # returns mean of data values excluding eid
    cols = get_cols_names(df=df)
    new_df = pd.DataFrame(columns=['eid',key])
    new_df['eid'] = df['eid']
    new_df[key] = df[cols[1::]].mean(axis=1)
    return new_df
    
def vars_by_visits(col_names=None,visit=0):
    # returns variables names associated with initial assessment (0), 1st (1) and 2nd (2) re-visit
    V1 =[]
    for var in col_names:
        res = re.search('(.*?)-'+str(visit)+'.(\d+)',var)
        if not res is None:
            V1.append(res.group(0))
    return V1

def rename_columns(df=None,key=None,option_str=True):
    # rename the columns of a data frame with something sensible
    col_names = get_cols_names(df)
    col_new = ['eid']
    for k in range(3):
        V0 = vars_by_visits(col_names,k)
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
    
def find_DataCoding(projectID=None,
                    studyID=None,
                     variable=None):
    projectID,studyID = convert_to_str(projectID,studyID)
    ### extract fields 
    soup = makeSoup(projectID,studyID)
    allrows = soup.findAll('tr')
    ## search variable string for shitty characters
    symbols = special_char()
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
    
def re_wildcard(strs=None):
    # inserts a regex wildcard between two keywords
    n = len(strs)
    if n < 2:
        print 'Not enough words to collate'
        return None
    if not type(strs) is list:
        print 'Input not a list'
        return None
    res = strs[0]
    for word in strs[1::]:
        res = res+'(.?)*'+word
    return res
    
def ICD10_match(df=None,cols=None,icds=None):
    # find input ICD10 codes in specified columns from input dataframe
    # type = 'HES'
    df = df.fillna(value='A000') # replace nan by a non-disease code
    if type(icds) is pd.core.series.Series:
        icds = icds.tolist()
        icds = [x for x in icds if str(x) != 'nan']
    if cols is None:
        cols = get_cols_names(df)
        # remove eids
        cols = cols[1::]
    new_df = pd.DataFrame(columns=icds)
    new_df['eid'] = df['eid']
    for icd10 in icds:
        temp = [df[loc].str.contains(icd10) for loc in cols]
        temp = np.column_stack(temp)
        res_tmp = np.sum(temp,axis=1)
        new_df[icd10] = res_tmp
    return new_df
    
def SR_match(df=None,cols=None,icds=None):
    # find input SR desease codes in specified columns from input dataframe
    # type = (self reported)
    df = df.fillna(value=0) # replace nan by a non-disease code
    if type(icds) is pd.core.series.Series:
        icds = icds.tolist()
        icds = [x for x in icds if str(x) != 'nan']
    if cols is None:
        cols = get_cols_names(df)
        # remove eids
        cols = cols[1::]
    new_df = pd.DataFrame(columns=icds)
    new_df['eid'] = df['eid']
    for icd10 in icds:
        temp = [df[loc]==icd10 for loc in cols]
        temp = np.column_stack(temp)
        res_tmp = np.sum(temp,axis=1)
        new_df[icd10] = res_tmp
    return new_df
    
def CVD_files(types='ICD10',what='stroke'):
        # types = ICD10 or SR
        # what = stroke of OPCS
    return "D:\Uk Biobank\HES data\\"+what+types+'.csv'
    
def ICD10_CVD(option='diagnosis',type='CAD',stack=True):
    # option 'diagnosis' or 'OPCS' 
    # type 'CAD', 'PAD', 'stroke'
    # returns ICD10 codes for CVD, as classified by EBS team
    if option=='diagnosis':
        filename = CVD_files(types='ICD10',what='stroke')
    if option == 'OPCS':
        filename = CVD_files(types='ICD10',what=option)
    df = pd.read_csv(filename)
    if stack:
        res = []
        for col in df:
            temp = df[col].tolist()
            temp = [str(x) for x in temp if str(x) != 'nan']
            res = np.concatenate((res,temp),axis=0)
        return res.tolist()
    else:
        return df[type]
    
def selfreported_CVD(option='diagnosis',type='CAD',stack=True):
    # option 'diagnosis' or 'OPCS' 
    # type 'CAD', 'PAD', 'stroke'
    # returns ICD10 codes for CVD, as classified by EBS team
    if option=='diagnosis':
        filename = CVD_files(types='SR',what='stroke')
    if option == 'OPCS':
        filename = CVD_files(types='SR',what=option)
    df = pd.read_csv(filename)
    if stack:
        res = []
        for col in df:
            temp = df[col].tolist()
            temp = [str(x) for x in temp if str(x) != 'nan']
            res = np.concatenate((res,temp),axis=0)
        res = res.tolist()
        res2 =[]
        for item in res:
            res2.append(int(float(item))) # messy format changes 
        return res2
    else:
        return df[type]
        
def search_in_list(ls=None,key=None):
    #search keyword in list
    return [x for x in ls if re.search(key,str(x))]
    
        
    
    
        
        
    
    
