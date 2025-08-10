#!/bin/env python3
import serial
import time

config=open('querymeter.conf','r').read().splitlines()
SERIAL=config[0] # first line of querymeter.conf should be like /dev/ttyUSB0
logfile=open('querymeter_'+time.strftime('%Y%m%d%H%M%S')+'.csv','w')
serialPort = serial.Serial(port=SERIAL,baudrate=1200, bytesize=8, parity='N', stopbits=1, timeout=5000, xonxoff=0, rtscts=0, dsrdtr=0, write_timeout=0.1)

def send_message(message):
    packet = [len(message) + 3] # firts byte is length including itself and checksum
    packet += message
    crc = crc16_arc(packet) # crc16 of length byte plus message
    packet.append(int(crc % 256)) # LSB
    packet.append(int(crc / 256)) # MSB
    serialPort.write(packet)
    return packet

def receive_message():
    a = serialPort.read_all()
    if a[0] != len(a):
        print('invalid packet recieved: ',end='')
        print(a)
        return False
    if crc16_arc(a[:-2]) !=    a[-1] * 256 + a[-2]:
        print(a)
        print('CRC was ' + str(a[-1] * 256 + a[-2]) + ' but expected ' + str(crc16_arc(a[:-2])))
        return False
    return a

def crc16_arc(data, offset=0, length=None):
    if length is None:
        length = len(data) - offset
    if data is None or offset < 0 or offset > len(data) - 1 or offset + length > len(data):
        return 0
    crc = 0x0000
    for i in range(length):
        crc ^= data[offset + i]
        for j in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc = crc >> 1
    return crc   

def wait_for_response():
    r = False
    startWaitTime = time.time()
    while (r == False) and (time.time() - startWaitTime < 5):
        r = receive_message()
    if r:
        print(r)
    else:
        print('timed out waiting for a response')

def send_break():
    serialPort.break_condition = True # https://forums.raspberrypi.com/viewtopic.php?t=239406
    time.sleep(0.110)
    serialPort.break_condition = False
    time.sleep(0.060)

if __name__ == '__main__':
    #print('CRC:',hex(crc16_arc(bytes.fromhex('0B0000000000000009'))))
    #print('CRC:',hex(crc16_arc([0x0B,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x09])))
    send_break()
    print('sent ' + str(send_message([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x09])))
    time.sleep(0.220)
    send_break()
    print('sent ' + str(send_message([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x07,0x00])))
    # now 0.553 seconds will go by before response
    wait_for_response()
    time.sleep(5.13)
    send_break()
    print('sent ' + str(send_message(['0x60','0x93','0x05','0x50','0x10','0x02','0xB6','0x03','0x00','0x00','0x00','0x00','0x00','0x00','0x00','0x01','0x00','0x00','0x00','0x00','0x00','0x00','0x00','0x00','0x22','0x01','0x00','0x00','0x74'])))
    wait_for_response()
    print('sent ' + str(send_message(['0x60','0x93','0x05','0x50','0x10','0x02','0xB6','0x05','0x00','0x00','0x00','0x00','0x00','0x00','0x00','0x00','0xA7','0x23','0xB1','0xC1','0xE9','0x4D','0xA6','0x8C'])))
    wait_for_response()
