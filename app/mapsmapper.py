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




class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.resize(800, 600)

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
        _label.setFixedSize(30,20)
        self.from_box = QComboBox()
        self.from_box.setEditable(True)
        self.from_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.from_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.from_box)

        _label = QLabel('  To: ', self)
        _label.setFixedSize(20,20)
        self.to_box = QComboBox()
        self.to_box.setEditable(True)
        self.to_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.to_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.to_box)

        _label = QLabel('Hops: ', self)
        _label.setFixedSize(20,20)
        self.hop_box = QComboBox()
        self.hop_box.addItems( ['1', '2', '3', '4', '5'] )
        self.hop_box.setCurrentIndex( 0 )
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.hop_box)

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
        self.conn = psycopg2.connect(database="city_mapper_db", user="postgres", host="localhost", password="postgres")
        self.cursor = self.conn.cursor()

        self.cursor.execute(""f" SELECT DISTINCT nom FROM network_node WHERE UPPER(nom) = nom """)
        self.conn.commit()
        rows = self.cursor.fetchall()

        for row in rows :
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))


    def table_Click(self):
        print("Row number double-clicked: ", self.tableWidget.currentRow())
        i = 0
        for col in self.rows[self.tableWidget.currentRow()] :
            print(f"{i} column value is: {col}")
            i = i + 1


    def button_Go(self):
        self.tableWidget.clearContents()

        _fromstation = str(self.from_box.currentText())
        _tostation = str(self.to_box.currentText())
        _hops = int(self.hop_box.currentText())

        self.rows = []



        if _hops >= 1 :
            self.cursor.execute(""f"SELECT DISTINCT route_I_counts FROM network_combined WHERE from_stop_i IN ( SELECT stop_i FROM network_node WHERE nom = $${_fromstation}$$)""")
            dep = self.cursor.fetchall()
            #on mets dans a tous les route_I qui sont dans route_I_counts
            a =set([])
            for element in dep :
                res = element[0]
                l = res.split(',')
                l = [x.split(':')[0] for x in l]
                u = set(l)
                a.update(u)

            print("a")


            self.cursor.execute(""f"SELECT DISTINCT route_I_counts FROM network_combined WHERE from_stop_i IN ( SELECT stop_i FROM network_node WHERE nom = $${_tostation}$$)""")
            arv = self.cursor.fetchall()
            b =set([])
            for element in arv :
                res = element[0]
                l = res.split(',')
                l = [x.split(':')[0] for x in l]
                u = set(l)
                b.update(u)
            print(b)
            c = b
            list_to = "("
            for r in c :
                list_to += "'" + str(r) + "'"+","

            list_to =  list_to.rstrip(',')
            if len(list_to) < 2 :
                #si l'intersection est vide on rajoute -1 pour pas que la requete crash
                list_to += "-1"
            list_to += ")"
            print(list_to)
            # apres suppresion de v  dans  u:v on l ajoute dans une liste qui sera la listedes route_I
            c = a
            #on fait l intersection de la liste des route_I de _fromstation et _tostation pour avoir la ligne qu ils ont en commun
            list_from = "("
            for r in c :
                list_from += "'" + str(r) + "'"+","

            list_from =  list_from.rstrip(',')
            if len(list_from) < 2 :
                #si l'intersection est vide on rajoute -1 pour pas que la requete crash
                list_from += "-1"
            list_from += ")"
            print("a+")
            print(list_from)

            self.cursor.execute(""f" with mytab as ((SELECT DISTINCT route_name FROM routes WHERE route_i IN {list_from}) INTERSECT (SELECT DISTINCT route_name FROM routes WHERE route_i IN {list_to})) SELECT DISTINCT A.nom,mytab.route_name,B.nom FROM mytab,network_node as A, network_node as B WHERE A.nom = $${_fromstation}$$ AND B.nom = $${_tostation}$$ """)
            self.rows = self.cursor.fetchall()
            self.conn.commit()

        if _hops >= 2:
            self.cursor.execute(""f"SELECT DISTINCT route_I_counts FROM network_combined WHERE from_stop_i IN ( SELECT stop_i FROM network_node WHERE nom = $${_fromstation}$$)""")
            dep = self.cursor.fetchall()
            #on mets dans a tous les route_I qui sont dans route_I_counts
            a =set([])
            for element in dep :
                res = element[0]
                l = res.split(',')
                l = [x.split(':')[0] for x in l]
                u = set(l)
                a.update(u)
                c = a
                depart = "("
                for r in c :
                    depart += "'" + str(r) + "'"+","

                depart =  depart.rstrip(',')
                if len(depart) < 2 :
                    #si l'intersection est vide on rajoute -1 pour pas que la requete crash
                    depart += "-1"
                depart += ")"
                print(depart)
            print("a")
            self.cursor.execute(""f"CREATE OR REPLACE VIEW depart as ( SELECT DISTINCT nom,route_name FROM routes,network_node WHERE route_i IN {depart} AND nom = $${_fromstation}$$) """)
            self.cursor.execute(""f" SELECT * FROM depart """)
            self.rows += self.cursor.fetchall()
            self.cursor.execute(""f"SELECT DISTINCT route_I_counts FROM network_combined WHERE from_stop_i IN ( SELECT stop_i FROM network_node WHERE nom = $${_tostation}$$)""")
            arv = self.cursor.fetchall()
            b =set([])
            for element in arv :
                res = element[0]
                l = res.split(',')
                l = [x.split(':')[0] for x in l]
                u = set(l)
                b.update(u)
            print(b)
            c = b
            arrivee = "("
            for r in c :
                arrivee += "'" + str(r) + "'"+","

            arrivee =  arrivee.rstrip(',')
            if len(arrivee) < 2 :
                #si l'intersection est vide on rajoute -1 pour pas que la requete crash
                arrivee += "-1"
            arrivee += ")"
            print(arrivee)
            self.cursor.execute(""f"CREATE OR REPLACE VIEW arrivee as ( SELECT DISTINCT nom,route_name FROM routes,network_node WHERE route_i IN {arrivee} AND nom = $${_tostation}$$) """)
            #self.cursor.execute(""f" SELECT * FROM arrivee """)


        self.conn.commit()
        #self.rows += self.cursor.fetchall()


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
        self.webView.addPoint(lat, lng)

        print(f"Clicked on: latitude {lat}, longitude {lng}")
        self.cursor.execute(""f" SELECT A.nom_long FROM metros as A """)
        self.conn.commit()
        myrows = self.cursor.fetchall()

        index = random.randint(0,len(myrows))
        self.from_box.setCurrentIndex(self.from_box.findText(myrows[index][0], Qt.MatchFixedString))



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


    def addMarker(self, lat, lng):
        js = Template(
        """
        L.marker([{{latitude}}, {{longitude}}] ).addTo({{map}});
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": "#3388ff",
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#3388ff",
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
