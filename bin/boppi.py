from sensors import Sensors
from network import Network
from outputs import Outputs
import threading
import random
import sys
import time
import Queue

class BopPi():
	"""
	Main logic thread for the BopPi game.
	"""

	def __init__(self):
		""" Setup game """
		print("[BOPPI] Starting BopPi game")
		boppi_event = threading.Event()
		boppi_event.set()
		
		# Init score
		self.score = None

		# Init selected sensor
		self.selected_sensor = BopPi.select_random_sensor()

		# Init network publisher queue
		self.publisher_queue = Queue.Queue()
		
		# Init timings. (Start time for the action, End time for the action, How long an action should take, How much to shorten the reaction time to the action, The minimum amount of time for every action)
		self.game_started = False
		self.action_start_time = None
		self.action_end_time = None
		self.action_time = 5
		self.action_time_delta = -0.1
		self.action_min_time = 1.5

		# Setup interface with sensors, network (app) and outputs (LEDs)
		self.outputs = Outputs(boppi_event)
		self.outputs.start()

		self.sensors = Sensors(boppi_event, self.on_button_pressed, self.on_dark, self.on_loud)
		self.sensors.start()
		
		self.network = Network(self, boppi_event)
		self.network.start()

		# Wait for KeyboardInterrupt before closing program
		try:
			while True:

				# If the game times out, quit
				if self.game_started is True:
					if (self.action_end_time - time.time() <= 0):
						self.publisher_queue.put(self.score)
						print("\n[BOPPI] Oh no! You ran out of time  :(")
						print("[BOPPI] Here's your score: {}".format(self.score))
						print("[BOPPI] Thanks for playing!")
						sys.exit(0)

				time.sleep(0.01)
		except KeyboardInterrupt:
			print("\n[BOPPI] Quitting BopPi game")
			print("[BOPPI] Thanks for Playing! :-)")
		finally:
			# Stop any other threads
			self.sensors.stop()
			self.outputs.stop()
			self.network.stop()
			self.sensors.join()
			self.outputs.join()
			self.network.join()
			sys.exit(0)

	def start_game(self):
		self.game_started = True
		self.select_next_sensor()

	def select_next_sensor(self):
		"""Select the next sensor in the game"""
		# Increment score if set, init if not
		if self.score is None:
			self.score = 0
		else:
			self.score += 1

		# Choose random instruction
		self.selected_sensor = BopPi.select_random_sensor(self.selected_sensor)

		# Set the lights for the selected sensor
		if self.selected_sensor is "BUTTON":
			self.outputs.set_button_led()
		elif self.selected_sensor is "SOUND":
			self.outputs.set_sound_led()
		else:
			self.outputs.set_light_led()

		# Set the start and end times for this action, and update the delta, making it shorter
		self.action_start_time = time.time()
		self.action_end_time = self.action_start_time + self.action_time

		if self.action_time > self.action_min_time:
			self.action_time += self.action_time_delta
		else:
			self.action_time = self.action_min_time

		print("[BOPPI] Selected Sensor => {}. You have {} seconds to react.".format(self.selected_sensor, self.action_time))

	@staticmethod
	def select_random_sensor(sensor=None):
		"""Selects a random sensor"""
		returned_sensor = random.choice(["BUTTON", "SOUND", "LIGHT"])
		if sensor is returned_sensor:
			returned_sensor = BopPi.select_random_sensor(sensor)
		return returned_sensor

	# Input callbacks
	def on_button_pressed(self):
		if self.selected_sensor is "BUTTON" and self.game_started is True:
			print("[BOPPI] Button instruction completed")
			self.select_next_sensor()

	def on_dark(self):
		if self.selected_sensor is "LIGHT" and self.game_started is True:
			print("[BOPPI] Light instruction completed")
			self.select_next_sensor()

	def on_loud(self):
		if self.selected_sensor is "SOUND" and self.game_started is True:
			print("[BOPPI] Sound instruction completed")
			self.select_next_sensor()


# Start the game
bp = BopPi()