import folium, io, json, sys, math, random, os
import psycopg2
from folium.plugins import Draw, MousePosition, MeasureControl
from jinja2 import Template
from branca.element import Element
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ast
import networkx as nx
import requests
import openrouteservice as ors



class MainWindow(QMainWindow):
    count = 0
    coord1 = []
    coord2 = []
    client = ors.Client(key='5b3ce3597851110001cf6248000fa91811364d86b89d93977ba9769c')
    G = nx.Graph()
    def __init__(self):
        super().__init__()

        self.resize(800, 800)

        main = QWidget()
        self.setCentralWidget(main)
        main.setLayout(QVBoxLayout())
        main.setFocusPolicy(Qt.StrongFocus)

        self.tableWidget = QTableWidget()
        self.tableWidget.doubleClicked.connect(self.table_Click)
        self.rows = []

        self.webView = myWebView()

        controls_panel = QHBoxLayout()
        mysplit = QSplitter(Qt.Vertical)
        mysplit.addWidget(self.tableWidget)
        mysplit.addWidget(self.webView)

        main.layout().addLayout(controls_panel)
        main.layout().addWidget(mysplit)

        _label = QLabel('From: ', self)
        _label.setFixedSize(20,20)
        self.from_box = QComboBox()
        self.from_box.setMaximumSize(250, 30)
        self.from_box.setEditable(True)
        self.from_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.from_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.from_box)

        _label = QLabel('  To: ', self)
        _label.setFixedSize(20,20)
        self.to_box = QComboBox()

        self.to_box.setMaximumSize(250, 30)
        self.to_box.setEditable(True)
        self.to_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.to_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.to_box)

        _label = QLabel('Hops: ', self)
        _label.setFixedSize(20,20)
        self.hop_box = QComboBox()
        self.hop_box.addItems( ['1', '2', '3', '4', '5'] )
        self.hop_box.setCurrentIndex( 2 )
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.hop_box)

        _label = QLabel('type: ', self)
        _label.setFixedSize(20,20)
        self.typ_box = QComboBox()
        self.typ_box.addItems( ['Bus', 'Metro', 'RER', 'Tram', 'Walk','ALL', 'RER/Metro','RER/Bus'] )
        self.typ_box.setCurrentIndex( 2 )
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.typ_box)




        self.go_button = QPushButton("Go!")
        self.go_button.clicked.connect(self.button_Go)
        controls_panel.addWidget(self.go_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.button_Clear)
        controls_panel.addWidget(self.clear_button)

        self.maptype_box = QComboBox()
        self.maptype_box.addItems(self.webView.maptypes)
        self.maptype_box.currentIndexChanged.connect(self.webView.setMap)
        controls_panel.addWidget(self.maptype_box)

        self.connect_DB()

        self.startingpoint = True

        self.show()


    def connect_DB(self):
        self.conn = psycopg2.connect(database="app_citymapper_db", user="postgres", host="localhost", password="postgres")
        self.cursor = self.conn.cursor()

        self.cursor.execute(""f" SELECT DISTINCT nom FROM noms_lignes WHERE UPPER(nom) = nom """)
        self.conn.commit()
        rows = self.cursor.fetchall()

        for row in rows :
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))


        self.cursor.execute(""f" select from_stop_I,to_stop_I, d_walk  from network_walk """)
        f = self.cursor.fetchall()
        for line in f:
            self.G.add_edge(int(line[0]), int(line[1]), weight = int(line[2]))



    def table_Click(self):
        print("Row number double-clicked: ", self.tableWidget.currentRow())
        list_coord = []
        ligne = self.rows[self.tableWidget.currentRow()]
        i = 1
        while i < len(ligne) :
            stops_list = []
            #Ligne entre les 2 stations
            route_name = str(ligne[i])
            self.cursor.execute(""f"SELECT  liste_arrets,route_i FROM routes WHERE route_name = '{route_name}' """)
            r = self.cursor.fetchall()
            #Station de départ
            depart = str(ligne[i-1])
            self.cursor.execute(""f"SELECT distinct stop_i FROM network_node WHERE nom = $${depart}$$ """)
            dep = self.cursor.fetchall()
            d = []
            for e in dep:
                d.append(int(e[0]))
            #Station d'arrivée
            arrivee = str(ligne[i+1])
            self.cursor.execute(""f"SELECT distinct stop_i FROM network_node WHERE nom = $${arrivee}$$ """)
            arv = self.cursor.fetchall()
            ar = []
            for e in arv:
                ar.append(int(e[0]))
            ok = 0
            for element in r:
                if(ok > 0):
                    break
                re = element[0]
                res = re.strip('][').split(', ')
                res = list(map(int,res))
                for e in d:
                    if(ok > 0):
                        break
                    for f in ar:
                        if e in res and f in res:
                            #Trouvé
                            a = res.index(int(e))
                            b = res.index(int(f))
                            if a > b :
                                res = res[b:a+1]
                                ok =  1
                                break
                            else:
                                res = res[a:b+1]
                                ok = 1
                                break
            for e in res:
                self.cursor.execute(""f"SELECT latitude,longitude FROM network_node WHERE stop_i = '{e}' """)
                r = self.cursor.fetchall()
                stops_list.append([float(r[0][0]),float(r[0][1])])

            for elt in stops_list :
                list_coord.append(elt)
            self.webView.addRoute(stops_list)#Ajouter un argument color :)

            i = i + 2

        #Sans le point de départ et d'arrivée

        chemin = list_coord[1:len(list_coord)-1]
        point_d = list_coord[0]
        point_f = list_coord[-1]



        col = "#B03A2E"
        msg = "Partez de là"
        m = msg + " " + route_name
        print(m)
        print(route_name)
        self.webView.addCol(float(point_d[0]),float(point_d[1]),col,msg) #Argument color plz
        msg = "Descendez Ici"
        self.webView.addCol(float(point_f[0]),float(point_f[1]),col,msg) #Argument color plz

        for e in chemin :
            self.webView.addMarker(float(e[0]),float(e[1])) #Arg color
        return i


    def button_Go(self):
        self.tableWidget.clearContents()

        _fromstation = str(self.from_box.currentText())
        _tostation = str(self.to_box.currentText())
        _hops = int(self.hop_box.currentText())

        self.rows = []
        if _hops >= 1 :
            _route_type = str(self.typ_box.currentText())
            if _route_type == "Bus":
                print("BUS")
                self.cursor.execute(""f" SELECT DISTINCT A.nom,A.ligne,B.nom FROM noms_lignes as A, noms_lignes as B WHERE B.nom = $${_tostation}$$ and A.nom = $${_fromstation}$$ AND A.ligne = B.ligne AND A.route_type = 3 AND B.route_type = 3 """)

            if _route_type == "Metro":
                print("Metro")
                self.cursor.execute(""f" SELECT DISTINCT A.nom,A.ligne,B.nom FROM noms_lignes as A, noms_lignes as B WHERE B.nom = $${_tostation}$$ and A.nom = $${_fromstation}$$ AND A.ligne = B.ligne AND A.route_type = 1 AND B.route_type = 1 """)

            if _route_type == "RER":
                print("RER")
                self.cursor.execute(""f" SELECT DISTINCT A.nom,A.ligne,B.nom FROM noms_lignes as A, noms_lignes as B WHERE B.nom = $${_tostation}$$ and A.nom = $${_fromstation}$$ AND A.ligne = B.ligne AND A.route_type = 2 AND B.route_type = 2""")

            if _route_type == "Tram":
                print("TRAM")
                self.cursor.execute(""f" SELECT DISTINCT A.nom,A.ligne,B.nom FROM noms_lignes as A, noms_lignes as B WHERE B.nom = $${_tostation}$$ and A.nom = $${_fromstation}$$ AND A.ligne = B.ligne AND A.route_type = 0 AND B.route_type = 0 """)

            if _route_type == "Walk":
                print("Walk")

                origin = int(self.coord1[0])
                print(origin)
                destination = int(self.coord2[0])
                print(destination)

                path=nx.dijkstra_path(self.G,origin,destination)
                print(path)
                coordinates = []
                for e in path:
                    self.cursor.execute(""f" select distinct latitude,longitude from network_node where stop_i = {e}""")
                    res = self.cursor.fetchall()
                    coordinates.append([float(res[0][1]),float(res[0][0])])
                print(coordinates)
                dep = coordinates[0]
                arv = coordinates[-1]

                self.webView.addMarker(dep[1],dep[0])
                self.webView.addMarker(arv[1],arv[0])
                self.webView.traceItineraire(coordinates,self.client)



            if _route_type == "RER/Metro":
                print("RER/Metro")
                self.cursor.execute(""f" SELECT DISTINCT A.nom,A.ligne,B.nom FROM noms_lignes as A, noms_lignes as B WHERE B.nom = $${_tostation}$$ and A.nom = $${_fromstation}$$ AND A.ligne = B.ligne AND A.route_type IN (1,2) AND B.route_type IN (1,2)""")

            if _route_type == "RER/Bus":
                print("RER/Bus")
                self.cursor.execute(""f" SELECT DISTINCT A.nom,A.ligne,B.nom FROM noms_lignes as A, noms_lignes as B WHERE B.nom = $${_tostation}$$ and A.nom = $${_fromstation}$$ AND A.ligne = B.ligne AND A.route_type IN (1,3) AND B.route_type IN (1,3)""")

            if _route_type == "ALL":
                print("ALL")
                self.cursor.execute(""f" SELECT DISTINCT A.nom,A.ligne,B.nom FROM noms_lignes as A, noms_lignes as B WHERE B.nom = $${_tostation}$$ and A.nom = $${_fromstation}$$ AND A.ligne = B.ligne """)
            self.rows += self.cursor.fetchall()
            self.conn.commit()

        if _hops >= 2 :
            _route_type = str(self.typ_box.currentText())
            if _route_type == "Bus":
                print("BUS")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B.nom, C.ligne,  D.nom FROM noms_lignes as A, noms_lignes as B, noms_lignes as C, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND D.nom = $${_tostation}$$ AND A.ligne = B.ligne AND B.nom = C.nom AND C.ligne = D.ligne AND A.ligne <> C.ligne AND A.nom <> B.nom AND B.nom <> D.nom AND A.route_type = 3 AND B.route_type = 3 AND C.route_type = 3 AND D.route_type = 3""")
            if _route_type == "Metro":
                print("Metro")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B.nom, C.ligne,  D.nom FROM noms_lignes as A, noms_lignes as B, noms_lignes as C, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND D.nom = $${_tostation}$$ AND A.ligne = B.ligne AND B.nom = C.nom AND C.ligne = D.ligne AND A.ligne <> C.ligne AND A.nom <> B.nom AND B.nom <> D.nom AND A.route_type = 2 AND B.route_type = 2 AND C.route_type = 2 AND D.route_type = 2""")
            if _route_type == "RER":
                print("RER")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B.nom, C.ligne,  D.nom FROM noms_lignes as A, noms_lignes as B, noms_lignes as C, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND D.nom = $${_tostation}$$ AND A.ligne = B.ligne AND B.nom = C.nom AND C.ligne = D.ligne AND A.ligne <> C.ligne AND A.nom <> B.nom AND B.nom <> D.nom AND A.route_type = 1 AND B.route_type = 1 AND C.route_type = 1 AND D.route_type = 1""")

            if _route_type == "Tram":
                print("TRAM")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B.nom, C.ligne,  D.nom FROM noms_lignes as A, noms_lignes as B, noms_lignes as C, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND D.nom = $${_tostation}$$ AND A.ligne = B.ligne AND B.nom = C.nom AND C.ligne = D.ligne AND A.ligne <> C.ligne AND A.nom <> B.nom AND B.nom <> D.nom AND A.route_type = 0 AND B.route_type = 0 AND C.route_type = 0 AND D.route_type = 0 """)

            if _route_type == "Walk":
                print("Walk")

                origin = int(self.coord1[0])
                print(origin)
                destination = int(self.coord2[0])
                print(destination)

                path=nx.dijkstra_path(self.G,origin,destination)
                print(path)
                coordinates = []
                for e in path:
                    self.cursor.execute(""f" select distinct latitude,longitude from network_node where stop_i = {e}""")
                    res = self.cursor.fetchall()
                    coordinates.append([float(res[0][1]),float(res[0][0])])
                print(coordinates)
                dep = coordinates[0]
                arv = coordinates[-1]

                self.webView.addMarker(dep[1],dep[0])
                self.webView.addMarker(arv[1],arv[0])
                self.webView.traceItineraire(coordinates,self.client)

            if _route_type == "RER/Metro":
                print("RER/Metro")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B.nom, C.ligne,  D.nom FROM noms_lignes as A, noms_lignes as B, noms_lignes as C, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND D.nom = $${_tostation}$$ AND A.ligne = B.ligne AND B.nom = C.nom AND C.ligne = D.ligne AND A.ligne <> C.ligne AND A.nom <> B.nom AND B.nom <> D.nom AND A.route_type IN (1,2) AND B.route_type IN (1,2) AND C.route_type IN (1,2) AND D.route_type IN (1,2)""")

            if _route_type == "RER/Bus":
                print("RER/Bus")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B.nom, C.ligne,  D.nom FROM noms_lignes as A, noms_lignes as B, noms_lignes as C, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND D.nom = $${_tostation}$$ AND A.ligne = B.ligne AND B.nom = C.nom AND C.ligne = D.ligne AND A.ligne <> C.ligne AND A.nom <> B.nom AND B.nom <> D.nom AND A.route_type IN (1,3) AND B.route_type IN (1,3) AND C.route_type IN (1,3) AND D.route_type IN (1,3)""")

            if _route_type == "ALL":
                print("ALL")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B.nom, C.ligne,  D.nom FROM noms_lignes as A, noms_lignes as B, noms_lignes as C, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND D.nom = $${_tostation}$$ AND A.ligne = B.ligne AND B.nom = C.nom AND C.ligne = D.ligne AND A.ligne <> C.ligne AND A.nom <> B.nom AND B.nom <> D.nom""")
            self.rows += self.cursor.fetchall()
            self.conn.commit()

        if _hops >= 3 :
            _route_type = str(self.typ_box.currentText())
            if _route_type == "Bus":
                print("BUS")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B2.nom, B2.ligne, C2.nom, C2.ligne, D.nom FROM noms_lignes as A, noms_lignes as B1, noms_lignes as B2, noms_lignes as C1, noms_lignes as C2, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND A.ligne = B1.ligne AND B1.nom = B2.nom AND B2.ligne = C1.ligne AND C1.nom = C2.nom AND C2.ligne = D.ligne AND D.nom = $${_tostation}$$ AND A.ligne <> B2.ligne AND B2.ligne <> C2.ligne AND A.ligne <> C2.ligne AND A.nom <> B1.nom AND B2.nom <> C1.nom AND C2.nom <> D.nom AND A.route_type = 3 AND B1.route_type = 3 AND B2.route_type = 3 AND C1.route_type = 3 AND C2.route_type = 3 AND D.route_type = 3""")
            if _route_type == "Metro":
                print("Metro")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B2.nom, B2.ligne, C2.nom, C2.ligne, D.nom FROM noms_lignes as A, noms_lignes as B1, noms_lignes as B2, noms_lignes as C1, noms_lignes as C2, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND A.ligne = B1.ligne AND B1.nom = B2.nom AND B2.ligne = C1.ligne AND C1.nom = C2.nom AND C2.ligne = D.ligne AND D.nom = $${_tostation}$$ AND A.ligne <> B2.ligne AND B2.ligne <> C2.ligne AND A.ligne <> C2.ligne AND A.nom <> B1.nom AND B2.nom <> C1.nom AND C2.nom <> D.nom AND A.route_type = 2 AND B1.route_type = 2 AND B2.route_type = 2 AND C1.route_type = 2 AND C2.route_type = 2 AND D.route_type = 2""")
            if _route_type == "RER":
                print("RER")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B2.nom, B2.ligne, C2.nom, C2.ligne, D.nom FROM noms_lignes as A, noms_lignes as B1, noms_lignes as B2, noms_lignes as C1, noms_lignes as C2, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND A.ligne = B1.ligne AND B1.nom = B2.nom AND B2.ligne = C1.ligne AND C1.nom = C2.nom AND C2.ligne = D.ligne AND D.nom = $${_tostation}$$ AND A.ligne <> B2.ligne AND B2.ligne <> C2.ligne AND A.ligne <> C2.ligne AND A.nom <> B1.nom AND B2.nom <> C1.nom AND C2.nom <> D.nom AND A.route_type = 1 AND B1.route_type = 1 AND B2.route_type = 1 AND C1.route_type = 1 AND C2.route_type = 1 AND D.route_type = 1""")

            if _route_type == "Tram":
                print("TRAM")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B2.nom, B2.ligne, C2.nom, C2.ligne, D.nom FROM noms_lignes as A, noms_lignes as B1, noms_lignes as B2, noms_lignes as C1, noms_lignes as C2, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND A.ligne = B1.ligne AND B1.nom = B2.nom AND B2.ligne = C1.ligne AND C1.nom = C2.nom AND C2.ligne = D.ligne AND D.nom = $${_tostation}$$ AND A.ligne <> B2.ligne AND B2.ligne <> C2.ligne AND A.ligne <> C2.ligne AND A.nom <> B1.nom AND B2.nom <> C1.nom AND C2.nom <> D.nom AND A.route_type = 0 AND B1.route_type = 0 AND B2.route_type = 0 AND C1.route_type = 0 AND C2.route_type = 0 AND D.route_type = 0""")

            if _route_type == "Walk":
                print("Walk")

                origin = int(self.coord1[0])
                print(origin)
                destination = int(self.coord2[0])
                print(destination)

                path=nx.dijkstra_path(self.G,origin,destination)
                print(path)
                coordinates = []
                for e in path:
                    self.cursor.execute(""f" select distinct latitude,longitude from network_node where stop_i = {e}""")
                    res = self.cursor.fetchall()
                    coordinates.append([float(res[0][1]),float(res[0][0])])
                print(coordinates)
                dep = coordinates[0]
                arv = coordinates[-1]

                self.webView.addMarker(dep[1],dep[0])
                self.webView.addMarker(arv[1],arv[0])
                self.webView.traceItineraire(coordinates,self.client)


            if _route_type == "RER/Metro":
                print("RER/Metro")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B2.nom, B2.ligne, C2.nom, C2.ligne, D.nom FROM noms_lignes as A, noms_lignes as B1, noms_lignes as B2, noms_lignes as C1, noms_lignes as C2, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND A.ligne = B1.ligne AND B1.nom = B2.nom AND B2.ligne = C1.ligne AND C1.nom = C2.nom AND C2.ligne = D.ligne AND D.nom = $${_tostation}$$ AND A.ligne <> B2.ligne AND B2.ligne <> C2.ligne AND A.ligne <> C2.ligne AND A.nom <> B1.nom AND B2.nom <> C1.nom AND C2.nom <> D.nom AND A.route_type IN (1,2) AND B1.route_type IN (1,2) AND B2.route_type IN (1,2) AND C1.route_type IN (1,2) AND C2.route_type IN (1,2) AND D.route_type IN (1,2)""")

            if _route_type == "RER/Bus":
                print("RER/Bus")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B2.nom, B2.ligne, C2.nom, C2.ligne, D.nom FROM noms_lignes as A, noms_lignes as B1, noms_lignes as B2, noms_lignes as C1, noms_lignes as C2, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND A.ligne = B1.ligne AND B1.nom = B2.nom AND B2.ligne = C1.ligne AND C1.nom = C2.nom AND C2.ligne = D.ligne AND D.nom = $${_tostation}$$ AND A.ligne <> B2.ligne AND B2.ligne <> C2.ligne AND A.ligne <> C2.ligne AND A.nom <> B1.nom AND B2.nom <> C1.nom AND C2.nom <> D.nom AND A.route_type IN (1,3) AND B1.route_type IN (1,3) AND B2.route_type IN (1,3) AND C1.route_type IN (1,3) AND C2.route_type IN (1,3) AND D.route_type IN (1,3)""")


            if _route_type == "ALL":
                print("ALL")
                self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B2.nom, B2.ligne, C2.nom, C2.ligne, D.nom FROM noms_lignes as A, noms_lignes as B1, noms_lignes as B2, noms_lignes as C1, noms_lignes as C2, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND A.ligne = B1.ligne AND B1.nom = B2.nom AND B2.ligne = C1.ligne AND C1.nom = C2.nom AND C2.ligne = D.ligne AND D.nom = $${_tostation}$$ AND A.ligne <> B2.ligne AND B2.ligne <> C2.ligne AND A.ligne <> C2.ligne AND A.nom <> B1.nom AND B2.nom <> C1.nom AND C2.nom <> D.nom""")
            self.rows += self.cursor.fetchall()
            self.conn.commit()

        if len(self.rows) == 0 :
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return

        numrows = len(self.rows)
        numcols = len(self.rows[-1])
        self.tableWidget.setRowCount(numrows)
        self.tableWidget.setColumnCount(numcols)

        i = 0
        for row in self.rows :
            j = 0
            for col in row :
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(col)))
                j = j + 1
            i = i + 1

        header = self.tableWidget.horizontalHeader()
        j = 0
        while j < numcols :
            header.setSectionResizeMode(j, QHeaderView.ResizeToContents)
            j = j+1

        self.update()


    def button_Clear(self):
        self.webView.clearMap(self.maptype_box.currentIndex())
        self.startingpoint = True
        self.update()


    def mouseClick(self, lat, lng):

        if (self.count % 2 == 0):
            self.webView.addPoint(lat, lng)
            _route_type = str(self.typ_box.currentText())
            if _route_type == "Bus":
                print("BUS")
                self.cursor.execute(""f" WITH tables_bus as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type = 3 and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_bus WHERE distance = (SELECT min(distance) FROM tables_bus)""")

            if _route_type == "Metro":
                print("Metro")
                self.cursor.execute(""f" WITH tables_metro as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type = 1 and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_metro WHERE distance = (SELECT min(distance) FROM tables_metro)""")

            if _route_type == "RER":
                print("RER")
                self.cursor.execute(""f" WITH tables_rer as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type = 2 and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_rer WHERE distance = (SELECT min(distance) FROM tables_rer)""")

            if _route_type == "RER/Metro":
                print("RER/Metro")
                self.cursor.execute(""f" WITH tables_rer_met as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type IN (1,2) and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_rer_met WHERE distance = (SELECT min(distance) FROM tables_rer_met)""")

            if _route_type == "RER/Bus":
                print("RER/Metro")
                self.cursor.execute(""f" WITH tables_rer_bus as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type IN (1,3) and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_rer_bus WHERE distance = (SELECT min(distance) FROM tables_rer_bus)""")

            if _route_type == "Tram":
                print("TRAM")
                self.cursor.execute(""f" WITH tables_tram as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type = 0 and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_tram WHERE distance = (SELECT min(distance) FROM tables_tram)""")

            if _route_type == "Walk":
                print("Walk")
                self.cursor.execute(""f" WITH montab as (SELECT nom,stop_i, CAST( latitude as FLOAT) as lat1 , CAST(longitude as FLOAT) as lng1,(ABS(CAST( latitude as FLOAT) - {lat} ) + ABS( CAST( longitude as FLOAT) - {lng})) as distance FROM network_node WHERE nom IN (SELECT nom from noms_lignes WHERE route_type IN  (0,1,2,3)) GROUP BY nom,stop_i,lat1,lng1,distance) SELECT montab.nom,montab.stop_i FROM montab WHERE montab.distance = (SELECT min(montab.distance) FROM montab)""")


            if _route_type == "ALL":
                print("ALL")
                self.cursor.execute(""f" WITH montab as (SELECT nom,stop_i, CAST( latitude as FLOAT) as lat1 , CAST(longitude as FLOAT) as lng1,(ABS(CAST( latitude as FLOAT) - {lat} ) + ABS( CAST( longitude as FLOAT) - {lng})) as distance FROM network_node WHERE nom IN (SELECT nom from noms_lignes WHERE route_type = 1) GROUP BY nom,lat1,lng1,distance) SELECT montab.nom FROM montab WHERE montab.distance = (SELECT min(montab.distance) FROM montab)""")


            print(f"1st-Clicked  on : latitude {lat}, longitude {lng}")
            self.conn.commit()
            myrows = self.cursor.fetchall()
            index = 0
            self.coord1.insert(0,float(myrows[0][1]))
            self.from_box.setCurrentIndex(self.from_box.findText(myrows[index][0], Qt.MatchFixedString))
            self.count = self.count + 1
        else:
            self.webView.addPoint(lat, lng)
            _route_type = str(self.typ_box.currentText())
            if _route_type == "Bus":
                print("BUS")
                self.cursor.execute(""f" WITH tables_bus as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type = 3 and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_bus WHERE distance = (SELECT min(distance) FROM tables_bus)""")

            if _route_type == "Metro":
                print("Metro")
                self.cursor.execute(""f" WITH tables_metro as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type = 1 and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_metro WHERE distance = (SELECT min(distance) FROM tables_metro)""")

            if _route_type == "RER":
                print("RER")
                self.cursor.execute(""f" WITH tables_rer as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type = 2 and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_rer WHERE distance = (SELECT min(distance) FROM tables_rer)""")

            if _route_type == "RER/Metro":
                print("RER/Metro")
                self.cursor.execute(""f" WITH tables_rer_met as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type IN (1,2) and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_rer_met WHERE distance = (SELECT min(distance) FROM tables_rer_met)""")

            if _route_type == "RER/Bus":
                print("RER/Metro")
                self.cursor.execute(""f" WITH tables_rer_bus as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type IN (1,3) and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_rer_bus WHERE distance = (SELECT min(distance) FROM tables_rer_bus)""")

            if _route_type == "Tram":
                print("TRAM")
                self.cursor.execute(""f" WITH tables_tram as (SELECT distinct noms_lignes.nom as nom,stop_i, CAST(latitude as FLOAT) as lat , CAST(longitude as FLOAT) as lng,(ABS( CAST(latitude as FLOAT)  - {lat} ) + ABS( CAST(longitude as FLOAT) - {lng}))  as distance  FROM noms_lignes,network_node WHERE route_type = 0 and noms_lignes.nom = network_node.nom ) SELECT nom,stop_i FROM tables_tram WHERE distance = (SELECT min(distance) FROM tables_tram)""")

            if _route_type == "Walk":
                print("Walk")
                self.cursor.execute(""f" WITH montab as (SELECT nom,stop_i, CAST( latitude as FLOAT) as lat1 , CAST(longitude as FLOAT) as lng1,(ABS(CAST( latitude as FLOAT) - {lat} ) + ABS( CAST( longitude as FLOAT) - {lng})) as distance FROM network_node WHERE nom IN (SELECT nom from noms_lignes WHERE route_type IN  (0,1,2,3)) GROUP BY nom,stop_i,lat1,lng1,distance) SELECT montab.nom,montab.stop_i FROM montab WHERE montab.distance = (SELECT min(montab.distance) FROM montab)""")


            if _route_type == "ALL":
                print("ALL")
                self.cursor.execute(""f" WITH montab as (SELECT nom,stop_i, CAST( latitude as FLOAT) as lat1 , CAST(longitude as FLOAT) as lng1,(ABS(CAST( latitude as FLOAT) - {lat} ) + ABS( CAST( longitude as FLOAT) - {lng})) as distance FROM network_node WHERE nom IN (SELECT nom from noms_lignes WHERE route_type = 1) GROUP BY nom,lat1,lng1,distance) SELECT montab.nom FROM montab WHERE montab.distance = (SELECT min(montab.distance) FROM montab)""")


            print(f"1st-Clicked  on : latitude {lat}, longitude {lng}")
            self.conn.commit()
            myrows = self.cursor.fetchall()
            index = 0
            self.coord2.insert(0,float(myrows[0][1]))
            self.to_box.setCurrentIndex(self.to_box.findText(myrows[index][0], Qt.MatchFixedString))
            self.count = self.count + 1



class myWebView (QWebEngineView):
    def __init__(self):
        super().__init__()

        self.maptypes = ["OpenStreetMap", "Stamen Terrain", "stamentoner", "cartodbpositron"]
        self.setMap(0)


    def add_customjs(self, map_object):
        my_js = f"""{map_object.get_name()}.on("click",
                 function (e) {{
                    var data = `{{"coordinates": ${{JSON.stringify(e.latlng)}}}}`;
                    console.log(data)}}); """
        e = Element(my_js)
        html = map_object.get_root()
        html.script.get_root().render()
        html.script._children[e.get_name()] = e

        return map_object


    def handleClick(self, msg):
        data = json.loads(msg)
        lat = data['coordinates']['lat']
        lng = data['coordinates']['lng']

        window.mouseClick(lat, lng)


    def addSegment(self, lat1, lng1, lat2, lng2):
        js = Template(
        """
        L.polyline(
            [ [{{latitude1}}, {{longitude1}}], [{{latitude2}}, {{longitude2}}] ], {
                "color": "red",
                "opacity": 1.0,
                "weight": 4,
                "line_cap": "butt"
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude1=lat1, longitude1=lng1, latitude2=lat2, longitude2=lng2 )

        self.page().runJavaScript(js)

    def addRoute(self,list):
        js = Template(
        """
        L.polyline(
            {{list}}, {
                "color": "#566573",
                "opacity": 1.0,
                "weight": 4,
                "line_cap": "butt"
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), list = list )

        self.page().runJavaScript(js)


    def addCol(self,lat,lng,col,msg):
        js = Template(
        """
        L.marker([{{latitude}}, {{longitude}}], {icon: L.AwesomeMarkers.icon({icon: 'spinner', prefix: 'fa', markerColor: 'red', spin:true}) }).addTo({{map}}).bindPopup('{{msg}}').openPopup();
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": '{{col}}',
                "popup": "{{msg}}",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": '{{col}}',
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng,col = "#B03A2E",msg = msg)
        self.page().runJavaScript(js)


    def addMarker(self, lat, lng):
        js = Template(
        """
         L.marker([{{latitude}},{{longitude}}], {icon: L.AwesomeMarkers.icon({icon: 'info', prefix: 'fa', markerColor: 'cadetblue'}) }).addTo({{map}});
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": "#17202A",
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#17202A",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def addPoint(self, lat, lng):
        js = Template(
        """
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": 'green',
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": 'green',
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def setMap (self, i):
        self.mymap = folium.Map(location=[48.8619, 2.3519], tiles=self.maptypes[i], zoom_start=12, prefer_canvas=True)

        self.mymap = self.add_customjs(self.mymap)

        page = WebEnginePage(self)
        self.setPage(page)

        data = io.BytesIO()
        self.mymap.save(data, close_file=False)

        self.setHtml(data.getvalue().decode())

    def clearMap(self, index):
        self.setMap(index)

    def traceItineraire(self,coordinates,client):
        route = client.directions(
            coordinates=coordinates,
            profile='foot-walking',
            format='geojson',
            options={"avoid_features": ["steps"]},
            validate=False,
        )
        folium.PolyLine(locations=[list(reversed(coord))
                                   for coord in route['features'][0]['geometry']['coordinates']]).add_to(self.mymap)


        self.mymap.save('map.html')

        mylist = []
        for coord in route['features'][0]['geometry']['coordinates']:
            mylist.append(list(reversed(coord)))
        self.addRoute(mylist)





class WebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        #print(msg)
        if 'coordinates' in msg:
            self.parent.handleClick(msg)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
