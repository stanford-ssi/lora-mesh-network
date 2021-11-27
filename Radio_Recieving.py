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
####  Initialization End #####

# For ID tracking
count = 0
seendID = bytearray(256)
loop = 0

finalNode = b'\xab' # Destination radio
origNode = b'\xaa'# Current radio. Changes depending on the radio

# Used for acknowledging a received signal
noSatAck = b'\x00'
yesSatAck = b'\xaa'
seen = False

while True:

    # Wait to receive signal
    response = radio.receive(keep_listening=True, with_header=True, timeout=None)
    seen = False # reset check

    if response is not None:
        print("Received (raw header):", [hex(x) for x in response[0:4]])
        print("Received (raw header):", response[0:4])
        #print("Received (raw payload): {0}".format(response[4:]))
        #print("Received (raw bytes): {0}".format(response))

        for ID in seendID:
            if response[2] == ID:  # we have seen this message
                seen = True
                print("already seen this message")

        if not seen:
            loop += 1

            # Temporary solution for when loop is greater than a byteArray
            if loop == 256:
                loop = 0

            seendID[loop] = response[2]  # Track new ID

            if response[4:5] == origNode:
                print("meant for this!")

                # Build new message to send back
                finalMessage = finalNode + origNode + yesSatAck
                count = response[2]  # send back with same ID
                print("Sending ack back")
                print(count)

                radio.send(finalMessage, identifier=count, destination=255, keep_listening=True)
