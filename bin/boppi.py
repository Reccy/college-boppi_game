from sensors import Sensors
from network import Network
from outputs import Outputs
import threading
import sys
import time


class BopPi():
	"""
	Main logic thread for the BopPi game.
	"""

	def __init__(self):
		""" Setup networking, sensors and output """
		print("Starting BopPi game")
		boppi_event = threading.Event()
		boppi_event.set()

		# Setup interface with sensors, network (app) and outputs (LEDs)
		self.sensors = Sensors(boppi_event, self.on_button_pressed, self.on_dark, self.on_loud).start()
		self.network = Network()
		self.outputs = Outputs()

		# Wait for KeyboardInterrupt before closing program
		try:
			while True:
				time.sleep(0.1)
		except KeyboardInterrupt:
			print("")
			print("Quitting BopPi game")
			boppi_event.clear()
			print("Thanks for Playing! :-)")
			sys.exit(0)

	# Input callbacks
	def on_button_pressed(self):
		print("Button is pressed")

	def on_dark(self):
		print("It's dark")

	def on_loud(self):
		print("It's loud")


# Start the game
bp = BopPi()
