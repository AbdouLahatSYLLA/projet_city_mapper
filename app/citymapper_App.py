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
    count = 0
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
        _label.setFixedSize(20,20)
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
        self.conn = psycopg2.connect(database="app_citymapper_db", user="postgres", host="localhost", password="postgres")
        self.cursor = self.conn.cursor()

        self.cursor.execute(""f" SELECT DISTINCT nom FROM noms_lignes WHERE UPPER(nom) = nom """)
        self.conn.commit()
        rows = self.cursor.fetchall()

        for row in rows :
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))


    def table_Click(self):
        print("Row number double-clicked: ", self.tableWidget.currentRow())
        i = 0
        listseg = []
        for col in self.rows[self.tableWidget.currentRow()] :
            chaine = str(col)
            #reste à recuperer lat et lng ensuite continuer ... :)
            print(f"{i} column value is: {chaine}")
            self.cursor.execute(""f"SELECT distinct latitude,longitude FROM network_node WHERE nom = $${chaine}$$ """)

            self.conn.commit()
            mylist = self.cursor.fetchall()
            if(mylist != []):
                item = mylist.pop(0)
                lat = item[0]
                lng = item[1]

                listseg.insert(0,lng)
                listseg.insert(0,lat)
                self.webView.addMarker(lat,lng)

        lng1 = listseg.pop(-1)
        lat1 = listseg.pop(-1)
        while(listseg != []):
            print(lat1)
            print(lng1)
            self.webView.addSegment(lat1,lng1,listseg[-2],listseg[-1])
            lng1 = listseg.pop(-1)
            lat1 = listseg.pop(-1)
        return i



    def button_Go(self):
        self.tableWidget.clearContents()

        _fromstation = str(self.from_box.currentText())
        _tostation = str(self.to_box.currentText())
        _hops = int(self.hop_box.currentText())

        self.rows = []
        if _hops >= 1 :

            self.cursor.execute(""f" SELECT DISTINCT A.nom,A.ligne,B.nom FROM noms_lignes as A, noms_lignes as B WHERE B.nom = $${_tostation}$$ and A.nom = $${_fromstation}$$ AND A.ligne = B.ligne """)
            self.rows += self.cursor.fetchall()
            self.conn.commit()

        if _hops >= 2 :
            self.cursor.execute(""f" SELECT distinct A.nom, A.ligne, B.nom, C.ligne,  D.nom FROM noms_lignes as A, noms_lignes as B, noms_lignes as C, noms_lignes as D WHERE A.nom = $${_fromstation}$$ AND D.nom = $${_tostation}$$ AND A.ligne = B.ligne AND B.nom = C.nom AND C.ligne = D.ligne AND A.ligne <> C.ligne AND A.nom <> B.nom AND B.nom <> D.nom""")
            self.rows += self.cursor.fetchall()
            self.conn.commit()

        if _hops >= 3 :
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
            print(f"1st-Clicked  on : latitude {lat}, longitude {lng}")
            self.cursor.execute(""f" WITH montab as (SELECT nom, CAST( latitude as FLOAT) as lat1 , CAST(longitude as FLOAT) as lng1,(ABS(CAST( latitude as FLOAT) - {lat} ) + ABS( CAST( latitude as FLOAT) - {lng})) as distance FROM network_node GROUP BY nom,lat1,lng1,distance) SELECT montab.nom FROM montab WHERE montab.distance = (SELECT min(montab.distance) FROM montab)""")
            self.conn.commit()
            myrows = self.cursor.fetchall()
            index = 0
            self.from_box.setCurrentIndex(self.from_box.findText(myrows[index][0], Qt.MatchFixedString))
            self.count = self.count + 1
        else:
            self.webView.addPoint(lat, lng)
            print(f"2nd-Clicked  on : latitude {lat}, longitude {lng}")
            self.cursor.execute(""f" WITH montab as (SELECT nom, CAST( latitude as FLOAT) as lat1 , CAST(longitude as FLOAT) as lng1,(ABS(CAST( latitude as FLOAT) - {lat} ) + ABS( CAST( latitude as FLOAT) - {lng})) as distance FROM network_node GROUP BY nom,lat1,lng1,distance) SELECT montab.nom FROM montab WHERE montab.distance = (SELECT min(montab.distance) FROM montab)""")
            self.conn.commit()
            myrows = self.cursor.fetchall()
            index = 0
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
