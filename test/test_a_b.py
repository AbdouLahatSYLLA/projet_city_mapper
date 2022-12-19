import psycopg2 

def route_I_counts_to_list(s) :
    l = s.split(',') 
    l = [x.split(':')[0] for x in l]  
    return set(l)

conn = psycopg2.connect(database="citymapper", user="danii", host="localhost", password="danii") 
cursor = conn.cursor() 
cursor.execute("""SELECT DISTINCT route_I_counts FROM network_rail WHERE from_stop_i IN ( SELECT stop_i FROM network_node WHERE nom = 'Nation')""") 
dep = cursor.fetchall() 
a =set([])
for element in dep :
    print(element[0])
    a.update(route_I_counts_to_list(element[0]))

print("a")
print(a)
print("a")
cursor.execute("""SELECT DISTINCT route_I_counts FROM network_rail WHERE from_stop_i IN ( SELECT stop_i FROM network_node WHERE nom = 'Nanterre-Préfecture')""") 
arv = cursor.fetchall() 
b =set([])
for element in arv :
    print(element[0])
    b.update(route_I_counts_to_list(element[0]))

print("b")
print(b)
print("b")
c = a.intersection(b)
req = "("
for r in c :
    req += "'" + str(r) + "'"+","

req =  req.rstrip(',')
req += ")"
print(req)
cursor.execute(""f"SELECT DISTINCT route_name FROM routes WHERE route_i IN {req}""") 
dep = cursor.fetchall() 
print(dep)
#print(route_I_counts_to_list(depart[0][1]))


