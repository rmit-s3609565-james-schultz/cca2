from PIL import Image
from PIL import ExifTags
from urllib.request import urlopen
import requests
from google.cloud import bigquery


def hello_gcs(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    filename = file['name']
    uri = file['mediaLink']    
    exif_loc = get_exif(uri)
    animal = detect_labels_uri(uri)
    userid = filename[:filename.index("-")]
    timestamp = get_timestamp(filename)
    update_bq(userid,animal,exif_loc[0],exif_loc[1],uri,timestamp)


def get_exif(image_url):
    exifData = {}
    img = Image.open(urlopen(image_url))
    exifDataRaw = img._getexif()
    for tag, value in exifDataRaw.items():
        decodedTag = ExifTags.TAGS.get(tag, tag)
        exifData[decodedTag] = value
    gps_data = exifData['GPSInfo']
    lat = ((gps_data[2][0][0] + gps_data[2][1][0]/60 + (gps_data[2][2][0]/gps_data[2][2][1])/3600)*-1) 
    lon = ((gps_data[4][0][0] + gps_data[4][1][0]/60 )+ (gps_data[4][2][0]/gps_data[4][2][1])/3600)
    return lat, lon

def update_bq(userid, animal, lat, long, url, timestamp):
    from google.cloud import bigquery
    client = bigquery.Client()
    query = 'INSERT INTO DATASET.TABLE (userid, animal, lat, long, url, timestamp) VALUES ("{}", "{}", "{}","{}","{}","{}")'.format(userid, animal, lat, long, url, timestamp)                                                                                                                      
    print(query)
    query_job = client.query(
    query,
    # Location mus t match that of the dataset(s) referenced in the query.
    location="US",
) 
    
def detect_labels_uri(uri):
    """Detects labels in the file located in Google Cloud Storage or on the
    Web."""
    feral_animals = set(["cat","dog","fox","goat","rabbit","hare","camel","horse"])
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.label_detection(image=image)
    labels = response.label_annotations

    for label in labels:
        if str(label.description).lower() in feral_animals:
            print(f'Labels: {label.description}')
            return label.description
    return "none"
   
def get_timestamp(filename):
    fn_clean = filename[filename.index("-")+1:filename.index(".")]
    ts = fn_clean[:10]
    ts += "T"
    time = "{}:{}:{}.984433".format(fn_clean[11:13],fn_clean[13:15]
,fn_clean[15:17])
    ts += time
    #2019-10-10T23:37:34.984433
    print(ts)
    return ts
    
    
    
    
    
    
    
   
