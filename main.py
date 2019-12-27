import logging
import sys
sys.path.append('lib')
import signal

import RPi.GPIO as GPIO

from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_LIGHTBULB
from pyhap.accessory_driver import AccessoryDriver


class LightBulb(Accessory):

    category = CATEGORY_LIGHTBULB

    @classmethod
    def _gpio_setup(_cls, pin):
        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)

    def __init__(self, *args, pin=12, **kwargs):
        super().__init__(*args, **kwargs)

        serv_light = self.add_preload_service('Lightbulb')
        self.char_on = serv_light.configure_char(
            'On', setter_callback=self.set_bulb, getter_callback=self.get_bulb)

        self.pin = pin
        self._gpio_setup(pin)
        self.__on = True

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._gpio_setup(self.pin)

    def set_bulb(self, value):
        self.__on = value
        if value:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)

    def get_bulb(self):
        return self.__on

    def stop(self):
        super().stop()
        GPIO.cleanup()

logging.basicConfig(level=logging.INFO)

driver = AccessoryDriver(port=51826)

lamp = LightBulb(driver, 'PrinterLight')
driver.add_accessory(accessory=lamp)

signal.signal(signal.SIGTERM, driver.signal_handler)

driver.start()