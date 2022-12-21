#open a file for read-only purposes
f = open("../paris/network_tram.csv", 'r')

lineno = 0

#loop over each line of the input file
next(f)
for line in f:
    #break line into an array of attributes separated by ';'
    items = line.rstrip("\n").split(";")

    #print the lineno variable
    #print(f"Starting printing line number {lineno}")

    i = 0


    #loop over each attribute in the array items
    insert =" "
    for item in items:

        #replace ' with '', for strings in postgreSQL
        item = item.replace("'", "''")
        #pour supprimer la partie droite dans route_i_counts qui nous interesse pas
        if(item == items[5]):
            l = item.split(",")
            l = [x.split(':')[0] for x in l]
            item = str(l)


        #print the attribute position in array and its value (modif version)
        #item = item.replace("\n", ",")
        #if "\n" in item:
            #item.replace("\n",",")
        insert +="'"+item+"',"
        #print(f" \'{item}\'")

        i = i + 1
    insert = insert.rstrip(",")
    print(f"INSERT INTO network_tram VALUES({insert});")
    lineno = lineno + 1

print(f"UPDATE network_tram")
print(f"SET route_I_counts = REPLACE(route_I_counts, ']', ')';")
print(f"UPDATE network_tram")
print(f"SET route_I_counts = REPLACE(route_I_counts, '[', '(';")
