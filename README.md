# python-TSC-Hyper-example
This code was created while working on the API Level 2 challenge (https://www.tableau.com/developer/mini-challenges).  

##Prereqs
You will need to install:
- Python 3
- Tableau Server Client https://github.com/tableau/server-client-python
- Tableau Hyper API https://help.tableau.com/current/api/hyper_api/en-us/index.html

You will also need to create an env.yaml file and put it in the root folder of your project.  A sample_env.yaml file is provided for you.

Finally create a project named HyperTest on your Tableau server.  

##Running the code
`python3 ./workbooks.py`

##Output
This will create two local files
1. workbooks.csv
1. workbooks.hyper

This will also deploy workbooks.hyper to the HyperTest project on your server.
