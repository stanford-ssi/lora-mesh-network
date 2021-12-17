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
radio.tx_power = 13
####  Initialization End #####

# For ID tracking
count = 0
seendID = bytearray(256)

#  finalNode = input("Node destination: ")
finalNode = b'\xcc'  # Destination radio
origNode = b'\xaa'  # Current radio. Changes depending on the radio

# Used for acknowledging a received signal
noSatAck = b'\x00'
yesSatAck = origNode

# Used for knowing whether signal was received by a relay
noRelay = b'\x00'
yesRelay = origNode

# Building message to send out
finalMessage = finalNode
finalMessage += origNode
finalMessage += noSatAck
finalMessage += noRelay
finalMessage += b'Message to node'

print(finalMessage)

while True:

    print("Sending message out to all nodes")
    count += 1


    # For when count is greater than a byte
    if count == 256:
        count = 1
        seendID = bytearray(256)


    radio.send(finalMessage, identifier=count, keep_listening=True)
    listenAgain = True
    print(count)

    # adding ID to seen
    seendID[count] = count

    while listenAgain:
        # wait for response for 3 seconds
        response = radio.receive(keep_listening=True, with_header=True, timeout=3)
        listenAgain = False

        if response is not None:
            print("Received (raw header):", [hex(x) for x in response[0:4]])
            print("Received (raw payload): {0}".format(response[4:]))
            print("Received RSSI: {0}".format(radio.last_rssi))

            for ID in seendID:
                if response[2] == ID:  # we have seen this message. We use single numbers to access the int value of the byte
                    if response[6:7] != noSatAck and response[7:8] != noRelay:
                        print("Signal was acknowledged by radio through a relay")
                        listenAgain = False
                    elif response[6:7] != noSatAck:  # its our ack! We use number:number to access the string of the byte
                        print("signal was acknowledged by radio directly")
                        listenAgain = False
                    elif response[7:8] != noRelay:
                        print("Messaged was relayed, waiting a second time")
                        listenAgain = True
                    else:
                        listenAgain = False

        else:
            ########
            # Note for debugging using RadioHead. radio.receive will return None
            # When it gets a signal that wasn't meant for it when it only accepts
            # signals that are meant for it. This only matters if you are using RadioHead
            # In that case you would add a listenAgain = True below the print. It will have
            # to connect right away or you will be stuck in an infinite loop.
            ########
            print("No response in 3 seconds")

    time.sleep(2)
