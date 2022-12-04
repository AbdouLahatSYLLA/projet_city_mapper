import geojson
#geojson.geometry.Geometry.__init__.__defaults__ = (None, False, 20)
with open("schema_sql/routes.geojson") as f:
   gj = geojson.load(f)
for line in gj['features']:
   print(f"INSERT INTO routes VALUES('{line['geometry']['coordinates']}','{line['properties']['route_type']}','{line['properties']['route_I']}','{line['properties']['route_name']}');")
