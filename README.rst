===========
Biobank Read
===========
“On the planet Earth, man had always assumed that he was more intelligent than dolphins because he had achieved so much—the wheel, New York, wars and so on—whilst all the dolphins had ever done was muck about in the water having a good time. But conversely, the dolphins had always believed that they were far more intelligent than man—for precisely the same reasons.”

################################
Overview
################################
BiobankRead aims to provide python-based tools for the extraction, cleaning and pre-processing of UK Biobank data.
(UKBiobank_). Approved researchers will have the ability to access the data through the dedicated online portal_ .
The package takes avantage of the data frame tools in pandas and of the regex facilities in re.


################################
Required input 
################################
Required input: files location of the .csv and .html files, and number of subjects N.
 -.csv: ukb<release_code>.csv, the main data file produced after extraction from the .enc file.
 
 -.html: associated information file, generated alongside the.csv file with all references to varaibles available.


These should be defined before loading the package as follows:
.. code-block::

 import __builtin__
 __builtin__.namehtml='<file_location>.html'
 __builtin__.namecsv='<file_location>.csv' 
 __builtin__.N= n
 import BiobankRead2.BiobankRead2 as UKBr


################################
Thanks
################################
Much gratitude is owed to Dr Bill Crum, who substantially contributed to this project and helped make it come out to the world

Current functionalities:
############
XXXXX

Future updates:
############
XXXXX


.. _UKBiobank: http://www.ukbiobank.ac.uk/
.. _portal: https://amsportal.ukbiobank.ac.uk/
