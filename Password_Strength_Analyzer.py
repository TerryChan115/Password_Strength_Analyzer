import sys
import re
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit,QProgressBar, QLabel, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class PasswordAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Strength Analyzer")
        self.setGeometry(100, 100, 400, 400)
        self.setStyleSheet("background-color: #f0f0f0;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 8px; font-size: 14px;")
        self.password_input.textChanged.connect(self.update_strength)
        layout.addWidget(self.password_input)
        
        self.show_password_checkbox = QCheckBox("Show Password")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #ff0000;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.strength_bar)

        self.strength_label = QLabel("Strength: Very Weak")
        self.strength_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.strength_label)

        self.criteria = {
            "length": QLabel("✓ At least 8 characters"),
            "upper": QLabel("✓ Contains uppercase letters"),
            "lower": QLabel("✓ Contains lowercase letters"),
            "digit": QLabel("✓ Contains digits"),
            "symbol": QLabel("✓ Contains symbols"),
        }
        for label in self.criteria.values():
            label.setStyleSheet("color: #666; font-size: 14px;")
            layout.addWidget(label)
        
        # Cracking Time
        self.crack_time_label = QLabel("Estimated time to crack: Instant")
        self.crack_time_label.setStyleSheet("font-size: 14px; color: #444;")
        layout.addWidget(self.crack_time_label)
        
        self.update_strength()

    def toggle_password_visibility(self, state):
        if state == Qt.CheckState.Checked.value:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def calculate_entropy(self, password):
        char_pools = {
            'lower': 26,
            'upper': 26,
            'digits': 10,
            'symbols': 32
        }
        pool_size = 0
        if re.search(r'[a-z]', password):
            pool_size += char_pools['lower']
        if re.search(r'[A-Z]', password):
            pool_size += char_pools['upper']
        if re.search(r'[0-9]', password):
            pool_size += char_pools['digits']
        if re.search(r'[^\w\s]', password):
            pool_size += char_pools['symbols']
        entropy = len(password) * math.log2(pool_size) if pool_size > 0 else 0
        return entropy

    def password_strength(self, password):
        strength = {
            'length': len(password) >= 8,
            'lower': re.search(r'[a-z]', password) is not None,
            'upper': re.search(r'[A-Z]', password) is not None,
            'digit': re.search(r'[0-9]', password) is not None,
            'symbol': re.search(r'[^\w\s]', password) is not None,
            'entropy': self.calculate_entropy(password)
        }
        entropy = strength['entropy']
        time_to_crack = (2 ** entropy) / 1e12

        if time_to_crack < 1:
            time_str = "Instant"
        elif time_to_crack < 60:
            time_str = f"{time_to_crack:.2f} seconds"
        else:
            years = time_to_crack / (60 * 60 * 24 * 365)
            time_str = f"{years:.2f} years" if years > 1 else f"{years*365:.2f} days"

        return strength, time_str

    def update_strength(self):
        password = self.password_input.text()
        strength, time_str = self.password_strength(password)

        entropy = strength['entropy']
        progress = min(int((entropy / 128) * 100), 100)
        self.strength_bar.setValue(progress)

        if progress < 33:
            color = "#ff0000"
            strength_text = "Very Weak"
        elif progress < 66:
            color = "#ffd700"
            strength_text = "Moderate"
        else:
            color = "#00ff00"
            strength_text = "Strong"
    
        self.strength_bar.setStyleSheet(f"""
            QProgressBar::chunk {{ background-color: {color}; }}
        """)
        self.strength_label.setText(f"Strength: {strength_text}")
        self.crack_time_label.setText(f"Estimated time to crack: {time_str}")
    
        criteria_checks = {
            "length": strength['length'],
            "upper": strength['upper'],
            "lower": strength['lower'],
            "digit": strength['digit'],
            "symbol": strength['symbol'],
        }
        for key, label in self.criteria.items():
            if criteria_checks[key]:
                label.setStyleSheet("color: #00aa00; font-size: 14px;")
            else:
                label.setStyleSheet("color: #666; font-size: 14px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordAnalyzerApp()
    window.show()
    sys.exit(app.exec())