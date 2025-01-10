from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QFileDialog


class MainWindow(QtWidgets.QWidget):
    def __init__(self, rows=3, cols=3, button_size=100):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.button_size = button_size

        # Main layout
        self.main_layout = QtWidgets.QGridLayout(self)

        # Grid layout for bottle buttons
        self.grid_layout = QtWidgets.QGridLayout()
        self.main_layout.addLayout(self.grid_layout, 0, 0, 1, 2)

        # Create a vertical layout for the right boxes
        self.right_vertical_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.right_vertical_layout, 1, 1)

        # Create the top-right group box
        self.top_right_group_box = QtWidgets.QGroupBox("Current State", self)
        self.create_top_right_box()
        self.right_vertical_layout.addWidget(self.top_right_group_box)

        # Create the bottom-right group box
        self.bottom_right_group_box = QtWidgets.QGroupBox("Bottle Information", self)
        self.create_bottom_right_box()
        self.right_vertical_layout.addWidget(self.bottom_right_group_box)

        # Create a QGroupBox to hold the 3x3 grid of bottle buttons
        self.button_group_box = QtWidgets.QGroupBox("Tray", self)
        self.create_group_box()
        self.main_layout.addWidget(self.button_group_box, 1, 0)

        # Create bottom layout with QLineEdit and QPushButton
        self.create_bottom_bar()

    def create_top_right_box(self):
        """Create the top-right group box."""
        layout = QtWidgets.QVBoxLayout(self.top_right_group_box)
        label = QtWidgets.QLabel("This is the top-right group box", self)
        layout.addWidget(label)
        self.top_right_group_box.setLayout(layout)

    def create_bottom_right_box(self):
        """Create the bottom-right group box."""
        layout = QtWidgets.QVBoxLayout(self.bottom_right_group_box)
        self.bottom_right_label = QtWidgets.QLabel(
            "This is the bottom-right group box", self
        )
        layout.addWidget(self.bottom_right_label)
        self.bottom_right_group_box.setLayout(layout)

    def create_group_box(self):
        """Create the QGroupBox with 3x3 bottle buttons."""
        grid_layout = QtWidgets.QGridLayout(self.button_group_box)
        self.button_group_box.setLayout(grid_layout)

        """
        0:100 1:99 2:98 3:97 4:96 5:95 6:94 7:93 8:92 9:91
        10:90 
        20:80
        
        """

        for row in range(self.rows):
            for col in range(self.cols):
                # Create button
                button = self.create_button(
                    f"{row*10+col}:{self.rows*self.cols-(row*10+col)}"
                )
                # Create line edit
                lineEdit = self.create_line_edit()

                # Add to grid layout
                self.grid_layout.addWidget(button, row, col)
                self.grid_layout.addWidget(lineEdit, row, col)

                # Connect signals
                button.clicked.connect(self.create_edit_handler(button, lineEdit))
                lineEdit.editingFinished.connect(self.update_bottom_right_box(lineEdit))
                lineEdit.editingFinished.connect(
                    self.create_edit_handler(lineEdit, button, reverse=True)
                )

                # Add the button to the grid layout
                grid_layout.addWidget(button, row, col)
                grid_layout.addWidget(lineEdit, row, col)

    def update_bottom_right_box(self, lineEdit):
        def handler():
            entered_text = lineEdit.text()
            self.bottom_right_label.setText(entered_text)

        return handler

    def create_bottom_bar(self):
        """Create a bottom bar with QLineEdit and QPushButton."""
        # Bottom layout
        bottom_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(bottom_layout, 3, 0, 1, 2)

        # Add QLineEdit
        self.bottom_line_edit = QtWidgets.QLineEdit(self)
        bottom_layout.addWidget(self.bottom_line_edit)

        # Add QPushButton
        self.bottom_button = QtWidgets.QPushButton("Save", self)
        bottom_layout.addWidget(self.bottom_button)

        # Connect the button's clicked signal
        self.bottom_button.clicked.connect(self.on_bottom_button_click)

    def on_bottom_button_click(self):
        """Handle the click event of the bottom button."""

        # Open a file dialog to select where to save the file
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:  # If the user selects a file path
            try:
                with open(file_path, "w") as file:
                    file.write(self.bottom_line_edit.text())  # Save the text content
                QtWidgets.QMessageBox.information(
                    self, "Success", "File saved successfully!"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Could not save file: {e}"
                )

    def create_button(self, text):
        """Create a QPushButton with a circular style."""
        button = QtWidgets.QPushButton(text, self)
        button.setMinimumSize(QtCore.QSize(self.button_size, self.button_size))
        button.setMaximumSize(QtCore.QSize(self.button_size, self.button_size))
        button.setStyleSheet(
            f"""
            QPushButton {{
                border: none;
                border-radius: {self.button_size // 2}px;  /* Half of the diameter for circular shape */
                background-color: #6495ED;
                color: white;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #4169E1;
            }}
            """
        )
        return button

    def create_line_edit(self):
        """Create a QLineEdit that is hidden initially."""
        lineEdit = QtWidgets.QLineEdit(self)
        lineEdit.setHidden(True)
        return lineEdit

    def create_edit_handler(self, source_widget, target_widget, reverse=False):
        """Create a handler to toggle between QPushButton and QLineEdit."""

        def handler():
            if reverse:  # When editing is finished
                target_widget.setText(source_widget.text())
                source_widget.setHidden(True)
                target_widget.setHidden(False)
            else:  # When button is clicked
                target_widget.setText(source_widget.text())
                source_widget.setHidden(True)
                target_widget.setHidden(False)
                target_widget.setFocus()

        return handler


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(rows=10, cols=10, button_size=40)
    window.setWindowTitle("Custom Button Grid with Bottom Bar")
    window.resize(400, 400)
    window.show()
    sys.exit(app.exec())
