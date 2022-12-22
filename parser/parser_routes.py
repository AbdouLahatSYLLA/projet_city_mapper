import geojson
import psycopg2
#Mettre latitude et longitude en TEXT dans le schema de network_node dans db-citymapper.sql
conn = psycopg2.connect(database="city_mapper_db", user="postgres", host="localhost", password="postgres")
cursor = conn.cursor()

geojson.geometry.Geometry.__init__.__defaults__ = (None, False, 20)
with open("routes.geojson") as f:
   gj = geojson.load(f)
for line in gj['features']:
   trajet = []
   for arret in line['geometry']['coordinates'] :
      lng,lat = arret
      cursor.execute(""f" SELECT stop_i FROM network_node WHERE longitude = '{lng}' and latitude = '{lat}'""")
      stop_i = cursor.fetchall()
      trajet.append(int(stop_i[0][0]))
   print(f"INSERT INTO routes VALUES('{trajet}','{line['properties']['route_type']}','{line['properties']['route_I']}','{line['properties']['route_name']}');")
