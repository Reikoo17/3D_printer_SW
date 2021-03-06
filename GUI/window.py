from utils.Event import subscribe, fire_event
from PySide2.QtCore import QObject, Slot, Signal, QTimer
import serial.tools.list_ports

from utils.settings import GetSettingsManager
from utils.script import GetScriptsManager

class MainWindow(QObject):
    """Třída pro kontrolu GUI. Jedná se o objekt, který pomocí objektu Signal(typ)
     komunikuje s front-endem GUI aplikace."""
    getPorts = Signal(list)
    getBaudrates = Signal(list)

    getPort = Signal(str)
    getBaudrate = Signal(int)

    getSerialAutoconnect = Signal(bool)
    getNumOfExtruders = Signal(int)

    getBedStatus = Signal(bool)
    getChamberStatus = Signal(bool)

    getExtruderMaxTemperature = Signal(int)
    getBedMaxTemperature = Signal(int)
    getChamberMaxTemperature = Signal(int)

    getExtruderTemperature = Signal(list)
    getBedTemperature = Signal(float)
    getChamberTemperature = Signal(float)

    getExtruderTargetTemperature = Signal(list)
    getBedTargetTemperature = Signal(float)
    getChamberTargetTemperature = Signal(float)

    getPositions = Signal(list)

    getPrinterStatus = Signal(bool)
    getPrinterPrinting = Signal(bool)
    getPrinterPause = Signal(bool)

    getPrinter_temp_interval = Signal(int)
    getPrinter_position_interval = Signal(int)

    getScriptList = Signal(list)
    getScriptText = Signal(str)

    # Signáli pro získání nastavení mqtt
    getMQTT_name = Signal(str)
    getMQTTIP = Signal(str)
    getMQTTPort = Signal(int)
    getMQTT_status = Signal(bool)
    getMQTT_auto_connect = Signal(bool)

    # Signáli pro získání nastavení MES
    getMESIP = Signal(str)
    getMESPort = Signal(int)

    getMES_URL = Signal(str)
    # Signáli pro zíkání nastavení automatického systému

    getSystem_status = Signal(bool)
    getRemoval_status = Signal(bool)

    getRemovalDialog = Signal(bool)
    getWarningDialog = Signal(str)

    extruder_target_temperature: list = [0]
    bed_target_temperature: float = 0
    chamber_target_temperature: float = 0

    def __init__(self):
        QObject.__init__(self)

        self.oldPort = None
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.updatePort())
        self.timer.start(2000)

        self.settings = GetSettingsManager()
        self.scripts = GetScriptsManager()
        subscribe("temperature_update", self.update_temperature)
        subscribe("position_update", self.update_position)
        subscribe("printer_connection", self.update_printer_status)
        subscribe("MQTT_connection_status", self.mqtt_connection_state)
        subscribe("GUI_removal_dialog", self.RemovalDialog)
        subscribe("printer_state", self.update_printer_state)
        subscribe("Serial_ERROR", self.WarningDialog)

    @Slot()
    def Debug(self):
        print("!!DEBUG!!")

    @Slot()
    def Init(self):
        """Inicializační funkce pro předání nastavení applikace do QML souboru."""
        self.getPort.emit(self.settings.setting["serial"]["port"])
        self.getBaudrate.emit(self.settings.setting["serial"]["baudrate"])
        self.getSerialAutoconnect.emit(self.settings.setting["serial"]["auto_connect"])
        self.updatePort()
        self.getBaudrates.emit(self.settings.setting["GUI"]["baudrates"])

        self.getMQTT_name.emit(self.settings.setting["MQTT"]["name"])
        self.getMQTTIP.emit(self.settings.setting["MQTT"]["IP_address"])
        self.getMQTTPort.emit(self.settings.setting["MQTT"]["port"])
        self.getMQTT_auto_connect.emit(self.settings.setting["MQTT"]["auto_connect"])

        self.getMES_URL.emit(self.settings.setting["MES"]["url"])

        self.getSystem_status.emit(self.settings.setting["system"]["status"])

        if self.settings.setting["system"]["removal"] == "manual":
            self.getRemoval_status.emit(False)
        elif self.settings.setting["system"]["removal"] == "auto":
            self.getRemoval_status.emit(True)

        self.getExtruderMaxTemperature.emit(self.settings.setting["printer"]["extruder"]["max_temp"])
        self.getBedMaxTemperature.emit(self.settings.setting["printer"]["bed"]["max_temp"])
        self.getChamberMaxTemperature.emit(self.settings.setting["printer"]["chamber"]["max_temp"])

        self.getBedStatus.emit(self.settings.setting["printer"]["bed"]["state"])
        self.getChamberStatus.emit(self.settings.setting["printer"]["chamber"]["state"])

        self.getScriptList.emit(self.scripts.get_list_of_scripts())

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
            pass
        else:
            self.getPorts.emit(f_ports)
            self.oldPort = f_ports

    def update_temperature(self, data):
        """Metoda pro updatování teploty v GUI, pokud příjde nová teplota"""
        self.getExtruderTemperature.emit(data["tools"][0])
        self.getBedTemperature.emit(data["bed"][0])
        self.getChamberTemperature.emit(data["chamber"][0])

        if data["tools"][1] != self.extruder_target_temperature:
            self.extruder_target_temperature = data["tools"][1]
            self.getExtruderTargetTemperature.emit(self.extruder_target_temperature)
        if data["bed"][1] != self.bed_target_temperature:
            self.bed_target_temperature = data["bed"][1]
            self.getBedTargetTemperature.emit(self.bed_target_temperature)
        if data["chamber"][1] != self.chamber_target_temperature:
            self.chamber_target_temperature = data["chamber"][1]
            self.getChamberTargetTemperature.emit(self.chamber_target_temperature)

    def update_position(self, data):
        """Metoda pro updatování pozive v GUI, pokud příjde nová pozice"""
        try:
            position_list = [data["X"], data["Y"], data["Z"]]
            self.getPositions.emit(position_list)
        except KeyError:
            print("Nejsou zde data")

    @Slot(str, int)
    def send_move_command(self, axis, range):
        command = {"axis": axis,
                   "range": range
                   }
        fire_event("printer_command_axis", command)

    @Slot(bool)
    def print_pause(self, state: bool):
        if state is True:
            fire_event("printer_printing_handle", "pause")
        else:
            fire_event("printer_printing_handle", "unpause")

    @Slot()
    def print_kill(self):
        fire_event("printer_printing_handle", "stop")


    @Slot(str)
    def getScript(self, name):
        script = self.scripts.get_script(name)
        print(script)
        self.getScriptText.emit(script)

    @Slot(str, str)
    def saveScript(self, name, g_code):
        self.scripts.update_script(name, g_code)
        print(f"name {name}, script {g_code}")

    @Slot(str)
    def send_home_command(self, axis):
        command = {"axis": axis,
                   }
        fire_event("printer_command_home", command)

    @Slot(str, int)
    def send_temp_command(self, tool, value):
        command = {"tool": tool,
                   "value": value,
                   }
        print(command)
        fire_event("printer_command_temp", command)

    @Slot()
    def print_connect(self):
        fire_event("printer_connect", None)

    @Slot()
    def print_disconnect(self):
        fire_event("printer_disconnect", None)

    def update_printer_status(self, status: str):
        if status == "CONNECTED":
            self.getPrinterStatus.emit(True)
            self.getPrinterPrinting.emit(False)
            self.getPrinterPause.emit(False)
        elif status == "DISCONNECTED":
            self.getPrinterStatus.emit(False)
        else:
            print("Neznamý stav")

    """    
    IDLE = "idle"
    PRINTING = "printing"
    REMOVAL = "removal"
    PAUSE = "pause"
    """

    def update_printer_state(self, status: str):
        if status == "idle":
            self.getPrinterPrinting.emit(False)
            self.getPrinterPause.emit(False)
        elif status == "printing":
            self.getPrinterPrinting.emit(True)
            self.getPrinterPause.emit(False)
        elif status == "pause":
            self.getPrinterPause.emit(True)
        elif status == "removal":
            self.getPrinterPrinting.emit(False)
            self.getPrinterPause.emit(False)

    # komunikace GUI s nastavením tiskárny


    @Slot(str)
    def serial_change_port(self, port: str):
        fire_event("serial_settings", {"port": port})
        print(f"port: {port}")

    @Slot(int)
    def serial_change_baudrate(self, baudrate: int):
        fire_event("serial_settings", {"baudrate": baudrate})
        print(f"baudrate: {baudrate}")

    @Slot(bool)
    def serial_change_autoconnect(self, autoconnect: bool):
        self.settings.setting["serial"]["auto_connect"] = autoconnect
        self.settings.update()

    @Slot(int)
    def printer_change_temp_interval_report(self, interval: int):
        fire_event("printer_set_interval", {"type": "temperature", "interval": interval})

    @Slot(int)
    def printer_change_position_interval_report(self, interval: int):
        fire_event("printer_set_interval", {"type": "position", "interval": interval})

    @Slot(bool)
    def printer_change_bed_status(self, status:bool):
        print(f"Bed status: {status}")
        self.settings.setting["printer"]["bed"]["state"] = status
        self.settings.update()

    @Slot(bool)
    def printer_change_chamber_status(self, status: bool):
        print(f"Chamber status: {status}")
        self.settings.setting["printer"]["chamber"]["state"] = status
        self.settings.update()

    @Slot(str, int)
    def printer_change_max_temperature(self, tool: str, value: int):
        print(f"tool: {tool} max temperature: {value}")
        if tool == "T":
            self.settings.setting["printer"]["extruder"]["max_temp"] = value
            self.settings.update()
        elif tool == "B":
            self.settings.setting["printer"]["bed"]["max_temp"] = value
            self.settings.update()
        elif tool == "C":
            self.settings.setting["printer"]["chamber"]["max_temp"] = value
            self.settings.update()

    # komunikace GUI s MQTT modulem
    @Slot(str)
    def printer_change_name(self, name: str):
        print(f"Printer Name: {name}")
        data = {"name": name}
        fire_event("MQTT_settings", data)

    @Slot(str)
    def mqtt_change_ip(self, ip_address: str):
        data = {"ip_address": ip_address}
        fire_event("MQTT_settings", data)

    @Slot(str)
    def mqtt_change_port(self, port: int):
        data = {"port": port}
        fire_event("MQTT_settings", data)

    @Slot()
    def mqtt_connect(self):
        fire_event("MQTT_connection", True)

    @Slot()
    def mqtt_disconnect(self):
        fire_event("MQTT_connection", False)

    @Slot(bool)
    def mqtt_auto_connect(self, state: bool):
        data = {"auto_connect": state}
        fire_event("MQTT_settings", data)

    def mqtt_connection_state(self, state: bool):
        self.getMQTT_status.emit(state)

    @Slot(str)
    def mes_change_url(self, url: str):
        print(f"MES URL: {url}")
        fire_event("MES_url", url)

    @Slot(bool)
    def automatic_system_change_status(self, state: bool):
        print(f"automatic_system_change_status: {state}")
        if state is True:
            fire_event("system_state", "start")
        else:
            fire_event("system_state", "stop")

    @Slot(bool)
    def automatic_removal_change_status(self, state: bool):
        print(f"automatic_removal_change_status: {state}")
        if state is True:
            fire_event("system_state", "auto")
        else:
            fire_event("system_state", "manual")

    @Slot(str)
    def print(self, file_url: str):
        import platform
        if platform.system() == "Linux":
            file_url = "/" + file_url
        print(f"Start print {file_url}")
        fire_event("printer_start_print", file_url)

    @Slot()
    def RemovalDone(self):
        fire_event("system_state", "removed")

    def RemovalDialog(self):
        self.getRemovalDialog.emit(True)

    def WarningDialog(self, warning):
        self.getWarningDialog.emit(warning)

    @Slot(int)
    def fan_rate_change(self, value):
        print(f"fan_rate: {value}")
        if value > 255:
            print("FAN: spatna hodnota")
        elif value <= 255 and value > 0:
            fire_event("printer_command", f"M106 P0 S{int(255/100*value)}")
        elif value == 0 or value == -1:
            fire_event("printer_command", f"M107 P0")
        else:
            print("FAN: spatna hodnota")

    @Slot(int)
    def flow_rate_change(self, value):
        print(f"flow_rate: {value}")
        fire_event("printer_command", f"M221 S{value}")

    @Slot(bool)
    def motor_off(self, state):
            fire_event("printer_command", "M84")

    @Slot(str)
    def printer_send_command(self, command: str):
        print(f"command: {command}")
        fire_event("printer_command", command)