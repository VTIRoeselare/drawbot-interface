import serial

class Communicator:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 57600)
        if not self.ser.is_open:
            self.ser.open()
        self.is_ready = False

    def waitfordrawing(self):
        line = self.ser.readline()
        while line != b'OK\r\n':
            line = self.ser.readline()
        self.is_ready = True
    
    def sendcommand(self, cmd):
        if self.is_ready == False:
            self.waitfordrawing()
        if isinstance(cmd, str):
            cmd = cmd.encode()
        self.ser.write(cmd + b'\r')
        self.is_ready = False
    
    def sendcommands(self, cmds):
        for cmd in cmds:
            self.sendcommand(cmd)
            
    def close(self):
        self.ser.close()

    def __exit__(self):
        self.close()
