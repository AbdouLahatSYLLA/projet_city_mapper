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

class TransportApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Définir le titre de la fenêtre et sa taille
        self.setWindowTitle("Transport App")
        self.resize(800, 600)

        # Créer la barre de menu
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Ajouter un menu "File" avec une option "Quit"
        self.file_menu = QMenu("File", self.menu_bar)
        self.menu_bar.addMenu(self.file_menu)
        self.quit_action = self.file_menu.addAction("Quit")
        self.quit_action.triggered.connect(self.close)

        # Ajouter un menu "Help" avec une option "About"
        self.help_menu = QMenu("Help", self.menu_bar)
        self.menu_bar.addMenu(self.help_menu)
        self.about_action = self.help_menu.addAction("About")

        # Créer la zone de carte
        self.map_view = QWebEngineView(self)
        self.map_view.load(QUrl("https://maps.google.com"))

        # Créer la zone de sélection de mode de transport
        self.transport_label = QLabel("Mode de transport:", self)
        self.transport_combo_box = QComboBox(self)
        self.transport_combo_box.addItems(["Voiture", "Bus", "Train", "Métro"])

        # Créer le bouton "Go"
        self.go_button = QPushButton("Go", self)
        self.go_button.clicked.connect(self.on_go_clicked)

        # Ajouter les éléments au layout horizontal
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.transport_label)
        self.h_layout.addWidget(self.transport_combo_box)
        self.h_layout.addWidget(self.go_button)

        # Ajouter la zone de carte et le layout horizontal au layout vertical
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.map_view)
        self.v_layout.addLayout(self.h_layout)

        # Définir le layout principal de la fenêtre
        self.setLayout(self.v_layout)

    def on_go_clicked(self):
        print("GO")
        # Cette fonction sera appel
