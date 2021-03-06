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

###################################################

# For ID tracking
seendID = bytearray(200)
loop = 0

finalNode = b'\xff' # Destination radio
origNode = b'\xbb'# Current radio. CHANGE depending on the radio

# Used for acknowledging a received signal
noSatAck = b'\x00'
yesSatAck = origNode


while True:
    response = radio.receive(keep_listening=True, with_header=True, timeout=1)
    seen = False

    if response is not None:
        finalMessage = response[4:]
        radio.send(finalMessage, keep_listening=True)



