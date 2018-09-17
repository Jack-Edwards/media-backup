import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFileDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName('MainWindow')
        self.init_base_ui()
        self.show()

    def init_base_ui(self):
        self.init_menu_bar()
        self.init_status_bar()
        self.init_layouts()

        self.setGeometry(50, 50, 400, 500)
        self.setWindowTitle('Media-Backup')

    def init_menu_bar(self):
        menu_bar = self.menuBar()

        #  File menu
        file_menu = menu_bar.addMenu('&File')
        exit_action = QAction('&Exit', self)
        exit_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_action)

        #  Options menu
        options_menu = menu_bar.addMenu('&Options')
        preferences_action = QAction('&Preferences', self)
        #preferences_action.triggered.connect('do something')
        options_menu.addAction(preferences_action)
    
    def init_status_bar(self):
        self.statusBar().showMessage('Ready')

    def init_layouts(self):

        #  Define the central widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName('centralWidget')
        self.setCentralWidget(self.central_widget)

        #  Set the layout of the central widget
        self.gridLayout = QGridLayout(self.central_widget)
        self.gridLayout.setObjectName('gridLayout')

        #  Add the 'Source' lineEdit
        self.lineEdit_Source = QLineEdit(self.central_widget)
        self.lineEdit_Source.setReadOnly(True)
        self.lineEdit_Source.setPlaceholderText('Path to source files')
        self.lineEdit_Source.setObjectName('lineEdit_Source')
        self.lineEdit_Source.mouseReleaseEvent = lambda event:self.handle_line_edit_clicked(sender=self.lineEdit_Source)
        self.gridLayout.addWidget(self.lineEdit_Source, 0, 0, 1, 3)

        #  Add the 'Source' pushButton
        self.pushButton_LoadSource = QPushButton(self.central_widget)
        self.pushButton_LoadSource.setObjectName('pushButton_LoadSource')
        self.pushButton_LoadSource.setText('Load')
        self.gridLayout.addWidget(self.pushButton_LoadSource, 0, 3, 1, 1)

        #  Add the 'Backup' lineEdit
        self.lineEdit_Backup = QLineEdit(self.central_widget)
        self.lineEdit_Backup.setReadOnly(True)
        self.lineEdit_Backup.setPlaceholderText('Path to backup files')
        self.lineEdit_Backup.setObjectName('lineEdit_Backup')
        self.lineEdit_Backup.mouseReleaseEvent = lambda event:self.handle_line_edit_clicked(sender=self.lineEdit_Backup)
        self.gridLayout.addWidget(self.lineEdit_Backup, 1, 0, 1, 3)

        #  Add the 'Backup' pushButton
        self.pushButton_LoadBackup = QPushButton(self.central_widget)
        self.pushButton_LoadBackup.setObjectName('pushButton_LoadBackup')
        self.pushButton_LoadBackup.setText('Load')
        self.gridLayout.addWidget(self.pushButton_LoadBackup, 1, 3, 1, 1)

        #  Add the treeView
        self.treeView = QTreeView(self.central_widget)
        self.treeView.setFrameShape(QFrame.Box)
        self.treeView.setFrameShadow(QFrame.Sunken)
        self.treeView.setObjectName('treeView')
        self.gridLayout.addWidget(self.treeView, 2, 0, 1, 4)

        #  Add the line separator
        #self.line = QFrame(self.central_widget)
        #self.line.setMouseTracking(False)
        #self.line.setFrameShadow(QFrame.Raised)
        #self.line.setMidLineWidth(0)
        #self.line.setFrameShape(QFrame.VLine)
        #self.line.setObjectName('line')
        #self.gridLayout_Main.addWidget(self.line, 1, 1, 1, 1)

    def handle_line_edit_clicked(self, sender):
        #  https://stackoverflow.com/questions/40392127/mousereleaseevent-triggers-at-application-start-not-on-click-in-pyqt5
        sender_name = sender.objectName()
        self.statusBar().showMessage('{} was clicked'.format(sender_name))

app = QApplication(sys.argv)
GUI = MainWindow()
sys.exit(app.exec_())