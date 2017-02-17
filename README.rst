################################
Biobank Read
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

############
Current functionalities
############
The packages provides the following functions;

Extracting variables from .csv file:

- extract_variable: extract values for one variable into a pandas dataframe. It first parses the html file for an input keyword, finds corresponding columns, and extract those into a pandas dataframe.
- all_related_vars: extracts all variables related to a keyword variable input, and returns them in one single dataframe.
- extract_many_vars: performs extract_variable() for several pre-specified variables, and returns them in one single dataframe. 
- Get_ass_dates: returns data frame of dates subjects attended the first assessment centre (known as "baseline").

Extracting confounding variables:

- confounders_gen: returns a dictionary of dataframes for a range of classical confounders (BMI, Age, Ethnicity and Sex). More confounders can be added optionally.
- rename_conf: shortens the names of columns in a dataframe of confounders.

Data-codings:

- find_DataCoding: finds the data coding associated with a variable, if it exists.
- codes_categories: returns data coding convention from online page, for any data coding number.
- Datacoding_match: finds a key-value in a variable's dataframe, if it has a known data coding.

Functions on extracted variables:

- Mean_per_visit: evaluates the average of a variable with multiple measurement for each visit, returns a dataframe with 1 column for each visit. Only relevant if multiple measurements available.
- df_mean: returns the mean of a variable in a dataframe, across all its columns.
- vars_by_visits: returns all the column names associated with a visit round: initial assessment (0), 1st (1) and 2nd (2) re-visit.
- rename_columns: renames the columns of a data frame for variable, while preserving the order and number of measurements and visits.
- remove_outliers: removes outliers from a variable's data frame, based on some input standard deviation (default = 4).

HES data
=========

- HES_tsv_read: opens and reads .tsv HES file, and returns the data in a dataframe.
- find_ICD10_codes: finds and returns all ICD10 codes associated with a class of disease codes.
- HES_code_match: finds all instances related to one or several disease codes input, across the diagnosis or operations columns of the HES data.
- HES_first_time: finds the earliest admission date in HES data for all subjects that have HES records.
- HES_after_assess: returns a boolean for whether subjects had HES records after attenting the baseline assessment centre.
- HES_before_assess: returns a boolean for whether subjects had HES records before attenting the baseline assessment centre.



################################
Thanks
################################
Much gratitude is owed to Dr Bill Crum, who substantially contributed to this project and helped make it come out to the world


“On the planet Earth, man had always assumed that he was more intelligent than dolphins because he had achieved so much—the wheel, New York, wars and so on—whilst all the dolphins had ever done was muck about in the water having a good time. But conversely, the dolphins had always believed that they were far more intelligent than man—for precisely the same reasons.”


.. _UKBiobank: http://www.ukbiobank.ac.uk/
.. _portal: https://amsportal.ukbiobank.ac.uk/
