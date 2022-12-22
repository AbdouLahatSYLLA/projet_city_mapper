enssemble = {'(324)', '(706)', '(705)', '(318)', '(8, 7)', '(1000)', '(228)', '(227)', '(323, 317)'}
liste_entiers = [(x.strip('()')) for x in enssemble]
print(liste_entiers)
string = str(liste_entiers)
elements = string.split(', ')
s = str(elements)
print(s)
s = s.replace("'","")
s =  s.replace("[","").replace("]","")
s = "(" + s + ")"
print(s)
