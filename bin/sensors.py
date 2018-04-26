import grovepi
import time
import os, sys
from threading import Thread


class Sensors(Thread):
	"""Responsible for controlling and recording sensor inputs"""

	def __init__(self, run_event, button_pressed_callback, is_dark_callback, loud_noise_callback):
		"""Ensures sensors are setup properly and sets up callbacks"""

		self.initialized = False

		# Set the GrovePi pins to read the sensors from
		self.BUTTON_PIN = 3	# Socket D3
		self.LIGHT_PIN = 0	# Socket A0
		self.SOUND_PIN = 1	# Socket A1

		print("[SENSORS] Testing Sensors")
		print("[SENSORS] BUTTON_PIN = {}, LIGHT_PIN = {}, SOUND_PIN = {}".format(self.BUTTON_PIN, self.LIGHT_PIN, self.SOUND_PIN))

		# Calibrate the base light and sound readings. Then set the trigger values for when to call the callbacks.
		self.light_threshold_delta = -75
		self.sound_threshold_delta = 75

		self.calibrated_light_reading = self.read_light(True)
		self.calibrated_sound_reading = self.read_sound(True)
		self.light_threshold = self.calibrated_light_reading + self.light_threshold_delta
		self.sound_threshold = self.calibrated_sound_reading + self.sound_threshold_delta

		print("[SENSORS] Calibrated Light Value: {}".format(self.calibrated_light_reading))
		print("[SENSORS] Calibrated Sound Value: {}".format(self.calibrated_sound_reading))
		print("[SENSORS] Light Threshold: {}".format(self.light_threshold))
		print("[SENSORS] Sound Threshold: {}".format(self.sound_threshold))

		# Setup the callbacks and default last readings
		self.last_button_read = 0
		self.button_pressed_callback = button_pressed_callback

		self.last_light_read = 0
		self.is_dark_callback = is_dark_callback

		self.last_sound_read = 0
		self.loud_noise_callback = loud_noise_callback

		# Configure Thread
		Thread.__init__(self)
		self.run_event = run_event
		self.daemon=True


	# Standard read methods
	def read_button(self):
		"""Reads the button"""
		return grovepi.digitalRead(self.BUTTON_PIN)


	def read_light(self, do_calibration=False):
		"""Reads the light sensor"""
		readings = []
		reading_amount = 5

		# Perform longer sample if it's a calibration
		if do_calibration:
			reading_amount = 1500

		# Sample the light sensor
		for i in range(0, reading_amount):
			readings.append(grovepi.analogRead(self.LIGHT_PIN))
		return sum(readings) / float(len(readings))


	def read_sound(self, do_calibration=False):
		"""Reads the sound sensor"""
		readings = []
		reading_amount = 5

		# Perform longer sample if it's a calibration
		if do_calibration:
			reading_amount = 500

		# Sample the sound sensor readings
		for i in range(0, reading_amount):
			readings.append(grovepi.analogRead(self.SOUND_PIN))
		return sum(readings) / float(len(readings))

	def stop(self):
		"""Stops the sensors thread by clearing the run flag """
		print("[SENSORS] Stopping thread")
		self.run_event.clear()

	def run(self):
		"""Reads the sensors and runs its callback when applicable"""
		print("[SENSORS] Sensor thread running")
		self.initialized = True

		while self.run_event.is_set():
			# Check Button
			self.current_button_read = self.read_button()
			if self.current_button_read is 1 and self.last_button_read is 0:
				self.button_pressed_callback()
			self.last_button_read = self.current_button_read

			# Check Light
			self.current_light_read = self.read_light()
			if self.current_light_read < self.light_threshold and self.last_light_read >= self.light_threshold:
				self.is_dark_callback()
			self.last_light_read = self.current_light_read

			# Check Sound
			self.current_sound_read = self.read_sound()
			if self.current_sound_read > self.sound_threshold and self.last_sound_read <= self.sound_threshold:
				self.loud_noise_callback()
			self.last_sound_read = self.current_sound_read

			time.sleep(0.01)
