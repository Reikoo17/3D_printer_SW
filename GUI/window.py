from utils.Event import subscribe, post_event
from PySide6.QtCore import QObject, Slot, Signal, QTimer
import serial.tools.list_ports

from utils.settings import GetSettingsManager

class MainWindow(QObject):
    # Signáli pro získání nastavení tiskárny
    getPorts = Signal(list)
    getBaudrates = Signal(list)

    getPort = Signal(str)
    getBaudrate = Signal(int)

    getNumOfExtruders = Signal(int)
    getBedStatus = Signal(bool)
    getChamberStatus = Signal(bool)

    getExtruderMaxTemperature = Signal(list)
    getBedMaxTemperature = Signal(int)
    getChamberMaxTemperature = Signal(int)

    getExtruderTemperature = Signal(list)
    getBedTemperature = Signal(list)
    getChamberTemperature = Signal(list)

    getPositions = Signal(list)

    getPrinterStatus = Signal(bool)


    # Signáli pro získání nastavení mqtt
    getMQTTIP = Signal(str)
    getMQTTPort = Signal(int)

    # Signáli pro získání nastavení MES
    getMESIP = Signal(str)
    getMESPort = Signal(int)

    def __init__(self):
        QObject.__init__(self)

        self.oldPort = None
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.updatePort())
        self.timer.start(2000)

        self.settings = GetSettingsManager()

        subscribe("temperature_update", self.update_temperature)
        subscribe("position_update", self.update_position)
        subscribe("printer_connection", self.update_printer_status)

    @Slot()
    def Debug(self):
        print("!!DEBUG!!")

    @Slot()
    def Init(self):
        """Inicializační funkce pro předání nastavení applikace do QML souboru."""
        self.getPort.emit(self.settings.setting["serial"]["port"])
        self.getBaudrate.emit(self.settings.setting["serial"]["baudrate"])

        self.updatePort()
        self.getBaudrates.emit(self.settings.setting["GUI"]["baudrates"])

        self.getMQTTIP.emit(self.settings.setting["MQTT"]["IP_address"])
        self.getMQTTPort.emit(self.settings.setting["MQTT"]["port"])

        self.getExtruderMaxTemperature.emit(self.settings.setting["printer"]["extruder"]["max_temp"])
        self.getBedMaxTemperature.emit(self.settings.setting["printer"]["bed"]["max_temp"])
        self.getChamberMaxTemperature.emit(self.settings.setting["printer"]["chamber"]["max_temp"])

    def updatePort(self):
        """
        Funkce pro updatování listu portu.
        :return:
        """
        ports = serial.tools.list_ports.comports()
        f_ports = []
        for port, dest, hwid in sorted(ports):
            f_ports.append(port)

        if self.oldPort == f_ports:
            print("same")
        else:
            self.getPorts.emit(f_ports)
            self.oldPort = f_ports
            print("notSame")

    def update_temperature(self, data):
        self.getExtruderTemperature.emit(data["tools"])
        self.getBedTemperature.emit(data["bed"])
        self.getChamberTemperature.emit(data["chamber"])

    def update_position(self, data):
        position_list = [data["X"], data["Y"], data["Z"]]
        self.getPositions.emit(position_list)

    @Slot(str, int)
    def send_GCode(self, axis, range):
        command = {"axis": axis,
                   "range": range
                   }
        post_event("printer_command_axis", command)

    @Slot()
    def print_connect(self):
        post_event("printer_connect", None)

    @Slot()
    def print_disconnect(self):
        post_event("printer_disconnect", None)

    def update_printer_status(self, status: str):
        if status == "CONNECTED":
            self.getPrinterStatus.emit(True)
        elif status == "DISCONNECTED":
            self.getPrinterStatus.emit(False)
        else:
            print("Neznamý stav")
