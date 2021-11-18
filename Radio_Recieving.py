import board
import busio
import digitalio

import adafruit_rfm9x

ANTENNA_ATTACHED = True

RADIO_FREQ_MHZ = 433.0
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D6)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

radio = adafruit_rfm9x.RFM9x(spi, cs, reset, 433.0)

#rfm9x.ack_retries = 2
#rfm9x.ack_wait = 0.5
radio.enable_crc = True  # idk what this does, but we need it :D
radio.node = 255  # accept all
radio.destination = 255  # send to all

count = 0

seendID = bytearray(256)

finalNode = b'\xab'
origNode = b'\xaa'
noSatAck = b'\x00' #  This could be changed with a flag, learn how to do this :). Maybe look at send_with_ack in library to see how to edit flags
yesSatAck = b'\xaa'

seen = False

while True:

    response = radio.receive(keep_listening=True, with_header=True, timeout=None)

    if response is not None:
        print("Received (raw header):", [hex(x) for x in response[0:4]])
        print("Received (raw header):", response[0:4])
        #print("Received (raw payload): {0}".format(response[4:]))
        #print("Received (raw bytes): {0}".format(response))

        for ID in seendID:
            if response[2:3] == ID: # we have seen this message
                #if response[2] == ID: should work, check if it does. above works for sure
                seen = True
                print("already seen this message")

        if not seen:
            if response[4:5] == origNode:
                print("meant for this!")
                finalMessage = finalNode + origNode + yesSatAck
                count = response[2]
                print("Sending ack back")
                print(count)
                radio.send(finalMessage, identifier = count, destination=255, keep_listening=True)
