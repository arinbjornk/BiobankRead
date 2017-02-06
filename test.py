# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 17:29:32 2017

@author: Deborah
"""

import __builtin__

##global IDmain
##global IDsub
__builtin__.namehtml='D:\\Uk Biobank\\Application 10035\\R8546\\ukb8546.html'
__builtin__.namecsv='D:\\Uk Biobank\\Application 10035\\R8546\\ukb8546.csv'
__builtin__.N = 502641  
import pandas as pd
import sys
import imp
sys.path.append('C:\Users\Deborah\Google Drive\Postdoc\python\BiobankRead\\')
import BiobankRead2
imp.reload(BiobankRead2)

#Find out what variables are included in the selected project
All_vars = BiobankRead2.Vars

# Is there data on Alcohol intake, for ex. ?
Alc = BiobankRead2.search_in_list(ls=BiobankRead2.Vars,key='Alcohol')
Alc_var = BiobankRead2.extract_variable(Alc[2],n_subjects=N)
Alc_var = BiobankRead2.rename_columns(Alc_var,Alc[2])

# put all the alcohol variables in one df
Alc_var_all  = BiobankRead2.extract_many_vars(Alc,N,baseline_only=False)

# compute average over each visit
# BP data more interesting for this 
BP = BiobankRead2.search_in_list(ls=BiobankRead2.Vars,key='blood pressure')
BP = [x for x in BP if 'automated' in x]
BP_var  = BiobankRead2.extract_many_vars(BP,N,baseline_only=False)
BP_aver  = BiobankRead2.Mean_per_visit(df=BP_var,dropnan=True)
BP_aver.describe()

