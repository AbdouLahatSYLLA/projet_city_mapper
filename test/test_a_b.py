import networkx as nx
import folium
import psycopg2
import requests
import openrouteservice as ors


client = ors.Client(key='5b3ce3597851110001cf6248000fa91811364d86b89d93977ba9769c')

conn = psycopg2.connect(database="app_citymapper_db", user="postgres", host="localhost", password="postgres")
cursor =conn.cursor()

G = nx.Graph()
cursor.execute(""f" select from_stop_I,to_stop_I, d_walk  from network_walk """)
f = cursor.fetchall()
for line in f:
    G.add_edge(int(line[0]), int(line[1]), weight = int(line[2]))


# Trouvez les noeuds de départ et d'arrivée de l'itinéraire
origin =  1
destination = 7

map =folium.Map(location=[48.8619, 2.3519], tiles="OpenStreetMap", zoom_start=12, prefer_canvas=True)

path=nx.dijkstra_path(G,origin,destination)
print(path)
coordinates = []
for e in path:
    cursor.execute(""f" select distinct latitude,longitude from network_node where stop_i = {e}""")
    res = cursor.fetchall()
    coordinates.append([float(res[0][1]),float(res[0][0])])

print(coordinates)
#nx.draw(H, with_labels=True,font_weight='bold')
#plt.savefig("path.png")
#m = ox.plot_route_folium(G, path,map)
dep = coordinates[0]
arv = coordinates[-1]
folium.Marker(
    location=[dep[1],dep[0]]
).add_to(map)

folium.Marker(
    location=[arv[1],arv[0]]
).add_to(map)

# Some coordinates in Berlin

route = client.directions(
    coordinates=coordinates,
    profile='foot-walking',
    format='geojson',
    options={"avoid_features": ["steps"]},
    validate=False,
)
folium.PolyLine(locations=[list(reversed(coord))
                           for coord in
                           route['features'][0]['geometry']['coordinates']]).add_to(map)

map.save('map.html')
