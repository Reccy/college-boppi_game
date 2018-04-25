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

		# Init currently selected LED
		self.set_button_led()

		# Configure Thread
		Thread.__init__(self)
		self.run_event = run_event
		self.daemon=True

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

	def stop(self):
		"""Stops the outputs thread by clearing the run flag"""
		self.run_event.clear()
		

	def run(self):
		"""Reads the sensors and runs its callback when applicable"""
		print("Outputs thread running")

		while self.run_event.is_set():
			if self.selected_led is "BUTTON":
				self.set_light_led()
			elif self.selected_led is "LIGHT":
				self.set_sound_led()
			else:
				self.set_button_led()
			time.sleep(0.1)

		# Turn off all LEDs when thread ends
		grovepi.digitalWrite(self.BUTTON_PIN, 0)
		grovepi.digitalWrite(self.LIGHT_PIN, 0)
		grovepi.digitalWrite(self.SOUND_PIN, 0)
