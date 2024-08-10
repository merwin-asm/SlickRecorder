import sys
import json
import os
import time
import threading
from screeninfo import get_monitors
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLineEdit, QPushButton, QFileDialog, QLabel, QGridLayout, QScrollArea, QDialog, QComboBox)
from PyQt5.QtGui import QPalette, QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt

class DefaultCursorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Default Cursor')
        self.setStyleSheet('background-color: white;')
        self.initUI()
    
    def current_path(self):
        x = os.path.abspath(__file__).split('/')
        x.pop()
        return "/".join(x)

    def initUI(self):
        gridLayout = QGridLayout()
        images = [f'{self.current_path()}/cursor{i}.png' for i in range(1, 8)]  # cursor1.png to cursor7.png
        
        for index, img_file in enumerate(images):
            button = QPushButton()
            pixmap = QPixmap(img_file)
            icon = QIcon(pixmap)  # Create a QIcon from QPixmap
            button.setIcon(icon)
            button.setIconSize(pixmap.size())
            button.setFixedSize(pixmap.size())
            button.clicked.connect(lambda checked, f=img_file: self.selectCursor(f))
            
            # Set button background to white and text color to black
            button.setStyleSheet('background-color: white; color: black; border: 1px solid #ddd;')
            
            gridLayout.addWidget(button, index // 3, index % 3)
        
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        container = QWidget()
        container.setLayout(gridLayout)
        scrollArea.setWidget(container)
        
        dialogLayout = QVBoxLayout()
        dialogLayout.addWidget(QLabel('Select Default Cursor'), 0, Qt.AlignTop)
        dialogLayout.addWidget(scrollArea)
        self.setLayout(dialogLayout)
        self.resize(500, 400)
    
    def selectCursor(self, file_name):
        print(f'Selected default cursor: {file_name}')
        self.cursor = file_name
        self.accept()  # Close the dialog after selection

class ScreenRecorderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.cursor = ""
        self.rec = False
        self.initUI()
        
    def initUI(self):
        # Set up dark theme
        self.setWindowTitle('Slick Recorder')
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.Text, QColor(240, 240, 240))
        self.setPalette(palette)
        
        # Layouts
        mainLayout = QVBoxLayout()
        imageLayout = QVBoxLayout()
        fpsLayout = QHBoxLayout()
        cursorLayout = QVBoxLayout()
        savingLocationLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()
        areaSelectionLayout = QHBoxLayout()
        
        # Add Image at the Top
        self.imageLabel = QLabel()
        self.imagePixmap = QPixmap(f'{self.current_path()}/title.png')  # Change this to your image path
        self.imageLabel.setPixmap(self.imagePixmap)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setFixedHeight(100)  # Fixed height for image
        imageLayout.addWidget(self.imageLabel)
        
        # UI Elements
        self.recordMicCheckbox = QCheckBox('Record from Mic')
        self.recordPCCheckbox = QCheckBox('Record from PC')
        self.showKeyboardCheckbox = QCheckBox('Show Keyboard Actions')
        """ 
        self.dynamicFPSCheckbox = QCheckBox('Dynamic FPS')
        self.customFPSInput = QLineEdit()
        self.customFPSInput = QLineEdit()
        self.customFPSInput.setPlaceholderText('Enter Custom FPS')
        self.customFPSInput.setEnabled(False)
        """
        self.codecComboBox = QComboBox()
        self.codecComboBox.addItems(['MP4V', 'MJPEG', 'XVID', 'DIVX'])
        
        self.voiceCaptionCheckbox = QCheckBox('Voice Caption Generation')
        """ 
        self.dynamicFPSCheckbox.setChecked(True)
        self.dynamicFPSCheckbox.toggled.connect(self.toggleFPSInput)
        """
        self.customCursorButton = QPushButton('Select Custom Cursor')
        self.changeDefaultCursorButton = QPushButton('Change Default Cursor')
        
        self.savingLocationInput = QLineEdit()
        self.browseButton = QPushButton('Browse')
        
        # Set default saving location to /home/{username}/Videos
        self.savingLocationInput.setText(os.path.expanduser('~/Videos'))
        
        self.startButton = QPushButton('Start Recording')
        self.stopButton = QPushButton('Stop (ESC)')
        
        self.monitorComboBox = QComboBox()
        
        # Get all monitors
        monitors = get_monitors()

        # Create a list of monitor IDs
        monitor_ids = [str(idx) for idx in range(len(monitors))]

        self.monitorComboBox.addItems(monitor_ids)  # Update as needed
        
        self.fullscreenCheckbox = QCheckBox('Full Screen')
        self.fullscreenCheckbox.setChecked(True)  # Enable fullscreen by default
        
        self.xStartInput = QLineEdit()
        self.xStartInput.setPlaceholderText('X Start')
        self.xEndInput = QLineEdit()
        self.xEndInput.setPlaceholderText('X End')
        self.yStartInput = QLineEdit()
        self.yStartInput.setPlaceholderText('Y Start')
        self.yEndInput = QLineEdit()
        self.yEndInput.setPlaceholderText('Y End')
        
        self.xStartInput.setEnabled(False)
        self.xEndInput.setEnabled(False)
        self.yStartInput.setEnabled(False)
        self.yEndInput.setEnabled(False)
        
        # Add elements to layout
        """
        fpsLayout.addWidget(QLabel('FPS:'), 0, Qt.AlignLeft)
        fpsLayout.addWidget(self.dynamicFPSCheckbox)
        fpsLayout.addWidget(self.customFPSInput)
        """
        fpsLayout.addWidget(QLabel('Codec:'), 0, Qt.AlignLeft)
        fpsLayout.addWidget(self.codecComboBox)
        
        cursorLayout.addWidget(QLabel('Default Cursor Settings'), 0, Qt.AlignTop)
        cursorLayout.addWidget(self.customCursorButton)
        cursorLayout.addWidget(self.changeDefaultCursorButton)
        
        savingLocationLayout.addWidget(self.savingLocationInput)
        savingLocationLayout.addWidget(self.browseButton)
        
        buttonLayout.addWidget(self.startButton)
        buttonLayout.addWidget(self.stopButton)
        
        areaSelectionLayout.addWidget(self.fullscreenCheckbox)
        areaSelectionLayout.addWidget(QLabel('X Start:'))
        areaSelectionLayout.addWidget(self.xStartInput)
        areaSelectionLayout.addWidget(QLabel('X End:'))
        areaSelectionLayout.addWidget(self.xEndInput)
        areaSelectionLayout.addWidget(QLabel('Y Start:'))
        areaSelectionLayout.addWidget(self.yStartInput)
        areaSelectionLayout.addWidget(QLabel('Y End:'))
        areaSelectionLayout.addWidget(self.yEndInput)
        
        mainLayout.addLayout(imageLayout)  # Add image layout at the top
        mainLayout.addWidget(self.recordMicCheckbox)
        mainLayout.addWidget(self.recordPCCheckbox)
        mainLayout.addLayout(fpsLayout)
        mainLayout.addWidget(self.voiceCaptionCheckbox)
        mainLayout.addWidget(self.showKeyboardCheckbox)
        mainLayout.addLayout(cursorLayout)
        mainLayout.addLayout(savingLocationLayout)
        mainLayout.addWidget(QLabel('Monitor:'))
        mainLayout.addWidget(self.monitorComboBox)
        mainLayout.addLayout(areaSelectionLayout)  # Add area layout with coordinates
        mainLayout.addLayout(buttonLayout)
        
        # Connect buttons to functions
        self.customCursorButton.clicked.connect(self.selectCustomCursor)
        self.changeDefaultCursorButton.clicked.connect(self.changeDefaultCursor)
        self.browseButton.clicked.connect(self.browseSavingLocation)
        self.startButton.clicked.connect(self.startRecording)
        self.stopButton.clicked.connect(self.stopRecording)
        self.fullscreenCheckbox.toggled.connect(self.toggleAreaInputs)
        
        self.setLayout(mainLayout)
        self.setFixedSize(800, 600)
        
        # Apply dark theme style
        self.setStyleSheet("""
            QWidget {
                background-color: #2c2c2c;
                color: #f0f0f0;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                color: #f0f0f0;
            }
            QPushButton#startButton {
                background-color: #4caf50;  /* Green for start */
            }
            QPushButton#stopButton {
                background-color: #f44336;  /* Red for stop */
                color: white;
            }
            QLineEdit {
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                background-color: #333;
                color: #f0f0f0;
            }
            QCheckBox {
                color: #f0f0f0;
            }
            QComboBox {
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                background-color: #333;
                color: #f0f0f0;
            }
        """)

        self.startButton.setStyleSheet("background-color: #4caf50; color: white;")
        #self.stopButton.setStyleSheet("background-color: red; color: white;")

    def toggleFPSInput(self, checked):
        self.customFPSInput.setEnabled(not checked)
    
    def selectCustomCursor(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select Custom Cursor', '', 'Images (*.png *.xpm *.jpg)', options=options)
        if file_name:
            self.cursor = file_name
            print(f'Selected custom cursor: {file_name}')
    
    def changeDefaultCursor(self):
        dialog = DefaultCursorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.cursor = dialog.cursor
            print(f'Selected default cursor: {self.cursor}')
            
    def browseSavingLocation(self):
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(self, 'Select Saving Location', options=options)
        if folder:
            self.savingLocationInput.setText(folder)
    
    def startRecording(self):
        # Collect data from UI elements
        if self.rec:
            return 0
        else:
            self.rec = True
        
        cursor = self.cursor 
        data = {
        'record_mic': self.recordMicCheckbox.isChecked(),
        'record_pc': self.recordPCCheckbox.isChecked(),
        'show_keyboard': self.showKeyboardCheckbox.isChecked(),
        'codec': self.codecComboBox.currentText(),
        'voice_caption': self.voiceCaptionCheckbox.isChecked(),
        'cursor':cursor,
        'saving_location': self.savingLocationInput.text(),
        'monitor': self.monitorComboBox.currentText(),
        'fullscreen': self.fullscreenCheckbox.isChecked(),
        'x_start': self.xStartInput.text() if not  self.fullscreenCheckbox.isChecked() else None,
        'x_end': self.xEndInput.text() if not self.fullscreenCheckbox.isChecked() else None,
        'y_start': self.yStartInput.text() if not  self.fullscreenCheckbox.isChecked() else None,
        'y_end': self.yEndInput.text() if not self.fullscreenCheckbox.isChecked() else None
        }

        # Print the collected data
        print("Recording Settings:")
        for key, value in data.items():
            print(f"{key}: {value}")

        if (not data['record_pc']) and (not data['record_mic']):
            os.system("touch .started_recording")
            ttt = True
        else:
            ttt = False

        data = json.dumps(data) 
        
        f = open(".settings.json", "w")
        f.write(data)
        f.close()
        
        x = lambda : os.system(f"python3 {self.current_path()}/SlickRecorder.py")
        y = lambda : os.system(f"python3 {self.current_path()}/start_icon.py")
        threading.Thread(target=x).start()
        
        while not os.path.isfile(".started_recording"):
            time.sleep(0.3)
        
        if ttt:
            time.sleep(4)

        threading.Thread(target=y).start()
        self.startButton.setStyleSheet("background-color: red; color: white;")

    def current_path(self):
        x = os.path.abspath(__file__).split('/')
        x.pop()
        return "/".join(x)

    def stopRecording(self):
        import pyautogui
        pyautogui.press('esc')
        self.rec = False
        self.startButton.setStyleSheet("background-color: #4caf50; color: white;")
        os.system("touch .stop_icon")
        os.system("rm .started_recording")

    def toggleAreaInputs(self, checked):
        self.xStartInput.setEnabled(not checked)
        self.xEndInput.setEnabled(not checked)
        self.yStartInput.setEnabled(not checked)
        self.yEndInput.setEnabled(not checked)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScreenRecorderUI()
    window.show()
    sys.exit(app.exec_())

