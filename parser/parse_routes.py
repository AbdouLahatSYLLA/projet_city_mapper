import geojson
import psycopg2

# Connect to the database
conn = psycopg2.connect(database="city_mapper_db", user="postgres", host="localhost", password="postgres")
cursor = conn.cursor()

# Initialize Geometry object with default values
geojson.geometry.Geometry.__init__.__defaults__ = (None, False, 20)

# Open the geojson file and load its contents
with open("parser/routes.geojson") as f:
   gj = geojson.load(f)

# Loop through the features in the geojson file
for line in gj['features']:
   trajet = []
   # Loop through the coordinates of each feature
   for arret in line['geometry']['coordinates']:
      lng, lat = arret

      # Execute a SELECT statement to retrieve the stop_i for the given longitude and latitude
      cursor.execute(""f"SELECT stop_i FROM network_node WHERE longitude = '{lng}' and latitude = '{lat}' """)
      conn.commit()
      stop_i = cursor.fetchall()
      
      trajet.append(int(stop_i[0][0]))

   # Print the INSERT statement for the current feature
   print(f"INSERT INTO routes VALUES('{trajet}','{line['properties']['route_type']}','{line['properties']['route_I']}','{line['properties']['route_name']}');")
