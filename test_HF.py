import __builtin__


__builtin__.namehtml=<my_html_file_location>
__builtin__.namecsv=<my_csv_file_location>
__builtin__.n =<n_of_subjects>

### import Biobankread package
import BiobankRead2.BiobankRead2 as UKBr
UKBr = UKBr.BiobankRead()

### optionally import additional packages
import pandas as pd
import numpy as np

### view the list of all variables available in files
All_vars = UKBr.Vars

#### Extract BMI variable
df_BMI = UKBr.extract_variable('Body mass index(BMI)', baseline_only=True) 

#### View Systolic blood pressure (SBP) variables
SBP = UKBr.search_in_list(ls=All_vars,key='Systolic') 

### Extract them in one data frame 
Df_Systolic = UKBr.extract_many_vars(SBP) 

### Take average of automated readings of SBP
Fields = ['Systolic blood pressure, automated reading-0.0',
	'Systolic blood pressure, automated reading-0.1'] 
Df_Systolic['Systolic blood pressure, automated reading'] = Df_Systolic[Fields].mean(axis=1) 

#### Moving on to Heart failure variable
#### specify how we define heart failure (HF) under ICD10 
HFs = ['I110','I132','I500','I501','I509'] 

### Open Hes records
HES_records=UKBr.HES_tsv_read(filename=<location of HES tsv file>) 

### Find HFs in HES record file - ICD10 diagnosis column
HES_HFs = UKBr.HES_code_match(df=HES_records, icds=HFs, which='diagnosis') 
## to select from other diagnosis columns:
## ICD9: which=''
## OPCS: which='opcs'


### Only keep first instance of HF for each subjects 
date='epistart' 
## date can otherwise be specified to: 'admidate'
First_times_HF = UKBr.HES_first_time(HES_HFs,date)

## Create binary variable for HF
First_dates_HF['HF_icd10'] = 1 

############### If pandas has been loaded previously #####################
### Merge all variables together
DF = pd.merge(df_BMI,SBP,on='eid',how='inner') ## 'inner' keeps the intersection of the samples in df_BMI and SBP
DF = pd.merge(DF,First_dates_HF[['eid','HF_icd10']],on='eid',how='outer') ## 'outer' keeps the union of the samples in DF and First_dates_HF

## Most subjects won't have a record of HF, and thus won't have any entry in 'First_dates_HF'; Mark then with '0' in the 'HF_icd10' variable in 'DF'
DF['HF_icd10'].fillna(0,inplace=True)

### Save the final result
DF.to_csv(<location\file_name.csv>, sep=',',index=None)
