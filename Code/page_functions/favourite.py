"""

Favourite.py
This file contains the functions for the Favourite page.
- Show the favourite words in the list widget
- Delete the favourite words from the list widget

"""

from PyQt5.QtWidgets import QWidget, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QDialog, QLabel, QDialogButtonBox, QMessageBox
from ui.pages.Favourite_page_ui import Ui_Form
from PyQt5.QtGui import QFont
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QHBoxLayout, QAbstractItemView, QMenu, QAction
import sqlite3
from PyQt5.QtCore import Qt, QSize
import sys
import os

class Favourite(QWidget):
    def __init__(self):
        super(Favourite, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.listWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listWidget.customContextMenuRequested.connect(self.show_context_menu)
    
    def showEvent(self, event):
        english_word = None
        self.ui.listWidget.clear()
        
        # Connect to the SQLite database
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        db_name = "data.db"
        db_path = os.path.join(os.path.expanduser("~"), db_name)
        print(db_path)
        
        if not os.path.exists(db_path):
            print(f"Database file {db_path} does not exist")
            return
        else:
            print("Connected to database")
        
        self.db.setDatabaseName(db_path)

        # Open the database connection
        if not self.db.open():
            print("Failed to open database")
            return
        else:
            print("Database opened successfully")

        query = QSqlQuery()

        #Choose the vocab by filtering to show only one word vocab
        query.prepare("SELECT DISTINCT Favourite.Word FROM Favourite JOIN translation ON Favourite.Word = translation.body")
        query.exec_()

        delete_query = QSqlQuery()
        delete_query.prepare("DELETE FROM Favourite WHERE NOT EXISTS (SELECT 1 FROM Translate WHERE Favourite.Word = translation.body)")
        delete_query.exec_()

        while query.next():
            english_word = query.value(0)
            self.ui.listWidget.addItem(english_word)
    
        print("Reconnected to database successfully")

    def show_context_menu(self, pos):
        print("show_context_menu called")
        
        # Create a context menu
        menu = QMenu(self.ui.listWidget)

        delete_action = QAction("Delete the Favourite", self.ui.listWidget)
        delete_action.setEnabled(self.ui.listWidget.currentItem() is not None)
        delete_action.triggered.connect(self.delete_selected_text)
        menu.addAction(delete_action)
        print("Delete action added to context menu")
        print("Current item:", self.ui.listWidget.currentItem())

        # Show the context menu at the cursor position
        menu.exec_(self.ui.listWidget.mapToGlobal(pos))

    def delete_selected_text(self):
        print("delete_selected_text called")
        # Get the selected text from the QListWidget
        selected_text = self.ui.listWidget.currentItem().text()

        # Delete the selected text from the SQLite database
        query = QSqlQuery()
        query.prepare("DELETE FROM Favourite WHERE Word = :word")
        query.bindValue(":word", selected_text)
        query.exec_()
        self.db.commit()

        self.ui.listWidget.clear()
        query.prepare("SELECT DISTINCT Word from Favourite")
        query.exec_()

        while query.next():
            english_word = query.value(0)
            self.ui.listWidget.addItem(english_word)
        self.db.commit()
