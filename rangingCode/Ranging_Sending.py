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

################################################

# For ID tracking
count = 0
seendID = bytearray(256)

#  finalNode = input("Node destination: ")
finalNode = b'\xcc'  # Destination radio
origNode = b'\xaa'  # Current radio. Changes depending on the radio

# Used for acknowledging a received signal
noSatAck = b'\x00'
yesSatAck = origNode

#Building message to send out
finalMessage = finalNode
finalMessage += origNode
print(finalMessage)


#transmits a signal
while True:
    start = time.perf_counter()
    print("Start Ranging")

    radio.send(finalMessage, identifier=count, keep_listening=True)
    listenAgain = True

    while listenAgain:
        response = radio.receive(keep_listening=True, with_header=True, timeout=3)
        listenAgain=False

        if response is not None:
            LED.value = True
            print("Received signal!")

            for ID in seendID:
                if response[2] == ID:  # we have seen this message. We use single numbers to access the int value of the byte
                    if response[6:7] != noSatAck: # its our ack! We use number:number to access the string of the byte
                        print("signal was acknowledged by radio directly")
                        listenAgain = False
                    else:
                        listenAgain = False
        else:
            LED.value = False
            print("No signal in 3 seconds")

#receives a repsonse an uses a timer to measure how long the exchange took
stop = time.perf_counter()
print(start - stop)
