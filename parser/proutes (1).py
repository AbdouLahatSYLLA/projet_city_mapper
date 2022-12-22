import geojson
import psycopg2 
#Mettre latitude et longitude en TEXT dans le schema de db-citymapper
print("CREATE TABLE noms_lignes(nom TEXT,ligne TEXT,route_type NUMERIC(1));")
conn = psycopg2.connect(database="citymapper", user="danii", host="localhost", password="danii") 
cursor = conn.cursor() 
cursor.execute(""f"SELECT DISTINCT nom,stations FROM lignes WHERE route_type = 0 ORDER BY nom ASC""") 
res = cursor.fetchall()
for tram in res:
   res = tram[1]
   res = res.strip('][').split(', ')
   res = list(map(int,res))
   ens = set([])
   for i in res :
      cursor.execute(""f"SELECT DISTINCT nom FROM network_node WHERE stop_i = {i}""") 
      nom = cursor.fetchall()
      ens.update(set([nom[0][0]]))
   for arret in ens :
      insert = " "
      x = arret.split("'")
      for y in x:
	      insert+="'"+y+"'"
      print(""f"INSERT into noms_lignes VALUES({insert},'{tram[0]}','0');""")


cursor.execute(""f"SELECT DISTINCT nom,stations FROM lignes WHERE route_type = 1 ORDER BY nom ASC""") 
res = cursor.fetchall()
for metro in res:
   res = metro[1]
   res = res.strip('][').split(', ')
   res = list(map(int,res))
   ens = set([])
   for i in res :
      cursor.execute(""f"SELECT DISTINCT nom FROM network_node WHERE stop_i = {i}""") 
      nom = cursor.fetchall()
      ens.update(set([nom[0][0]]))
   for arret in ens :
      insert = " "
      x = arret.split("'")
      for y in x:
	      insert+="'"+y+"'"      
      print(""f"INSERT into noms_lignes VALUES({insert},'{metro[0]}','1');""")

cursor.execute(""f"SELECT DISTINCT nom,stations FROM lignes WHERE route_type = 2 ORDER BY nom ASC""") 
res = cursor.fetchall()
for train in res:
   res = train[1]
   res = res.strip('][').split(', ')
   res = list(map(int,res))
   ens = set([])
   for i in res :
      cursor.execute(""f"SELECT DISTINCT nom FROM network_node WHERE stop_i = {i}""") 
      nom = cursor.fetchall()
      ens.update(set([nom[0][0]]))
   for arret in ens :
      insert = " "
      x = arret.split("'")
      for y in x:
	      insert+="'"+y+"'"  
      print(""f"INSERT into noms_lignes VALUES({insert},'{train[0]}','2');""")

cursor.execute(""f"SELECT DISTINCT nom,stations FROM lignes WHERE route_type = 3 ORDER BY nom ASC""") 
res = cursor.fetchall()
for bus in res:
   res = bus[1]
   res = res.strip('][').split(', ')
   res = list(map(int,res))
   ens = set([])
   for i in res :
      cursor.execute(""f"SELECT DISTINCT nom FROM network_node WHERE stop_i = {i}""") 
      nom = cursor.fetchall()
      ens.update(set([nom[0][0]]))
   for arret in ens :
      insert = " "
      x = arret.split("'")
      for y in x:
	      insert+="'"+y+"'"  
      print(""f"INSERT into noms_lignes VALUES({insert},'{bus[0]}','3');""")