import grovepi
import time
from threading import Thread


class Outputs(Thread):
	"""Responsible for controlling outputs"""

	def __init__(self, run_event):
		"""Ensures outputs are setup properly"""

		# Set the GrovePi pins to send data to
		self.BUTTON_PIN = 4	# Socket D4
		self.LIGHT_PIN = 7	# Socket D7
		self.SOUND_PIN = 2	# Socket D2

		print("[OUTPUTS] Testing Outputs")
		print("[OUTPUTS] BUTTON_PIN = {}, LIGHT_PIN = {}, SOUND_PIN = {}".format(self.BUTTON_PIN, self.LIGHT_PIN, self.SOUND_PIN))

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

	def unset_leds(self):
		grovepi.digitalWrite(self.BUTTON_PIN, 0)
		grovepi.digitalWrite(self.LIGHT_PIN, 0)
		grovepi.digitalWrite(self.SOUND_PIN, 0)

	def stop(self):
		"""Stops the outputs thread by clearing the run flag"""
		print("[OUTPUTS] Stopping thread")
		self.run_event.clear()
		

	def run(self):
		"""Reads the sensors and runs its callback when applicable"""
		print("[OUTPUTS] Outputs thread running")

		while self.run_event.is_set():
			if self.selected_led is "BUTTON":
				self.set_button_led()
			elif self.selected_led is "LIGHT":
				self.set_light_led()
			elif self.selected_led is "SOUND":
				self.set_sound_led()
			else:
				self.set_all_leds()
				
			time.sleep(0.05)
			self.unset_leds()
			time.sleep(0.05)

		# Turn off all LEDs when thread ends
		self.unset_leds()
