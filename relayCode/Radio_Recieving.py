import board
import busio
import digitalio

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
seendID = bytearray(200)
loop = 0

finalNode = b'\xff' # Destination radio
origNode = b'\xbb'# Current radio. CHANGE depending on the radio

# Used for acknowledging a received signal
noSatAck = b'\x00'
yesSatAck = origNode

# Used for acknowledging whether signal was received by a relay
noRelay = b'\x00'
yesRelay = origNode

while True:

    # Wait to receive signal
    response = radio.receive(keep_listening=True, with_header=True, timeout=1)
    seen = False

    if response is not None:
        print("Received (raw header):", [hex(x) for x in response[0:4]])
        #print("Received (raw header):", response[0:4])
        print("Received (raw payload): {0}".format(response[4:]))
        #print("Received (raw bytes): {0}".format(response))

        messageID = response[2]  # track ID

        for ID in seendID:
            if messageID == ID:  # we have seen this message
                seen = True
                print("already seen this message")

        # if it has seen it, it is not its own acknowledgment that was relayed back, and its an acknowledgment of another radio
        if seen and response[6:7] != origNode and response[6:7] != noSatAck:
            print("Re-relaying the message because its an acknowledgment")

            finalMessage = response[4:7] + yesRelay
            print(finalMessage)

            radio.send(finalMessage, identifier=messageID, keep_listening=True)

        elif not seen:
            loop += 1
            # Solution for when loop is greater than a byteArray
            if loop == 200:
                loop = 0
                seendID = bytearray(256)

            seendID[loop] = messageID  # Track new ID

            if response[4:5] == origNode:
                print("Meant for this!")

                # Build new message to send back. New finalNode and newOrigin for the message (back to sender)
                finalMessage = response[5:6] + response[4:5] + yesSatAck + response[7:8]

                print("Sending ack back")
                print(messageID)

                radio.send(finalMessage, identifier=messageID, keep_listening=True)

            else:
                print("Not meant for this")
                print("Re-relaying the message")

                #build new message to send back
                finalMessage = response[4:7] + yesRelay
                print(finalMessage)

                radio.send(finalMessage, identifier=messageID, keep_listening=True)

