
from google.cloud import bigquery
import requests_toolbelt.adapters.appengine

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()



def get_recent(userid):
    client = bigquery.Client()
    
    query = (
'SELECT * FROM `TABLE_TAME.TABLE` where userid="' +str(userid)+ '" order by timestamp desc LIMIT 10'
    )
    query_job = client.query(
    query,
    location="US",
    )
    return  query_job.result() 
