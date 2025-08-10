#!/bin/env python3

def send_message(message):
    packet = [len(message) + 3] # firts byte is length including itself and checksum
    packet += message
    crc = crc16_arc(packet) # crc16 of length byte plus message
    packet.append(int(crc % 256)) # LSB
    packet.append(int(crc / 256)) # MSB
    return packet

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

if __name__ == '__main__':
    print('CRC:',hex(crc16_arc(bytes.fromhex('0B0000000000000009'))))
    print('CRC:',hex(crc16_arc([0x0B,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x09])))
    print(send_message([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x09]))
