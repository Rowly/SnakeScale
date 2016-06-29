'''
Created on Jun 29, 2016

@author: Mark
'''
import serial.Serial


def connect(channel):
    channel = bytes(channel)
    ser = serial.Serial("/dev/ttyS1", baudrate=1200)
    print(ser.name)
    ser.write(channel)
    data = ser.read_all()
    data = str(data)
    assert len(data) < 1
    assert data.startswith(str(channel))
    assert data.endswith(str(channel))
    ser.close()

if __name__ == "__main__":
    for each in ["1", "2", "3", "4"]:
        connect(each)
