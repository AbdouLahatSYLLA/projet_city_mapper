import geojson
geojson.geometry.Geometry.__init__.__defaults__ = (None, False, 20)
with open("sections.geojson") as f:
   gj = geojson.load(f)
for line in gj['features']:
   stri = ""
   for elt in line['properties']['route_I_counts']:
      a = str(elt)
      b = str(line['properties']['route_I_counts'][elt])
      stri +=a+":"+b+','
   stri = stri.rstrip(',')   
   print(f"INSERT INTO sections VALUES('{line['geometry']['coordinates']}','{line['properties']['from_stop_I']}','{line['properties']['to_stop_I']}','{line['properties']['n_vehicles']}','{line['properties']['duration_avg']}','{stri}','{line['properties']['route_type']}');")


