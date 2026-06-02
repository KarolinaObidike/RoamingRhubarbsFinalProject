#THIS CODE WILL BE RESPONSIBLE FOR LOADING ALL FUNCTIONS
from databases import create_database
from databases import connectdb
from ETL import Extract
from ETL import transform

#create_database.setup_db()

rawdata = Extract.get_data()

transform.transform(rawdata)
