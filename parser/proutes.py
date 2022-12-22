import geojson
import psycopg2
#Mettre latitude et longitude en TEXT dans le schema de db-citymapper
conn = psycopg2.connect(database="city_mapper_db", user="postgres", host="localhost", password="postgres")
cursor = conn.cursor()
cursor.execute(""f"SELECT DISTINCT nom FROM noms WHERE route_type = 0 ORDER BY nom ASC""")
res = cursor.fetchall()
trams = []
for nom in res:
   trams.append(nom[0])


cursor.execute(""f"SELECT DISTINCT nom FROM noms WHERE route_type = 1 ORDER BY nom ASC""")
res = cursor.fetchall()
metros = []
for nom in res:
   metros.append(nom[0])


cursor.execute(""f"SELECT DISTINCT nom FROM noms WHERE route_type = 2 ORDER BY nom ASC""")
res = cursor.fetchall()
trains = []
for nom in res:
   trains.append(nom[0])


cursor.execute(""f"SELECT DISTINCT nom FROM noms WHERE route_type = 3 ORDER BY nom ASC""")
res = cursor.fetchall()
bus = []
for nom in res:
   bus.append(nom[0])


for tram in trams :
   cursor.execute(""f"SELECT DISTINCT liste_stops FROM routes_stops WHERE route_name = $${tram}$$ """)
   res = cursor.fetchall()
   s = set([])
   for l in res :
      res = l[0]
      res=res.strip('][').split(', ')
      res = list(map(int,res))
      s.update(set(res))

   print(""f"INSERT into lignes VALUES('{tram}','{list(s)}','0');""")

for metro in metros :
   cursor.execute(""f"SELECT DISTINCT liste_stops FROM routes_stops WHERE route_name = $${metro}$$ """)
   res = cursor.fetchall()
   s = set([])
   for l in res :
      res = l[0]
      res=res.strip('][').split(', ')
      res = list(map(int,res))
      s.update(set(res))

   print(""f"INSERT into lignes VALUES('{metro}','{list(s)}','1');""")

for train in trains :
   cursor.execute(""f"SELECT DISTINCT liste_stops FROM routes_stops WHERE route_name = $${train}$$ """)
   res = cursor.fetchall()
   s = set([])
   for l in res :
      res = l[0]
      res=res.strip('][').split(', ')
      res = list(map(int,res))
      s.update(set(res))
   print(""f"INSERT into lignes VALUES('{train}','{list(s)}','2');""")

for bu in bus :
   cursor.execute(""f"SELECT DISTINCT liste_stops FROM routes_stops WHERE route_name = $${bu}$$ """)
   res = cursor.fetchall()
   s = set([])
   for l in res :
      res = l[0]
      res=res.strip('][').split(', ')
      res = list(map(int,res))
      s.update(set(res))
   print(""f"INSERT into lignes VALUES('{bu}','{list(s)}','3');""")
