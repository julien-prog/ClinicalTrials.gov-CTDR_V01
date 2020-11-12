
# CTDR_V01
Overview: 

ClinicalTrials.gov is a platform gathering the data of a high number of clinical trials performed through the last decades. The interface and the code behind, helps the user retrieving, organising and storing the data needed for a selected set of trials into a CSV file.

The advantage of using this tool rather than dealing directly with the governmental platform:

Store an unlimited number of trials data into the same CSV
Show the user the entire set of retrievable information
User select only the information needed
Improve the efficiency by running URL in batch

Requirements :

These scripts were developed on Python 3 and does not work with Python 2.
The graphic adjustement has been done on a Macbook 13 inch. No testing has been performed on other screen size and OS

How to use it :

First: Download the files and folders and store them on the same directory

Second: Launch User_Interface_F4J_Public.py on your terminal or your IDE

Third: In "XML Schema":
  click "Download the latest XML schema version" button ; the latest version will be stored in the XMLShema folder
  click "Apply Change" change
  
Fourth: In "User Setting" -> Select the data you want to retrieve

Fifth: Enter the output name and path

Sixth: Paste the URL of the files to download with the following format: 
        https://clinicaltrials.gov/ct2/results/download_studies?cond=Covid19&term=&cntry=US&state=&city=&dist=
  or select the CSV file where you previously put all the URL to download following the CSV pattern "Run_in_batch_example.csv"

Seventh: Select the different option and launch it !
