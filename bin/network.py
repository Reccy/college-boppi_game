import os
import json
import time
import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from threading import Thread


class Network(Thread):
	"""Responsible for controlling AWS publishing and subscriber threads, which interfaces with the companion app"""

	def __init__(self, boppi, run_event):
		"""Ensures AWS is setup properly and dispatches the pub and sub threads"""
		
		# Set boppi instance
		self.boppi = boppi

		# Init threading event
		self.run_event = run_event

		# Setup AWS
		self.connected = False
		self.client_id = "BopPi"
		self.endpoint = "a2qfywdy8ysvgg.iot.eu-west-1.amazonaws.com"
		self.root_ca_path = os.path.abspath(os.path.join(os.path.realpath(__file__), "../../config/security_certs/root_ca.txt"))
		self.private_key_path = os.path.abspath(os.path.join(os.path.realpath(__file__), "../../config/security_certs/private.pem.key"))
		self.certificate_path = os.path.abspath(os.path.join(os.path.realpath(__file__), "../../config/security_certs/certificate.pem.crt"))

		self.client = AWSIoTMQTTClient(self.client_id)
		self.client.configureEndpoint(self.endpoint, 8883)
		self.client.configureCredentials(self.root_ca_path, self.private_key_path, self.certificate_path)
		self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
		self.client.configureConnectDisconnectTimeout(10)  # 10 sec
		self.client.configureMQTTOperationTimeout(5)  # 5 sec

		# Configure logging
		logger = logging.getLogger("AWSIoTPythonSDK.core")
		logger.setLevel(logging.ERROR)
		streamHandler = logging.StreamHandler()
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		streamHandler.setFormatter(formatter)
		logger.addHandler(streamHandler)

		# Configure Thread
		Thread.__init__(self)
		self.run_event = run_event
		self.daemon=True

	def run(self):
		print("[NETWORK] Started Network thread")
		print("[NETWORK] Connecting to AWS IoT Core")
		self.client.connect()
		print("[NETWORK] Connected to AWS IoT Core")

		print("[NETWORK] Starting Subscriber Thread")
		self.sub = Subscriber(self.boppi, self.run_event, self.client)
		self.sub.start()

		print("[NETWORK] Starting Publisher Thread")
		self.pub = Publisher(self.boppi, self.run_event, self.client)
		self.pub.start()

		while self.pub.connected is False and self.sub.connected is False:
			time.sleep(0.1)

		self.connected = True

	def stop(self):
		print("[NETWORK] Stopping thread")
		self.run_event.clear()

		self.sub.stop()
		self.pub.stop()
		self.sub.join()
		self.pub.join()
		self.client.disconnect()
		print("[NETWORK] Network stopped")


class Subscriber(Thread):
	"""Responsible for listening to AWS MQTT messages and taking appropriate actions based on those messages"""

	def __init__(self, boppi, run_event, client):

		self.connected = False

		# Set BopPi instance
		self.boppi = boppi

		# Init threading event
		self.run_event = run_event

		# Get AWS client instance
		self.client = client

		# Configure Thread
		Thread.__init__(self)
		self.run_event = run_event
		self.daemon=True

	def run(self):
		print("[SUBSCRIBER] Subscriber Thread Started")
		self.client.subscribe("BopPi/To", 1, self.handle_message)
		self.connected = True

	def handle_message(self, client, userdata, message):
		msg = json.loads(message.payload)["message"]
		print("[SUBSCRIBER] Received Message [{}]".format(msg))

		if msg == "START_GAME" and self.boppi.game_started is False:
			self.boppi.start_game()
			self.boppi.publisher_queue.put("START_GAME")

	def stop(self):
		print("[SUBSCRIBER] Stopping thread")
		self.run_event.clear()


class Publisher(Thread):
	"""Responsible for sending messages to AWS MQTT"""

	def __init__(self, boppi, run_event, client):

		self.connected = False

		# Set BopPi instance
		self.boppi = boppi

		# Init threading event
		self.run_event = run_event

		# Get AWS client instance
		self.client = client

		# Configure Thread
		Thread.__init__(self)
		self.run_event = run_event
		self.daemon=True

	def run(self):
		print("[PUBLISHER] Publisher Thread Started")
		self.connected = True

		while self.run_event.is_set() or self.boppi.publisher_queue.empty() is False:
			if self.boppi.publisher_queue.empty() is False:
				queued_msg = self.boppi.publisher_queue.get()
				send_msg = {}
				
				if queued_msg is "START_GAME":
					send_msg['type'] = "start_game"
				elif queued_msg is "GAME_QUIT":
					send_msg['type'] = "game_quit"
				else:
					send_msg['type'] = "score"

				send_msg['message'] = queued_msg
				print("[PUBLISHER] Publishing message: [{}]".format(json.dumps(send_msg)))
				self.client.publish("BopPi/From", json.dumps(send_msg), 0)
			time.sleep(0.1)

	def stop(self):
		print("[PUBLISHER] Stopping thread")
		self.run_event.clear()
