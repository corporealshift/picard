import sqlite3
from fulcrum import Fulcrum

conn = sqlite3.connect('photodb')
cur = conn.cursor()
formid = ''

fulcrum = Fulcrum(key='')
print("Starting to Sync photos")
for (photo_id, filename, lat, lon, alt, created_on, uploaded, speed) in cur.execute('SELECT * FROM photos WHERE uploaded=0'):

  photo = fulcrum.photos.create('/home/pi/picard/pics/%s' % filename)
  print("Photo uploaded")
  obj = {
    "record": {
      "form_id": formid,
      "latitude": lat,
      "longitude": lon,
      "altitude": alt,
      "speed": speed,
      "form_values": {
        '4cf9': [{'photo_id': photo['photo']['access_key']}]
      }
    }
  }
  record = fulcrum.records.create(obj)
  print("Record created")
  cur.execute('UPDATE photos set uploaded=1 where id=%s' % photo_id)
  conn.commit()
  print("Sync'd photo %s to Fulcrum" % photo_id)