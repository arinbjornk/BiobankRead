# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 17:29:32 2017

@author: Deborah
"""
import sys
import __builtin__

__builtin__.namehtml='D:\\Uk Biobank\\Application 10035\\R8546\\ukb8546.html'
__builtin__.namecsv='D:\\Uk Biobank\\Application 10035\\R8546\\ukb8546.csv'
__builtin__.N = 502641  
import BiobankRead2.BiobankRead2 as UKBr

# MAIN
def main(argv = None):
    # Catch command-line arguments in context
    if argv is None:
        argv = sys.argv

    # Instantiate class
    location = 'Z:\\EABOAGYE\\Users\\wcrum\\Projects\\UKBB\\UKBB-data'
    projectID, studyID = 10035, 8546
    bbclass = UKBr.BiobankRead(projectID=projectID, studyID=studyID, location=location, N=1000)
    if not bbclass.OK:
        print 'error creating bbclass'
        return 1
    
    
    # Is there data on Alcohol intake, for ex. ?
    Alc = UKBr.search_in_list(ls=bbclass.Vars,key='Alcohol')
    Alc_var = bbclass.extract_variable(Alc[2])
    Alc_var = bbclass.rename_columns(Alc_var,Alc[2])
    
    # put all the alcohol variables in one df
    Alc_var_all  = bbclass.extract_many_vars(Alc, baseline_only=False)
    
    # compute average over each visit
    # BP data more interesting for this 
    BP = UKBr.search_in_list(ls=bbclass.Vars,key='blood pressure')
    BP = [x for x in BP if 'automated' in x]
    BP_var  = bbclass.extract_many_vars(BP,baseline_only=False)
    BP_aver  = bbclass.Mean_per_visit(df=BP_var,dropnan=True)
    BP_aver.describe()
    
    print BP
    print BP_var
    print BP_aver
    
    return 0    
    
    ## Functionalities related to HES file extractions
    # after downloading HES file from online platform, unpack it as df
    filename = 'D:\Uk Biobank\HES data\ukb_HES_10035.tsv'
    everything_HES = UKBr.HES_tsv_read(filename=filename)
    # Let's find all disease related to acute renal problems: N0-N3 +N99
    select = ['N'+str(n) for n in range(4)]##
    select.append('N99')               
    RD_ICD10 = UKBr.find_ICD10_codes(select=select) # there should be ~240 codes in this variable
    # Find all HES admission with acute renal disease as diagnostic
    HES_RD = UKBr.HES_code_match(df=everything_HES,icds=RD_ICD10,which='diagnosis')
    HES_RD = HES_RD[['eid','diag_icd10','admidate']]
    HES_RD = HES_RD.dropna(subset=['admidate'])
    # Which subjects had admissions before attending a UKB assessment centre?
    # step 1: load assessment centre dates
    Ass_dates = UKBr.assess_dates
    Ass_dates = Ass_dates[Ass_dates.columns.tolist()[0:2]]
    # step 2: Find when subjects were first ever admitted
    HES_sub = HES_RD[['eid','admidate']]
    First_times = UKBr.HES_first_time(HES_sub)
    
    ## Find records of Self-reported diseases in df
    illness = UKBr.search_in_list(ls=All_vars,key='illness code')
    illness_var = UKBr.extract_variable(illness[0],n_subjects=N)
    illness_var = UKBr.rename_columns(illness_var,'illness_code')
    CV_illness = ['1095','1070','1065']
    SR_cvd = UKBr.SR_code_match(df=illness_var,cols=None,icds=CV_illness)
    
# Test
if __name__ == '__main__':
    sys.exit(main())
