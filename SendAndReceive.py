from network import LoRa
import socket
import time
import binascii
import pycom

lora = LoRa(mode=LoRa.LORAWAN)

print ("devEUI {}".format(binascii.hexlify(lora.mac())))

app_eui = binascii.unhexlify('00 00 00 00 00 00 00 00'.replace(' ',''))
app_key = binascii.unhexlify('11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ',''))
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)

pycom.heartbeat(False)
pycom.rgbled(0x111111)


while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
#s.bind(5)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)


while True:
    pycom.rgbled(0x110000)
    s.setblocking(True)
    s.settimeout(10)

# for testing new code, remove try/except

    try:
        s.send('Hello LoRa')
    except:
        print ('timeout in sending')

    pycom.rgbled(0x001100)

    try:
        data = s.recv(64)

        print(data)
        pycom.rgbled(0x000011)
    except:
        print ('timeout in receive')
        pycom.rgbled(0x000000)


    s.setblocking(False)
    time.sleep (30)
