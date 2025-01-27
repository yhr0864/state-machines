from UI_design import Ui_MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
