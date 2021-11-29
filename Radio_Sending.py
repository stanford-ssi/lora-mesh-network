import board
import busio
import digitalio
import time

import adafruit_rfm9x

#####  Initialization  #######
ANTENNA_ATTACHED = True

RADIO_FREQ_MHZ = 433.0
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D6)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

radio = adafruit_rfm9x.RFM9x(spi, cs, reset, 433.0)

# rfm9x.ack_retries = 2
# rfm9x.ack_wait = 0.5
radio.enable_crc = True
radio.node = 255  # accept all
radio.destination = 255  # send to all
# 5-23, 13 is default. Power of radio signal
radio.tx_power = 5
####  Initialization End #####


# For ID tracking
count = 0
seendID = bytearray(256)

#  finalNode = input("Node destination: ")
finalNode = b'\xcc'  # Destination radio
origNode = b'\xaa'  # Current radio. Changes depending on the radio

# This could be changed with a flag
# Used for acknowledging a received signal
noSatAck = b'\x00'
yesSatAck = b'\xaa'

# Used for knowing whether signal was received by a relay
noRelay = b'\x00'
yesRelay = b'\xaa'

# Building message to send out
#  finalMessage = input("What do you want to tell the node?: ")
finalMessage = finalNode
finalMessage += origNode
finalMessage += noSatAck
finalMessage += noRelay
finalMessage += b'Message to node'

print(finalMessage)

while True:

    print("Sending message out to all nodes")
    count += 1

    # Temporary solution for when count is greater than a byte
    if count == 256:
        count = 0

    radio.send(finalMessage, identifier=count, destination=255, keep_listening=True)
    listenAgain = False;

    # adding ID to seen
    seendID[count] = count

    # wait for response for 10 seconds
    response = radio.receive(keep_listening=True, with_header=True, timeout=3)

    if response is not None:
        # print("Received (raw header):", [hex(x) for x in response[0:4]])
        print("Received (raw payload): {0}".format(response[4:]))
        print("Received RSSI: {0}".format(radio.last_rssi))

        for ID in seendID:
            if response[2] == ID:  # we have seen this message. We use single numbers to access the int value of the byte
                if response[6:7] == yesSatAck and response[7:8] == yesRelay:
                    print("Signal was acknowledged by radio through a relay")
                elif response[6:7] == yesSatAck:  # its our ack! We use number:number to access the string of the byte
                    print("signal was acknowledged by radio directly")
                elif response[7:8] == yesRelay:
                    print("Messaged was relayed")
                    listenAgain = True

        if listenAgain == True:
            response = radio.receive(keep_listening=True, with_header=True, timeout=3)

            if response is not None:
                # print("Received (raw header):", [hex(x) for x in response[0:4]])
                print("Received (raw payload): {0}".format(response[4:]))
                print("Received RSSI: {0}".format(radio.last_rssi))

            for ID in seendID:
                if response[2] == ID:  # we have seen this message. We use single numbers to access the int value of the byte
                    if response[6:7] == yesSatAck and response[7:8] == yesRelay:
                        print("Signal was acknowledged by radio through a relay")
                    elif response[6:7] == yesSatAck:  # its our ack! We use number:number to access the string of the byte
                        print("signal was acknowledged by radio directly")
                    elif response[7:8] == yesRelay:
                        print("Messaged was relayed")
    else:
        print("No response in 3 seconds")

    time.sleep(1)
