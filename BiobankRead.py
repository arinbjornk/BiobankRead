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
from datetime import datetime

projectID=IDmain
studyID=IDsub

def convert_to_str(projectID,studyID):
    if isinstance(projectID,int):
        projectID = str(projectID)
    if isinstance(studyID,int):
        studyID= str(studyID)
    return projectID,studyID
    
projectID,studyID=convert_to_str(projectID,studyID)
    
def files_path(x=None,y=None,opt='html'):
    #x = project ID
    #y = study ID
    #opt = html or csv
    return 'D:\Uk Biobank\Application '+x+'\R'+y+'\ukb'+y+'.'+opt
   
html_file = files_path(x=projectID,y=studyID)
    
def makeSoup():
    f =  open(html_file,'r').read()
    soup = bs4.BeautifulSoup(f,'html.parser')
    return soup
    
Global_soup = makeSoup()

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
    filename = files_path(x=projectID,y=studyID,opt='csv')
    EIDs = pd.read_csv(filename,usecols=['eid'],nrows=n_subjects)
    return EIDs
    
Eids_all = GetEIDs(n_subjects=N)
    
def Get_ass_dates(n_subjects = 1000):
    # data frame of EIDs
    var = 'Date of attending assessment centre'
    Ds = extract_variable(var,n_subjects)
    return Ds

def extract_variable(variable=None,
                     n_subjects = 1000):
    filename = files_path(x=projectID,y=studyID,opt='csv')
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
    return df_dict
    
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
       stuff_var = extract_variable(projectID,studyID,stuff[0],n_subjects)
       stuff_var = stuff_var[0]
       tmp = list(stuff_var.columns.values)
       if dropNaN:
           stuff_var = stuff_var[np.isfinite(stuff_var[tmp[1]])]  
    return stuff_var, stuff
    
def extract_many_vars(keywords=None,n_subjects=1000,dropNaN=False,spaces=False,baseline_only=False):
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
       main_Df = extract_variable(projectID,studyID,keywords[0],n_subjects)
       tmp = list(main_Df.columns.values)
       if dropNaN:
           main_Df = main_Df[np.isfinite(main_Df[tmp[1]])]
    # drop columns of data not collected at baseline 
    if baseline_only:
        cols = main_Df.columns
        keep = ['_0.' in x for x in cols]
        keep[0] = True # always keep eid column
        main_Df = main_Df[cols[keep]]
    return main_Df

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
    
def confounders_gen(more_vars = [],
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
        tmp = extract_variable(var,n_subjects)
        if var == 'Year of birth': # substract from 2016 to get Age
            now = datetime.now()
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
    
def METhday(df=None):
    # computes METh/day according to Guo et al 2015
    # df input needs to be structured as: 
    #'eid','walk','walk-dur','moderate','moderate-dur','vigorous','vigorous-dur'
    cols = df.columns[1::]
    multipliers = [2.3,3,7]
    df_t = pd.DataFrame(columns=['eid'])
    df_t['eid']=df['eid']
    r = [0,2,4]
    v=0
    for i in r:
        var = df[cols[i]]
        dur = df[cols[i+1]]
        # remove negative values
        dur = [np.nan if x in [-3,-1] else x for x in dur]
        var = [np.nan if x in [-3,-1] else x for x in var]
        var = [0 if x == -2 else x for x in var]
        dur = np.asarray(dur)
        var = np.asarray(var)
        vd = var*dur
        vd = multipliers[v]*vd/60
        df_t[cols[i]] = vd
        v +=1
    df_t['METhday'] = df_t[df_t.columns[1::]].sum(axis=1)
    tmp= df_t['vigorous']/df_t['METhday']
    df_t['VtT_PA'] = tmp #[0 if x !=x else x for x in tmp]
    df_t = df_t[['eid','METhday','VtT_PA']]
    return df_t 
    
def urine_Kawasaki(df=None,target='Sodium'):
    # calculates 24h estimate from spot Na/Potassium secretion in urine
    # df should be: ['eid','age','weight','height','sex','Sodium','Potassium','Creatinine']
    # target = sodium or potassium
    coeff = np.zeros(shape=(2,4))
    coeff[0,:] = [-12.63,15.12,7.39,-79.9] # women
    coeff[1,:] =[-4.72,8.58,5.09,-74.5] # men
    target_df = df[target]
    Cr = df['Creatinine']
    df_new = pd.DataFrame(columns=['eid'])
    df_new['eid'] = df['eid']
    df_tmp = pd.DataFrame(columns=['eid'])
    df_tmp['eid'] = df['eid']
    for i in range(2):
        tmp_df = df[df['sex']==i]
        sub_coeff = coeff[i,:]
        predicted = sub_coeff[0]*tmp_df['age']+sub_coeff[1]*tmp_df['weight']+sub_coeff[2]*tmp_df['height']+sub_coeff[3]
        res = 16.3*np.sqrt(target_df/Cr)*predicted
        df_tmp[str(i)]=res
    df_new['24h_'+target] = df_tmp[df_tmp.columns[1::]].sum(axis=1)
    return df_new
    
 
 ################## HES data extraction + manipulation ##############################
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
    if option=='icd9':
        filename = CVD_files(types='ICD9',what='stroke')
    if option=='death':
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
        tmp = df[type].tolist()
        res = [str(x) for x in tmp if str(x) != 'nan']
        return res
        
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
        tmp = df[type].tolist()
        res = [str(x) for x in tmp if str(x) != 'nan']
        res2 = [('%s' % x).rstrip('0').rstrip('.') for x in res]
        return res2
   
# define global variable
def generate_codes(options):
    if options == "All":
       ## codes - all CVD
        codes_icd10 = ICD10_CVD(option='diagnosis')
        codes_icd9 = ICD10_CVD(option='icd9')
        codes_icd9=[('%s' % x).rstrip('0').rstrip('.') for x in codes_icd9] #remove superfluous decimal precision
        codes_OPCS = ICD10_CVD(option='OPCS')
        codes_SR = selfreported_CVD(option='diagnosis')
        codes_Death = ICD10_CVD(option='death')
        final_str="CVD"
    else:
       ## codes - CAD, PAD or stroke only 
        codes_icd10 = ICD10_CVD(option='diagnosis',type=options,stack=False)
        codes_icd9 = ICD10_CVD(option='icd9',type=options,stack=True)
        codes_icd9=[('%s' % x).rstrip('0').rstrip('.') for x in codes_icd9] #remove superfluous decimal precision
        codes_OPCS = ICD10_CVD(option='OPCS',type=options,stack=False)
        codes_SR = selfreported_CVD(option='diagnosis',type=options,stack=False)
        codes_Death = ICD10_CVD(option='death',type=options,stack=False)
        final_str=options
    return codes_icd10,codes_icd9,codes_OPCS,codes_SR,codes_Death,final_str
    
codes_icd10,codes_icd9,codes_OPCS,codes_SR,codes_Death,final_str = generate_codes(options)
    
def ICD10_match(df=None,cols=None,icds=codes_icd10):
    # find input ICD10 codes in specified columns from input dataframe
    # type = 'HES'
    #df = df.fillna(value='A000') # replace nan by a non-disease code
    if type(icds) is pd.core.series.Series:
        icds = icds.tolist()
        icds = [x for x in icds if str(x) != 'nan']
    if cols is None:
        cols = get_cols_names(df)
        # remove eids
        cols = cols[1::]
    new_df = pd.DataFrame(columns=cols)
    new_df['eid'] = df['eid']
    df = df.replace(np.nan,' ', regex=True)
    for col in cols:
         res_1 = [x in icds for x in df[col]]
         new_df[col]=res_1
    return new_df
''' res = [icds[0] in y for y in df[col]]
z = z+sum(res)
for i in range(1,len(icds)):
 print icds[i]
 tmp = [icds[i] in y for y in df[col]]
 print sum(tmp)
 z = z+sum(tmp)
 res = [sum(x) for x in zip(res,tmp)]
res_1 = [x>0 for x in res]'''
       # print z
    
def code_match_HES(df=None,cols=None,icds=None,opt='All',which='diagnosis'):
    # find input ICD10 codes in specified columns from input Series
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
    if opt == 'All':
        new_df[cols] = res_tmp
        return new_df
    else:
        new_df_2 = df[res_tmp]
        return new_df_2
        
def CVD_type_match_HES(df=None,cols=None,icds=codes_icd10,icd_old=codes_icd9,opcs=codes_OPCS):
    # find input ICD10 & OPCS codes in specified columns from input Series
    # USe only on'HES' extrated directly from HES.tsv file
    if type(icds) is pd.core.series.Series:
        icds = icds.tolist()
        icds = [x for x in icds if str(x) != 'nan']
    if type(opcs) is pd.core.series.Series:
        opcs = opcs.tolist()
        opcs = [x for x in opcs if str(x) != 'nan']  
    if type(icd_old) is pd.core.series.Series:
        icd_old = icd_old.tolist()
        icd_old = [x for x in icd_old if str(x) != 'nan'] 
    if cols is None:
        cols = get_cols_names(df)
    cols = cols[1::]     # remove eids
    new_df = pd.DataFrame(columns=cols)
    new_df['eid'] = df['eid']
    #'diagnosis' part
    icd = 'diag_icd10'
    df_mini1 = df[icd].tolist()
    res_tmp1 =[ x in icds for x in df_mini1]
    # icd9 diagnosis part
    icd = 'diag_icd9'
    df_mini2 = df[icd].tolist()
    res_tmp2 =[ x in icd_old for x in df_mini2]
    # opertaion part
    icd = 'oper4'
    df_mini3 = df[icd].tolist()
    res_tmp3 =[ x in opcs for x in df_mini3]
    #print len(res_tmp2)
    ## union of the 2
    res_tmp = [max(x,y,z) for (x,y,z) in zip(res_tmp1,res_tmp2,res_tmp3)]
    new_df_2 = df[res_tmp]
    return new_df_2
    
def CVD_match_HES(df=None,cols=None):
    cats = ['CAD','PAD','stroke']
    df_new = pd.DataFrame(columns=['eid'])
    df_new['eid'] = Eids_all['eid']
    df_new2 = pd.DataFrame(columns=['eid'])
    df_new2['eid'] = df['eid']
    for c in cats:
        codes_icd10,codes_icd9,codes_OPCS,codes_SR,codes_Death,final_str = generate_codes(c)
        tmp_df = CVD_type_match_HES(df,cols,icds=codes_icd10,icd_old=codes_icd9,opcs=codes_OPCS)
        #discart missing values in admission date
        tmp_df=tmp_df.dropna(subset=['admidate'])
        #get unique eids for subjects with CVD HES records
        eids_CVD = tmp_df['eid'].tolist()
        eids_CVD = list(set(eids_CVD))
        df_new[c] = [e in eids_CVD for e in Eids_all['eid']]
        # keep admission dates
        df_new2[c] = tmp_df['admidate']
    df_new['CVD']=df_new[['CAD','PAD','stroke']].sum(axis=1)
    df_new2 = df_new2.dropna(how='all',axis=0,subset=df_new2.columns[1::])
    return df_new,df_new2
    
    
    
def SR_match(df=None,cols=None,icds=codes_SR):
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
    new_df = pd.DataFrame(columns=cols)
    new_df['eid'] = df['eid']
    df = df.replace(np.nan,' ', regex=True)
    for col in cols:
        res_tmp1 =[ x in icds for x in df[col]]
        new_df[col]=res_tmp1
    new_df2 = pd.DataFrame(columns=['eid','SR_CVD'])
    new_df2['SR_CVD'] = new_df[cols].sum(axis=1)
    new_df2['eid'] = df['eid']
    return new_df2
        
def search_in_list(ls=None,key=None):
    #search keyword in list
    return [x for x in ls if re.search(key,str(x))]
    
def HES_tsv_read(filename=None,var='All',n=None):
    everything_HES = pd.read_csv(filename,delimiter='\t',nrows=n)
    #everything_HES=everything_HES.set_index('eid')
    if var == 'All':    
        return everything_HES
    else:
       sub_HES = everything_HES[var]
       return sub_HES
       
def HES_remove_Duplicates(df=None,which='First'):
    # which: which incidents to keep
    # first: first ever HES record, else: most recent HES record
    eids = df['eid'].tolist()
    cols = get_cols_names(df)
    new_Df = pd.DataFrame(columns=cols)
    eids = list(set(eids)) # remove duplicates
    for ee in eids:
        tmp =  df[df['eid']==ee]
        if len(tmp) > 1:
            if which == 'First':
                x = min(tmp['epistart'])
            else:
                x = max(tmp['epistart'])
            tmp2 = tmp[tmp['epistart']==x]
            new_Df=new_Df.append(tmp2,ignore_index=True)
            #eids = [z for z in eids if z != ee]
        else:
            new_Df=new_Df.append(tmp,ignore_index=True)
    return new_Df
    
'''def HES_baseline(df=None,which='No'):
    biobank_start = datetime(2005,12,31)
    dates = df[['epistart','admidate']] # discrepancies in records
    #dates['epistart'].fillna(dates['admidate'],inplace=True) #fill blanks
    #dates['admidate'].fillna(dates['epistart'],inplace=True) #fill blanks
    admi_date = dates['epistart'].tolist()
    res = []
    for ee in eids:
        tmp =  df[df['eid']==ee]
        if len(tmp) > 1:
    for dates in admi_date:
        if dates >0:
            new_admidate = datetime.strptime(dates, "%Y-%m-%d")
            res.append(new_admidate > biobank_start)
        else:
            res.append(False)
    if which != 'No':
        res = [not r for r in res]
    new_df = df[res]
    return new_df'''
    
def HES_first_time(df=None):
    # finds the earliest admission date in HES data for each subject
    #   df should be HES file dataframe
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
    
def HES_CVD_after_assess(df=None,assess_dates=None):
    # returns boolean : subject had CVD after baseline
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
    
def HES_CVD_before_assess(dates=None):
    # returns boolean : subject had CVD before baseline
    # input dates needs to come from HES_first_time()
    DF = pd.DataFrame(columns=['eid','Before'])
    DF['eid'] = dates['eid']
    assess_date = dates['assess_date'].tolist()
    res=[a>b for (a,b) in zip(assess_date,dates['first_admidate'].tolist())]
    DF['Before'] = res
    return DF

    
    
    
        
    
    
        
        
    
    
