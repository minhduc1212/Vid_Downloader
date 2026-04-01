import os
import sys
from PySide6.QtWidgets import QApplication

# Ensure src module can be imported properly from command line
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui_main import FlatDesignUI

def main():
    app = QApplication(sys.argv)
    window = FlatDesignUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()