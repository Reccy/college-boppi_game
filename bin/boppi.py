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
		
		# Init score
		self.score = None

		# Init selected sensor
		self.selected_sensor = None
		
		# Init timings. (Start time for the action, End time for the action, How long an action should take, How much to shorten the reaction time to the action, The minimum amount of time for every action)
		self.action_start_time = None
		self.action_end_time = None
		self.action_time = 5
		self.action_time_delta = -0.1
		self.action_min_time = 2

		# Setup interface with sensors, network (app) and outputs (LEDs)
		self.sensors = Sensors(boppi_event, self.on_button_pressed, self.on_dark, self.on_loud)
		self.sensors.start()
		self.network = Network()
		self.outputs = Outputs(boppi_event)
		self.outputs.start()

		self.select_next_sensor()

		# Wait for KeyboardInterrupt before closing program
		try:
			while True:

				# If the game times out, quit
				if (self.action_end_time - time.time() <= 0):
					print("")
					print("Oh no! You ran out of time  :(")
					print("Here's your score: {}".format(self.score))
					print("Thanks for playing!")
					sys.exit(0)

				time.sleep(0.01)
		except KeyboardInterrupt:
			print("")
			print("Quitting BopPi game")
			print("Thanks for Playing! :-)")
		finally:
			# Stop any other threads
			self.sensors.stop()
			self.outputs.stop()
			self.sensors.join()
			self.outputs.join()
			sys.exit(0)

	# Select the next sensor in the game
	def select_next_sensor(self):
		# Increment score if set, init if not
		if self.score is None:
			self.score = 0
		else:
			self.score += 1

		# Choose random instruction
		self.selected_sensor = random.choice(["BUTTON", "SOUND", "LIGHT"])

		# Set the start and end times for this action, and update the delta, making it shorter
		self.action_start_time = time.time()
		self.action_end_time = self.action_start_time + self.action_time

		if self.action_time > self.action_min_time:
			self.action_time += self.action_time_delta
		else:
			self.action_time = self.action_min_time

		print("Selected Sensor => {}. You have {} seconds to react.".format(self.selected_sensor, self.action_time))

	# Input callbacks
	def on_button_pressed(self):
		if self.selected_sensor is "BUTTON":
			print("Button instruction completed")
			self.select_next_sensor()

	def on_dark(self):
		if self.selected_sensor is "LIGHT":
			print("Light instruction completed")
			self.select_next_sensor()

	def on_loud(self):
		if self.selected_sensor is "SOUND":
			print("Sound instruction completed")
			self.select_next_sensor()


# Start the game
bp = BopPi()
