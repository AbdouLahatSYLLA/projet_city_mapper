import geojson
geojson.geometry.Geometry.__init__.__defaults__ = (None, False, 20)
with open("stops.geojson") as f:
    gj = geojson.load(f)
    
for line in gj['features']:
    print(f"INSERT INTO stops VALUES('{line['properties']['stop_I']}','{line['geometry']['coordinates'][1]}','{line['geometry']['coordinates'][0]}','{line['properties']['name']}');")
