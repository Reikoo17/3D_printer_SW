import os
from pathlib import Path
import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal, QTimer

from printer.communicatio import Printer

from window import MainWindow


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Context
    main = MainWindow()
    engine.rootContext().setContextProperty("backend", main)

    engine.load(os.fspath(Path(__file__).resolve().parent / "content/App.qml"))
    if not engine.rootObjects():
        sys.exit(-1)

    #printer = Printer(port='COM5', baudrate=250000)
    #printer.connect()

    sys.exit(app.exec())
