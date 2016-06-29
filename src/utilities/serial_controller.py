'''
Created on Jun 29, 2016

@author: Mark
'''
import serial


def connect(channel):
    channel = channel.encode("UTF-8")
    ser = serial.Serial("/dev/ttyS1", baudrate=1200)
    try:
        print(ser.name)
        ser.write(channel)
#         data = ser.read_all()
#         data = data.decode("UTF-8")
#         print(data)
#         assert len(data) < 1
#         assert data.startswith(channel.decode("UTF-8"))
#         assert data.endswith(channel.decode("UTF-8"))
    finally:
        ser.close()

if __name__ == "__main__":
    for each in ["1", "2", "3", "4"]:
        connect(each)
