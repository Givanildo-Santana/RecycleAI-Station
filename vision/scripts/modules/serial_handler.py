import serial
import threading
import time

class SerialHandler:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serial_obj = None
        self.running = True
        self.thread = None

    def start(self):
        try:
            print(f"Tentando abrir porta {self.port} com baudrate {self.baudrate}...")
            self.serial_obj = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)
            print("🔌 Arduino conectado!")
        except Exception as e:
            print("⚠ ERRO AO CONECTAR NO ARDUINO:", e)
            self.serial_obj = None

        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()

    def _monitor(self):
        while self.running:
            if self.serial_obj and self.serial_obj.in_waiting:
                try:
                    msg = self.serial_obj.readline().decode(errors="ignore").strip()
                    if msg:
                        print("\n─────────────────────────────────────────")
                        print(f"[ARDUINO] {msg}")
                        print("─────────────────────────────────────────\n")
                except:
                    pass
            time.sleep(0.05)

    def send(self, message):
        if self.serial_obj:
            msg = (message + "\n").encode()
            self.serial_obj.write(msg)
            print(f"[PYTHON] → Enviado para Arduino: {message}")

    def stop(self):
        self.running = False
        if self.serial_obj:
            self.serial_obj.close()
