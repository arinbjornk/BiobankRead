################################
Biobank Read
################################

BiobankRead is a package that pulls out data from UKBiobank extracted files and turns it into readily usable data-frames for any specified variables. It provides faster and easier pre-processing tools in Python of UKBiobank clinical and phenotypical data, which is otherwise known for its intricate complexity. The functionalities of this package support both main project data and HES records data.

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
Approved investigators will have access to data, as part of a project, which they have to download in .enc format. The .enc file - enc for encrypted - has to be unpacked locally using helper programs that can be downloaded from the same webpage. Detailed instructions are available on the portal ("Data Collection", "Essential Information", "Accessing your data", "Downloading, converting and using your dataset").
After the data has been unpacked locally, there should be two resulting files: a .csv file and a .hmtl file. The csv file contains all the data associated with the project the investigator is working on. The html file explains how that csv file is structured. Conventionally, researchers would open and read the html file, search for a variable, look up its corresponding column number, then extract that column number using STATA, R , Python or similar program.
Now, 

################################
Required input 
################################
Required input: files location of the .csv and .html files, and number of subjects N.

 -.csv: ukb<release_code>.csv, the main data file produced after extraction from the .enc file.
 -.html: associated information file, generated alongside the.csv file with all references to varaibles available.


These should be defined before loading the package as follows :

.. code-block::

 import __builtin__
 __builtin__.namehtml='<file_location>.html'
 __builtin__.namecsv='<file_location>.csv' 
 __builtin__.N= n
 import BiobankRead2.BiobankRead2 as UKBr
 
Current functionalities:
############
XXXXX

Future updates:
############
XXXXX


################################
Thanks
################################
Much gratitude is owed to Dr Bill Crum, who substantially contributed to this project and helped make it come out to the world

-----
“On the planet Earth, man had always assumed that he was more intelligent than dolphins because he had achieved so much—the wheel, New York, wars and so on—whilst all the dolphins had ever done was muck about in the water having a good time. But conversely, the dolphins had always believed that they were far more intelligent than man—for precisely the same reasons.”
-----


.. _UKBiobank: http://www.ukbiobank.ac.uk/
.. _portal: https://amsportal.ukbiobank.ac.uk/
