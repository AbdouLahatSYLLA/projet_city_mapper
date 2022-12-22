#open a file for read-only purposes
f = open("../paris/network_combined.csv", 'r')

lineno = 0

#loop over each line of the input file
next(f)
for line in f:
    #break line into an array of attributes separated by ';'
    items = line.rstrip("\n").split(";")

    #print the lineno variable
    #print(f"Starting printing line number {lineno}")




    #loop over each attribute in the array items
    insert =" "
    for item in items:

        #replace ' with '', for strings in postgreSQL
        item = item.replace("'", "''")
        if(item == items[5]):
            l = item.split(",")
            l = [int(x.split(':')[0]) for x in l]
            item = str(l)

        #print the attribute position in array and its value (modif version)
        #item = item.replace("\n", ",")
        #if "\n" in item:
            #item.replace("\n",",")
        insert +="'"+item+"',"
        #print(f" \'{item}\'")


    insert = insert.rstrip(",")
    print(f"INSERT INTO network_combined VALUES({insert});")
    lineno = lineno + 1

print(f"UPDATE network_combined")
print(f"SET route_I_counts = REPLACE(route_I_counts, ']', ')' );")
print(f"UPDATE network_combined")
print(f"SET route_I_counts = REPLACE(route_I_counts, '[', '(' );")
