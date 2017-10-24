################################
Biobank Read - latest version: 2.2.1
################################

BiobankRead is a package that pulls out data from UKBiobank extracted files and turns it into readily usable data-frames for any specified variables. 
It provides faster and easier pre-processing tools in Python of UKBiobank clinical and phenotypical data, which is otherwise known for its intricate complexity. The functionalities of this package support both main project data and HES records data.

This python package is intended to be usable as part of processing and analysis pipelines. 

################################
Overview
################################
BiobankRead aims to provide python-based tools for the extraction, cleaning and pre-processing of UK Biobank data.
(UKBiobank_). Approved researchers will have the ability to access the data through the dedicated online portal_ .
The package takes avantage of the data frame tools in pandas and of the regex facilities in re.

Biobankread is also a ressourceful tool for creating custom variables , using existing ones, HES records for any disease / groups of diseases, and any data frame manipulation in Pandas.

################################
Citation
################################
To use this package in published work, please cite us using the following DOI:

.. image:: https://zenodo.org/badge/73500060.svg
   :target: https://zenodo.org/badge/latestdoi/73500060

################################
UKBiobank data
################################
Approved investigators will have access to data, as part of a project, which they have to download in .enc format. The .enc file (enc for encrypted) has to be unpacked locally using helper programs that can be downloaded from the same webpage. Detailed instructions are available on the portal_ ("Data Collection", "Essential Information", "Accessing your data", "Downloading, converting and using your dataset").

After the data has been unpacked locally, there should be two resulting files, a .csv file and a .hmtl file. The csv file contains all the data associated with the project the investigator is working on. The html file explains how that csv file is structured. Conventionally, researchers would open and read the html file, search for a variable, look up its corresponding column number, then extract that column number using STATA, R , Python or similar program.

For each variable, there is between 1 to 28 measurements, across three assessment centre days (baseline, first  and second re-visits). So for one variable, there can be up to 84 associated columns. 

This python package was created with the idea of easing the intricacy of extracting, sorting and analysing such type of data.

HES data
=========
HES (Hospital Episode Statistics) data refers to incidentce of hospitalisation anywhere in England for subjects in UKBiobank, as far back as 1997. It contains information about dates of admission/release/operation, diagnosis coded in ICD10 (or ICD9 if prior to 2000), as well as operations & procedure (OPCS) codes when applicable.

This data can be accessed through the portal_ in the following pathway: "Data Collection", "Downloads", "Data Portal", "Connect". This gives access to a database where the data is kept, and has to be queried using SQL.

################################
Installation
################################
Simply go through pip install:

.. code-block::
 
 $ pip install BiobankRead


################################
Required input 
################################
Required input: files location of the .csv and .html files, and number of subjects N.

 1. .csv: ukb<release_code>.csv, the main data file produced after extraction from the .enc file.
 
 2. .html: associated information file, generated alongside the.csv file with all references to varaibles available.
 
 3. N: number of subjects to extract data for. It is recommended to set this to the total number of subjects available in the project (identical to number of rows in .csv file)


These should be defined before loading the package as follows :

.. code-block::

 import __builtin__
 __builtin__.namehtml='<file_location>.html'
 __builtin__.namecsv='<file_location>.csv' 
 __builtin__.N= n
 import BiobankRead2.BiobankRead2 as UKBr
 BiobankRead=UKBr.BiobankRead()

############
Examples
############
Have a look at the test examples (testpy_ and testHFpy_) included in this repo to get an idea of how various functions can be used!

############
Current functionalities
############
The packages provides the following functions;

General:

- All_variables: Read all variable names available in input files and returns their names.
- GetEIDs: Returns all the EIDs related to the app. #. of the input files.
- Get_ass_dates: returns data frame of dates subjects attended the first assessment centre (known as "baseline").

Extracting variables from .csv file:

- extract_variable: extract values for one variable into a pandas dataframe. It first parses the html file for an input keyword, finds corresponding columns, and extract those into a pandas dataframe. 
   + Inputs: variable = name of variable to extract. Has to be exact, check full name of all variables in "All_variables"
   + Options: baseline_only= True (only 1st assessment), False (default, all assessment rounds)
- all_related_vars: extracts all variables related to a keyword variable input, and returns them in one single dataframe. 
   + Inputs: variable = name of variable to extract. Has to be exact, check full name of all variables in "All_variables"
   + Options: baseline_only= True (only 1st assessment), False (default, all assessment rounds); dropNaN=False (default, keep subjects with complete entries only), True (the inverse of False)
- extract_many_vars: performs extract_variable() for several pre-specified variables, and returns them in one single dataframe. 
   + Inputs: keywords = list of string of exact names of all desired variables. Have to be exact, check full name of all variables in "All_variables" 
   + Options: baseline_only= True (only 1st assessment), False (default, all assessment rounds); dropNaN=False (default, keep subjects with complete entries only), True (the inverse of False)

Extracting confounding variables:

- confounders_gen: returns a dictionary of dataframes for a range of classical confounders (BMI, Age, Ethnicity and Sex). More confounders can be added:
   + Options: more_vars: [] (default), or any text list with elements in 'quotes'.
- rename_conf: shortens the names of columns in a dataframe of confounders to shorter versions

Data-codings:

- find_DataCoding: finds the data coding associated with a categorical variable (input= the name of that said variable), if it exists.
- codes_categories: returns data coding convention from online page, for any data coding number.
- Datacoding_match: finds a key-value in a variable's dataframe, if it has a known data coding. Find datacoding with find_DataCoding() before using this funct. if you are not sure what it is. 
   + Inputs: df (dataframe), key (category sought), name (column of categorical variable)

Functions on extracted variables:

- Mean_per_visit: evaluates the average of a variable with multiple measurement for each visit, returns a dataframe with 1 column for each visit. Only relevant if multiple measurements available.
   + Inputs: df= data frame
   + Options: dropnan (default dropna=False) drop any subject with missing observation
- df_mean: returns the mean of a variable in a dataframe, across all its columns excluding eid.
   + Inputs: df = data input, key = which columns to average over
- vars_by_visits: returns all the column names associated with a visit round: initial assessment (0), 1st (1) and 2nd (2) re-visit.
   + Inputs: col_names: name of variable to search
   + Options: visit: which visit round (Default: visit=0) can also be "1" or "2"
- remove_outliers: removes outliers for any variable based on std dev.. 
   + Inputs: df= data frame, cols = variable(s) to trim; 
   + Options: lim = how many std dev. away (default = 4), one_sided = trim both small/large values, or only large values (default=False).
- SR_code_match: finds input SR desease codes in specified columns of Self-reported conditions data
   + Inputs: df = dataframe to search, icds = SR codes to find
- ICD_code_match: find input ICD disease codes in 'cause of death' variables
   + Inputs: df = dataframe to search, icds = ICD10 codes to find

HES data
=========

- HES_tsv_read: opens and reads .tsv HES file, and returns the data in a dataframe.
   + Inputs: filename = HES file name, n = number of rows to extract
   + Options: var = which fields to extract (default: var='All')
- find_ICD10_codes: finds and returns all ICD10 codes associated with a class of disease codes.
   + Inputs: select: any ICD10 category code(s) 
- find_ICD9_codes: finds and returns all ICD9 codes associated with a class of disease codes.
   + Inputs: select: any ICD9 category code(s)
- HES_code_match: find input ICDs & OPCS codes in specified columns from input HES data frame, across its diagnosis or operations columns.
   + Inputs: df = data frame, should be HES data. icds = disease codes to find
   + Options: which = which type of diagnosis. Default: which='ICD10', can also be 'ICD9' or 'OPCS'
- OPCS_code_match: find input OPCS codes in HES data
   + Inputs: df = data frame, should be HES data. icds = disease codes to find
- HES_first_time: finds the earliest admission date in HES data for all subjects that have HES records.
   + Inputs: df= data frame output from HES_code_match or OPCS_code_match
- HES_after_assess: returns a boolean for whether subjects had HES records after attenting the baseline assessment centre.
   + Inputs: df = data frame output from HES_first_time, assess_dates = data frame of baseline assessment dates
- HES_before_assess: returns a boolean for whether subjects had HES records before attenting the baseline assessment centre.
   + Inputs: df = data frame output from HES_first_time


################################
Acknowledgement
################################
BiobankRead was developed as part of the ITMAT Data Science Group and the Epidemiology & Biostatistics department at Imperial College London. 

################################
Thanks
################################
Much gratitude is owed to Dr Bill Crum, who contributed to this project and co-authored its related papers


“On the planet Earth, man had always assumed that he was more intelligent than dolphins because he had achieved so much—the wheel, New York, wars and so on—whilst all the dolphins had ever done was muck about in the water having a good time. But conversely, the dolphins had always believed that they were far more intelligent than man—for precisely the same reasons.”


.. _UKBiobank: http://www.ukbiobank.ac.uk/
.. _portal: https://amsportal.ukbiobank.ac.uk/
.. _zonodo: https://zenodo.org/badge/73500060.svg
.. _testpy: https://github.com/saphir746/BiobankRead/blob/master/test-class.py
.. _testHFpy: https://github.com/saphir746/BiobankRead/blob/master/test_HF.py
