import board
import busio
import digitalio
import time

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
radio.enable_crc = True  # idk what this does
radio.node = 255  # accept all(?) Idk if we need to specify or not
radio.destination = 255  # send to all

count = 0

seendID = bytearray(256)

# #Comment out when testting as it will not run without input
#  finalNode = input("Node destination: ")
finalNode = b'\xaa'
origNode = b'\xab'
noSatAck = b'\xbb' #  This could be changed with a flag, learn how to do this :). Maybe look at send_with_ack in library to see how to edit flags
yesSatAck = b'xaa'

#  finalMessage = input("What do you want to tell the node?: ")
finalMessage = finalNode
finalMessage += origNode
finalMessage += noSatAck
finalMessage += b'Message to node'

print(finalMessage)

while True:

    #  receving radio will switch from listening to all to accepting just ack
    #  the radios will have the window open for 100 seconds before accepting
    #  all again
    print("Sending message out to all nodes")
    count += 1
    radio.send(finalMessage, identifier = count, destination=255, keep_listening=True)

    # adding ID to seen, mainly to check for ack
    seendID[count] = count #  play around with bytearray

    response = radio.receive(keep_listening=True, with_header=True, timeout=10)

    if response is not None:
        print("Received (raw header):", [hex(x) for x in response[0:4]])
        print("Received (raw payload): {0}".format(response[4:]))
        print("Received RSSI: {0}".format(radio.last_rssi))

        for ID in seendID: # TODO: check that if byte can equal number. Like if 1 == 0x01
            #ID = (ID) & 0xFF # this is how radio library changes number to byte(?). Might not be necessary. Look into if its not working
            if response[2:3] == ID: # we have seen this message
                if response[6:7] == yesSatAck: # its our ack!
                    print("signal was acknowledged by radio")

    else:
        print("No ack in 10 seconds")

    time.sleep(2)

