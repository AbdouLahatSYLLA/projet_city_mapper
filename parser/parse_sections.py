import geojson
geojson.geometry.Geometry.__init__.__defaults__ = (None, False, 20)
with open("sections.geojson") as f:
   gj = geojson.load(f)
for line in gj['features']:
   routes = []
   for elt in line['properties']['route_I_counts']:
      a = [int(str(elt))]
      routes += a
      
   print(f"INSERT INTO sections VALUES('{line['geometry']['coordinates']}','{line['properties']['from_stop_I']}','{line['properties']['to_stop_I']}','{line['properties']['n_vehicles']}','{line['properties']['duration_avg']}','{routes}','{line['properties']['route_type']}');")


