from sensors import Sensors
from network import Network
from outputs import Outputs
import threading
import random
import sys
import time


class BopPi():
	"""
	Main logic thread for the BopPi game.
	"""

	def __init__(self):
		""" Setup game """
		print("Starting BopPi game")
		boppi_event = threading.Event()
		boppi_event.set()
		self.selected_sensor = None
		self.action_start_time = None

		# Setup interface with sensors, network (app) and outputs (LEDs)
		self.sensors = Sensors(boppi_event, self.on_button_pressed, self.on_dark, self.on_loud)
		self.sensors.start()
		self.network = Network()
		self.outputs = Outputs()

		self.select_next_sensor()

		# Wait for KeyboardInterrupt before closing program
		try:
			while True:
				time.sleep(0.01)
		except KeyboardInterrupt:
			print("")
			print("Quitting BopPi game")
			print("Thanks for Playing! :-)")
		finally:
			self.sensors.stop()
			self.sensors.join()
			sys.exit(0)

	# Select the next sensor in the game
	def select_next_sensor(self):
		self.selected_sensor = random.choice(["BUTTON", "SOUND", "LIGHT"])
		self.action_start_time = time.time()
		print("Selected Sensor => {}".format(self.selected_sensor))

	# Input callbacks
	def on_button_pressed(self):
		if self.selected_sensor is "BUTTON":
			print("Button is pressed")
			self.select_next_sensor()

	def on_dark(self):
		if self.selected_sensor is "LIGHT":
			print("It's dark")
			self.select_next_sensor()

	def on_loud(self):
		if self.selected_sensor is "SOUND":
			print("It's loud")
			self.select_next_sensor()

	# Timeout callback
	def on_timeout(self):
		self.selected_sensor = None
		print("Oh no! You lost :(")
		print("Thanks for Playing! :-)")
		boppi_event.clear()
		self.sensors.join()
		sys.exit(0)


# Start the game
bp = BopPi()
