import base64
import simplekml
from google.cloud import bigquery
from google.cloud import storage


def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
         
         
    """
    table_list = ["latest_cats" ,"recent_dogs"]
    color_list = ["ff0000ff","0000ffff","ffff00ff"]
    for table in table_list:
        result = run_bq(table)
        write_to_gcloud(result, table, color_list.pop())
        
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    
def run_bq(tablename):
    from google.cloud import bigquery
    client = bigquery.Client()
    dataset='INSERT_DATASET'
    query = 'select * from {}.{} limit 50'.format(dataset,tablename)
    print(query)
    query_job = client.query(
    query,
    # Location mus t match that of the dataset(s) referenced in the query.
    location="US",
)
    results = query_job.result()
    return results
    
def write_to_gcloud(result, tablename, color):
    from google.cloud import storage
    import simplekml
    rows = "userid,animal,lat,long,url,timestamp\n"
    kml=simplekml.Kml()
    for row in result:
        animal = str(row['animal'])
        timestamp = str(row['timestamp'])
        lat=row['lat']
        lon=row['long']
        pnt = kml.newpoint(name=animal+ "_" + timestamp,
                     coords=[(lon,lat)],
                     description=row['url'])
        pnt.style.labelstyle.color = color
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('cca2-photos')
    blob = bucket.blob(tablename+ ".kml")
    upload = str(kml.kml())
    print(blob.upload_from_string(upload))

    print('File {} uploaded to {}.'.format(
        tablename,
        tablename))
    
    
    
    
    
    
