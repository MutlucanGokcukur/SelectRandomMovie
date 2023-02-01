import sys
from PyQt5 import QtWidgets
import requests
from bs4 import BeautifulSoup
import pywhatkit as pyw
import random
import wikipedia
import webbrowser
import sqlite3

class Pencere(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.VeriCekme()
        self.Baglantı()
        self.unit_ui()

    #region Connection Function to SQLite 
    def Baglantı(self):
        self.baglantı=sqlite3.connect("WatchedBefore.db")
        self.cursor=self.baglantı.cursor()
        sorgu="Create table If not exists WatchedBefore (MovieName TEXT,IMDb Rating INT)"
        self.cursor.execute(sorgu)
        self.baglantı.commit()
    #endregion
    
    #region get movies from 'imdb top 250 movies' site
    def VeriCekme(self):
        self.url ="https://www.imdb.com/chart/top/"
        self.response=requests.get(self.url)
        self.html=self.response.content
        soup=BeautifulSoup(self.html,"html.parser")
        self.movies=soup.find_all("td",{"class":"titleColumn"})
        self.ratings=soup.find_all("td",{"class":"ratingColumn imdbRating"})
        self.movielist=[]
        self.ratinglist=[]
        for m,r in zip(self.movies,self.ratings):
            m=m.text
            r=r.text
            m=m.strip()
            r=r.strip()
            m=m.replace("\n","")
            r=r.replace("\n","")
            lst=m[:4:]    #Film sıralamasını aldık.
            lst=lst.strip()
            m=m[5::]    #Filmlerin başındaki sıralamaları sildim ve düzenledim.
            m=m.strip() #Baştaki ve sondaki gereksiz boşlukları sildim.  
            self.movielist.append(m)
            self.ratinglist.append(r)
        #endregion
        
    #region Elements in the Interface
    def unit_ui(self):
        self.app=QtWidgets.QApplication(sys.argv)
        self.pencere=QtWidgets.QWidget()
        self.etiket=QtWidgets.QLabel(self.pencere)
        self.secmebuton=QtWidgets.QPushButton("Select Random Movie")
        self.fragmanbuton=QtWidgets.QPushButton("Watch Trailer")
        self.watchedbutton=QtWidgets.QPushButton("Watched Before")
        self.searchwiki=QtWidgets.QPushButton("Search this movie on 'Wikipedia'")
        self.trailererror=QtWidgets.QLabel("")
        self.dizirating=QtWidgets.QLabel("")
        self.rastgeledizi=QtWidgets.QLabel("")
        self.etiket.setText("Welcome to the movie selection app!!!")
        self.pencere.setWindowTitle("Movie Selection Application")

        self.vbox=QtWidgets.QVBoxLayout()
        self.hbox=QtWidgets.QHBoxLayout()
        self.hbox.addStretch()
        self.hbox.addLayout(self.vbox)
        self.vbox.addWidget(self.etiket)
        self.vbox.addWidget(self.secmebuton)
        self.vbox.addWidget(self.dizirating)
        self.vbox.addWidget(self.rastgeledizi)
        self.vbox.addWidget(self.watchedbutton)
        self.vbox.addWidget(self.fragmanbuton)
        self.vbox.addWidget(self.trailererror)
        self.vbox.addWidget(self.searchwiki)
        self.vbox.addStretch()
        self.hbox.addStretch()
        self.pencere.setLayout(self.hbox)

        self.secmebuton.clicked.connect(self.click)
        self.fragmanbuton.clicked.connect(self.click)
        self.searchwiki.clicked.connect(self.click)
        self.watchedbutton.clicked.connect(self.click)
        self.pencere.show()
    #endregion

    #region Functions Of Buttons
    def click(self):
        sender=self.sender()
        if sender.text()=="Select Random Movie": 
            self.number=random.randint(0,len(self.movielist)-1)
            self.randommovie=self.movielist[self.number]
            self.rastgeledizi.setText(self.randommovie)
            self.dizirating.setText(self.ratinglist[self.number])
            self.trailererror.clear()
        elif sender.text()=="Watch Trailer":
            try:
                pyw.playonyt(self.randommovie+"Fragman")
            except:
                self.trailererror.setText("First you have to press the "+
                "'Select Random Movie'\nbutton and let the movie be selected")
        elif sender.text()=="Search this movie on 'Wikipedia'":
            try:
                wiki=wikipedia.page(self.randommovie)
                link=wiki.url
                webbrowser.open(link)
            except:
                self.trailererror.setText("First you have to press the "+
                "'Select Random Movie'\nbutton and let the movie be selected")
        else:
            try:
                self.watchedmovie=self.rastgeledizi.text()
                self.watchedmovierating=self.dizirating.text()
                if self.watchedmovie!="":
                    self.cursor.execute("Insert into WatchedBefore VALUES(?,?)",(self.watchedmovie,self.watchedmovierating))
                    self.baglantı.commit()
                    self.movielist.remove(self.watchedmovie)
                    self.ratinglist.remove(self.watchedmovierating)
                    self.rastgeledizi.clear()
                    self.dizirating.clear()
            except:                
                self.trailererror.setText("First you have to press the "+
                "'Select Random Movie'\nbutton and let the movie be selected")
    #endregion
    
app=QtWidgets.QApplication(sys.argv)
pencere=Pencere()
sys.exit(app.exec_())