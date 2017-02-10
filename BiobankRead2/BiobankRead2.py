# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 12:24:41 2017

@author: Deborah
"""

import pandas as pd
import bs4 #beautifulsoup4 package
import re # RegEx 
import urllib2
import numpy as np
import os


html_file = namehtml
csv_file = namecsv

if not isinstance(html_file,str) & isinstance(csv_file,str):
    raise NameError('files location misspecified')
    
if not  os.path.isabs(html_file) &  os.path.isabs(csv_file):
     raise ValueError('file location incorrectly specified')

def special_char():
    # needed to handle some funny variable names
    return "~`!@#$%^&*()_-+={}[]:>;',</?*-+"
    
def makeSoup():
    f =  open(html_file,'r').read()
    soup = bs4.BeautifulSoup(f,'html.parser')
    return soup
    
Global_soup = makeSoup()

def search_in_list(ls=None,key=None):
    #search keyword in list
    return [x for x in ls if re.search(key,str(x))]

def All_variables():
    soup = Global_soup
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

def GetEIDs(n_subjects = 1000):
    # data frame of EIDs
    filename = csv_file
    EIDs = pd.read_csv(filename,usecols=['eid'],nrows=n_subjects)
    return EIDs
    
Eids_all = GetEIDs(n_subjects=N)
    

def extract_variable(variable=None,
                     n_subjects = 1000,
                     baseline_only=False):
    filename = csv_file
    ### extract fields 
    soup =Global_soup
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
    my_range = []
    #for name in var_names:
    my_range = Sub_list[var_names]
    my_range.append('eid') # Encoded anonymised participant ID
    everything = pd.read_csv(filename,usecols=my_range,nrows=n_subjects)#na_filter=False)
        # drop columns of data not collected at baseline 
    if baseline_only:
        cols = everything.columns
        keep = ['-0.' in x for x in cols]
        keep[0] = True # always keep eid column
        everything= everything[cols[keep]]
    return everything
    
def Get_ass_dates(n_subjects = 1000):
    # data frame of EIDs
    var = 'Date of attending assessment centre'
    Ds = extract_variable(var,n_subjects)
    return Ds
    
assess_dates = Get_ass_dates(n_subjects=N)
    
def codes_categories(data_coding=6):
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
 
Vars = All_variables()
   
def all_related_vars(keyword=None,n_subjects=1000,dropNaN=True):
    stuff = [t for t in Vars if re.search(keyword[1::],t)]#t.find(keyword[1::]) > -1]
    if len(stuff) >1:
        stuff_var = {}
        for var in stuff:
            DBP, DBP_names = extract_variable(var,n_subjects)
            if dropNaN:
            # drop subjects with no reported illness
                tmp = list(DBP.columns.values)
                DBP = DBP[np.isfinite(DBP[tmp[1]])]    
            stuff_var[var] = DBP
    else:
       #print stuff[0]
       stuff_var = extract_variable(stuff[0],n_subjects)
       stuff_var = stuff_var[0]
       tmp = list(stuff_var.columns.values)
       if dropNaN:
           stuff_var = stuff_var[np.isfinite(stuff_var[tmp[1]])]  
    return stuff_var, stuff
    
def extract_many_vars(keywords=None,n_subjects=1000,
                      dropNaN=False,spaces=False,baseline_only=False):
    # extract variables for several pre-specified var. names 
    # returns one single df with eids and each variables as columns
    if len(keywords) >1:
        main_Df = pd.DataFrame(columns =['eid'])
        main_Df['eid'] = Eids_all['eid']
        for var in keywords:
            DBP = extract_variable(var,n_subjects)
            if spaces:
                b,k,a = var.partition(' ')
                var = b
            DBP = rename_columns(DBP,var)
            if dropNaN:
            # drop subjects with no reported illness
                tmp = list(DBP.columns.values)
                DBP = DBP[np.isfinite(DBP[tmp[1]])]    
            main_Df = pd.merge(main_Df,DBP,on='eid',how='outer')
    else:
       #print stuff[0]
       main_Df = extract_variable(keywords[0],n_subjects,baseline_only)
       tmp = list(main_Df.columns.values)
       if dropNaN:
           main_Df = main_Df[np.isfinite(main_Df[tmp[1]])]
    return main_Df

def Mean_per_visit(df=None,dropnan=False):
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
    
def confounders_gen(more_vars = [],
                    n_subjects=1000):
    # creates a dictionary of conventional confounding variables
    # more can be added through the 'more_vars' input 
    # output = dictionary with dfs, 1 df per variable
    # output dfs need to be further processed before analysis
    conf_names = ['Body mass index (BMI)','Age when attended assessment centre','Ethnic background','Sex']
    if len(more_vars)>0:
        if len(more_vars)>1:
            for items in more_vars:
                conf_names.append(items)
        else:
            conf_names.append(more_vars[0])
    df_new = {}
    #print conf_names
    for var in conf_names:
        tmp = extract_variable(var,n_subjects)
        tmp = rename_columns(df=tmp,key=var)
        df_new[var] = tmp
    return df_new,conf_names
    
def find_Age(df=None):
    # find age of subjects based on Year(assessment)-Year(birth)
    # input = df with "Year of birth"
        Ass_dates = Get_ass_dates(n_subjects=N)
        Ass_dates = Ass_dates[Ass_dates.columns[0:2]]
        Ass_dates['Ass_yr']=[float(x[0:4]) for x in Ass_dates[Ass_dates.columns[1]]]
        df= pd.merge(df,Ass_dates[['eid','Ass_yr']],on='eid',how='outer')
        df[df.columns[1]] = [float(x) for x in df[df.columns[1]]]
        df['Age'] = (df['Ass_yr']-df[df.columns[1]])
        return df
    
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
    
def find_DataCoding(variable=None):
    ### extract fields 
    soup = Global_soup
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
    
def Datacoding_match(df=None,key=None,name=None):
    # find key din df with known data coding
    # find datacoding with find_DataCoding() before using this funct.
    if type(key) == str:
        key = int(key)
    cols = get_cols_names(df)
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
    
def remove_outliers(df=None,cols=None,lim=4,one_sided=False):
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

this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "data", "ICD10_UKB.tsv")

     
def HES_tsv_read(filename=None,var='All',n=None):
    ## opens HES file, usually in the form of a .tsv file
    ## outputs a pandas dataframe
    everything_HES = pd.read_csv(filename,delimiter='\t',nrows=n)
    #everything_HES=everything_HES.set_index('eid')
    if var == 'All':    
        return everything_HES
    else:
       sub_HES = everything_HES[var]
       return sub_HES
        
def find_ICD10_codes(select=None):
    ## extract ICD10 codes from a large, complete dictionary of ICD10 codes
    ##          of all deseases known to medicine
    ## input: select - general code for one class of deseases
    ## output: icd10 - codes of all deseases associated with class
    tmp = HES_tsv_read(DATA_PATH)
    codes_all = tmp['coding']
    icd10 = []
    for categ in select:
        Ns = [categ in x for x in codes_all]
        tmp = codes_all[Ns]
        for y in tmp:
            icd10.append(y)
    icd10 = [x for x in icd10 if 'Block' not in x]
    return icd10
    
##### example: ICD10 codes associated with Cardiovasculas incidents
    ### input: desease classes I2, I6, I7 and G4
    ### t=['I2','I7','I6','G4']
    ### codes_icd10 = find_ICD10_codes(t)
     
def HES_code_match(df=None,cols=None,icds=None,which='diagnosis'):
    # find input ICD10 codes in specified columns from input df
    # USe only on'HES' extrated directly from HES.tsv file
    # opt= ALL of cvd_only
    if type(icds) is pd.core.series.Series:
        icds = icds.tolist()
        icds = [x for x in icds if str(x) != 'nan']
    if cols is None:
        cols = get_cols_names(df)
    # remove eids
    cols = cols[1::]
    if which == 'diagnosis':
        icd = 'diag_icd10'
    elif which == 'opcs':
        icd = 'oper4'
    else:
        icd = 'diag_icd9'
    new_df = pd.DataFrame(columns=cols)
    new_df['eid'] = df['eid']
    df_mini = df[icd].tolist()
    #print df_mini
    res_tmp =[ x in icds for x in df_mini]
    new_df_2 = df[res_tmp]
    return new_df_2
  
def HES_first_time(df=None):
    # finds the earliest admission date in HES data for each subject
    #   df should be HES file dataframe outout from "HES_code_match"
    eids_unique = df.index.tolist()
    eids_unique = list(set(eids_unique))
    #cols = get_cols_names(df)
    new_Df = pd.DataFrame(columns=['eid','first_admidate'])
   #new_Df['eid']=df['eid']
    res = []
    for ee in eids_unique:
        tmp =  df[df.index==ee]
        res.append(len(tmp))
        x = tmp['admidate'].min()
        df2=pd.DataFrame([[ee,x]],columns=['eid','first_admidate'])
        new_Df=new_Df.append(df2,ignore_index=True)
    return new_Df
    
def HES_after_assess(df=None,assess_dates=None):
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
            oo = True
            x = tmp2['admidate'].min()
        else:
            oo = False
            x = 0
        df2 = pd.DataFrame([[ee,oo,x]],columns=['eid','After','date_aft'])
        DF = DF.append(df2)
    return DF
    
def HES_before_assess(dates=None):
    # returns boolean : subject had HES records before baseline
    # input dates needs to come from HES_first_time()
    DF = pd.DataFrame(columns=['eid','Before'])
    DF['eid'] = dates['eid']
    assess_date = dates['assess_date'].tolist()
    res=[a>b for (a,b) in zip(assess_date,dates['first_admidate'].tolist())]
    DF['Before'] = res
    return DF

    
    
    
        
    
    
        
        
    
    
