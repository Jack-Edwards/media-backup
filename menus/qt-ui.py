import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setObjectName('MainWindow')
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle('Media-Backup')

        self.init_menu_bar()
        self.init_status_bar()
        self.init_main_form()

    def init_menu_bar(self):
        menu_bar = self.menuBar()

        #  File menu
        file_menu = menu_bar.addMenu('File')
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_action)

        #  Options menu
        options_menu = menu_bar.addMenu('Options')
        preferences_action = QAction('Preferences', self)
        #preferences_action.triggered.connect('do something')
        options_menu.addAction(preferences_action)
    
    def init_status_bar(self):
        self.statusBar().showMessage('Ready')

    def init_main_form(self):
        #  Define the central widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName('centralWidget')
        self.setCentralWidget(self.central_widget)

        #  Set the layout of the central widget
        self.gridLayout = QGridLayout(self.central_widget)
        self.gridLayout.setObjectName('gridLayout')

        #  Add the 'Source' lineEdit
        self.lineEdit_Source = QLineEdit(self.central_widget)
        self.lineEdit_Source.setPlaceholderText('Source directory')
        self.lineEdit_Source.setObjectName('lineEdit_Source')
        self.gridLayout.addWidget(self.lineEdit_Source, 0, 0, 1, 4)

        #  Add the 'Browse' toolButton for the 'Source' lineEdit
        self.toolButton_BrowseForSource = QToolButton(self.central_widget)
        self.toolButton_BrowseForSource.setObjectName('toolButton_BrowseForSource')
        self.toolButton_BrowseForSource.setText('...')
        self.toolButton_BrowseForSource.clicked.connect(self.browse_button_clicked)
        self.gridLayout.addWidget(self.toolButton_BrowseForSource, 0, 4, 1, 1)

        #  Add the 'Load' pushButton for the 'Source' lineEdit
        self.pushButton_LoadSource = QPushButton(self.central_widget)
        self.pushButton_LoadSource.setObjectName('pushButton_BrowseForSource')
        self.pushButton_LoadSource.setText('Load')
        self.pushButton_LoadSource.clicked.connect(
            lambda : self.load_button_clicked(self.lineEdit_Source.text())
        )
        self.gridLayout.addWidget(self.pushButton_LoadSource, 0, 5, 1, 1)

        #  Add the 'Backup' lineEdit
        self.lineEdit_Backup = QLineEdit(self.central_widget)
        self.lineEdit_Backup.setPlaceholderText('Backup directory')
        self.lineEdit_Backup.setObjectName('lineEdit_Backup')
        self.gridLayout.addWidget(self.lineEdit_Backup, 1, 0, 1, 4)

        #  Add the 'Browse' toolButton for the 'Backup' lineEdit
        self.toolButton_BrowseForBackup = QToolButton(self.central_widget)
        self.toolButton_BrowseForBackup.setObjectName('toolButton_BrowseForBackup')
        self.toolButton_BrowseForBackup.setText('...')
        self.toolButton_BrowseForBackup.clicked.connect(self.browse_button_clicked)
        self.gridLayout.addWidget(self.toolButton_BrowseForBackup, 1, 4, 1, 1)

        #  Add the 'Load' pushButton for the 'Backup' lineEdit
        self.pushButton_LoadBackup = QPushButton(self.central_widget)
        self.pushButton_LoadBackup.setObjectName('pushButton_LoadBackup')
        self.pushButton_LoadBackup.setText('Load')
        self.pushButton_LoadBackup.clicked.connect(
            lambda : self.load_button_clicked(self.lineEdit_Backup.text())
        )
        self.gridLayout.addWidget(self.pushButton_LoadBackup, 1, 5, 1, 1)

        #  Add the treeView to the UI
        self.treeView = self.init_treeview(self.central_widget)
        self.gridLayout.addWidget(self.treeView, 2, 0, 1, 6)

        #  Set the treeView model
        self.treeView_model = TreeviewModel(self)
        self.treeView.setModel(self.treeView_model)

    def init_treeview(self, central_widget):
        tree_view = QTreeView(central_widget)
        tree_view.setFrameShape(QFrame.Box)
        tree_view.setFrameShadow(QFrame.Sunken)
        tree_view.setObjectName('treeView')
        return tree_view

    def browse_button_clicked(self):
        sender_name = self.sender().objectName()
        assert(sender_name == 'toolButton_BrowseForSource' or sender_name == 'toolButton_BrowseForBackup')
        
        #  Open a file-picker dialog
        source_or_backup = 'Source' if sender_name == 'toolButton_BrowseForSource' else 'Backup'
        caption = 'Select {} Directory'.format(source_or_backup)

        directory = self.show_file_dialog(caption)
        if directory is not None:
            if source_or_backup is 'Source':
                self.lineEdit_Source.setText(directory)
            else:
                self.lineEdit_Backup.setText(directory)

    def show_file_dialog(self, caption):
        #  Requires:
        #    'caption' should be a string.
        #  Guarantees:
        #    Returns 'None' if the user does not make a selection.
        #    Otherwise, returns the directory selected by the user, as a string.
        #  Notes:
        #    Showing the dialog in Linux throws this error:
        #     - 'GtkDialog mapped without a transient parent.  This is discouraged.'
        #    This cannot be avoided as this is a native dialog.
        #    Gtk has no knowledge of QT.
        #    Reference:  https://forum.qt.io/topic/85997/gtk-warning-for-native-qfiledialog-under-linux/11

        dialog = QFileDialog()

        #  todo - get this to work
        #dialog.setOption(QFileDialog.ShowDirsOnly)

        directory = dialog.getExistingDirectory(self, caption, '~/')
        return directory if directory else None

    def load_button_clicked(self, directory):
        assert(os.path.exists(directory))
        self.treeView_model.add_row('Deadpool', 123, 'Movie', '2018-01-01')

    def load_button_clicked_deprecated(self, directory):
        #  This is sample/test code only
        #  Do not use this method
        assert(os.path.exists(directory))

        treeview_model = QFileSystemModel()
        self.treeView.setModel(treeview_model)
        self.treeView.setRootIndex(
            treeview_model.setRootPath(directory)
        )

class TreeviewModel(QStandardItemModel):
    #  https://pythonspot.com/pyqt5-treeview/
    #  http://pyqt.sourceforge.net/Docs/PyQt4/qstandarditemmodel.html
    #  https://gist.github.com/skriticos/5415869
    def __init__(self, parent):
        #  super().__init__(rows, columns, parent)
        super().__init__(0, 4, parent)

        #  Column indexes
        self.NAME = 0
        self.SIZE = 1
        self.TYPE = 2
        self.DATE_MODIFIED = 3

        #  Load the treeview
        self.set_headers()
        self.set_parent_rows()

    def set_headers(self):
        self.setHeaderData(self.NAME, Qt.Horizontal, 'Name')
        self.setHeaderData(self.SIZE, Qt.Horizontal, 'Size')
        self.setHeaderData(self.TYPE, Qt.Horizontal, 'Type')
        self.setHeaderData(self.DATE_MODIFIED, Qt.Horizontal, 'Date Modified')

    def set_parent_rows(self):
        self.root = self.invisibleRootItem()
        self.source_item = MirrorItem('Source', None)
        self.backup_item = MirrorItem('Backup', None)

        self.root.appendRow(self.source_item.as_row())
        self.root.appendRow(self.backup_item.as_row())

    def row_model(self, name, size=None, type=None, date_modified=None):
        name_item = QStandardItem(name)
        size_item = QStandardItem(size)
        type_item = QStandardItem(type)
        date_item = QStandardItem(date_modified)
        return [
            name_item,
            size_item,
            type_item,
            date_item
        ]

    def get_selected_index(self):
        return


class MirrorItem(QStandardItem):
    def __init__(self, name, path):
        QStandardItem.__init__(self, name)
        self.name = name
        self.path = path

    def as_row(self):
        return [
            QStandardItem(self.name),
            QStandardItem(None),
            QStandardItem('Mirror'),
            QStandardItem(None)
        ]

app = QApplication(sys.argv)
GUI = MainWindow()
sys.exit(app.exec_())