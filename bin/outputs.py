import grovepi
import time
from threading import Thread


class Outputs(Thread):
	"""Responsible for controlling outputs"""

	def __init__(self, run_event, rate):
		"""Ensures outputs are setup properly"""

		self.initialized = False

		# Set the GrovePi pins to send data to
		self.BUTTON_PIN = 4	# Socket D4
		self.LIGHT_PIN = 2	# Socket D2
		self.SOUND_PIN = 7	# Socket D7

		print("[OUTPUTS] Testing Outputs")
		print("[OUTPUTS] BUTTON_PIN = {}, LIGHT_PIN = {}, SOUND_PIN = {}".format(self.BUTTON_PIN, self.LIGHT_PIN, self.SOUND_PIN))

		# Set sleep rate
		self.flashing = False
		self.base_sleep_rate = rate
		self.set_sleep_rate(rate)

		# Init currently selected LED
		self.set_all_leds()

		# Configure Thread
		Thread.__init__(self)
		self.run_event = run_event
		self.daemon=True

	def set_all_leds(self):
		self.selected_led = "ALL"
		grovepi.digitalWrite(self.BUTTON_PIN, 1)
		grovepi.digitalWrite(self.LIGHT_PIN, 1)
		grovepi.digitalWrite(self.SOUND_PIN, 1)

	def set_button_led(self):
		self.selected_led = "BUTTON"
		grovepi.digitalWrite(self.BUTTON_PIN, 1)
		grovepi.digitalWrite(self.LIGHT_PIN, 0)
		grovepi.digitalWrite(self.SOUND_PIN, 0)

	def set_light_led(self):
		self.selected_led = "LIGHT"
		grovepi.digitalWrite(self.BUTTON_PIN, 0)
		grovepi.digitalWrite(self.LIGHT_PIN, 1)
		grovepi.digitalWrite(self.SOUND_PIN, 0)

	def set_sound_led(self):
		self.selected_led = "SOUND"
		grovepi.digitalWrite(self.BUTTON_PIN, 0)
		grovepi.digitalWrite(self.LIGHT_PIN, 0)
		grovepi.digitalWrite(self.SOUND_PIN, 1)

	def set_network_led(self):
		self.selected_led = "NETWORK"
		grovepi.digitalWrite(self.BUTTON_PIN, 0)
		grovepi.digitalWrite(self.LIGHT_PIN, 0)
		grovepi.digitalWrite(self.SOUND_PIN, 0)

	def unset_leds(self):
		grovepi.digitalWrite(self.BUTTON_PIN, 0)
		grovepi.digitalWrite(self.LIGHT_PIN, 0)
		grovepi.digitalWrite(self.SOUND_PIN, 0)

	def stop(self):
		"""Stops the outputs thread by clearing the run flag"""
		print("[OUTPUTS] Stopping thread")
		self.run_event.clear()

	def set_sleep_rate(self, rate):
		"""How many seconds"""
		self.sleep_rate = (rate / self.base_sleep_rate) * 0.5

	def speed_up(self, rate):
		self.sleep_rate = self.sleep_rate * rate
		

	def run(self):
		"""Reads the sensors and runs its callback when applicable"""
		print("[OUTPUTS] Outputs thread running")
		self.initialized = True

		while self.run_event.is_set():

			if self.flashing is True:
				time.sleep(self.sleep_rate)
				self.unset_leds()
				time.sleep(self.sleep_rate)
			else:
				time.sleep(0.05)

			if self.selected_led is "BUTTON":
				self.set_button_led()
			elif self.selected_led is "LIGHT":
				self.set_light_led()
			elif self.selected_led is "SOUND":
				self.set_sound_led()
			elif self.selected_led is "NETWORK":
				self.unset_leds()
			else:
				self.set_all_leds()

		# Turn off all LEDs when thread ends
		self.unset_leds()
