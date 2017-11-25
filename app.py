from json import loads as json_loads
import socket
from queue import Queue, Empty
from _thread import start_new_thread

from gpiozero import DigitalOutputDevice

HOST = ""
PORT = 1631

STATE_QUEUE = Queue()

LEFT_RELAY = DigitalOutputDevice(18)
RIGHT_RELAY = DigitalOutputDevice(1)


class State:
	def __init__(self, power=False, cycle_time=100,
		operating_ratios=None):

		self.power = power
		self.cycle_time = cycle_time
		if operating_ratios is None:
			self.operating_ratios = [1.0, 1.0]
		else:
			self.operating_ratios = operating_ratios

	def __repr__(self):
		return str(self.__dict__)


def object_decoder(obj):
	return State(obj["power"], obj["cycle_time"], 
		obj["operating_ratios"])


def calc_pwm(cycle_time, operating_ratio):
	operating_time = cycle_time * operating_ratio
	return operating_time, 1 - operating_time


class ControlLoop:
	def __init__(self, left_relay, right_relay):
		self.left_relay = left_relay
		self.right_relay = right_relay

		self.state = None
		self.power = False

	def run(self):
		while True:
			state = STATE_QUEUE.get()

			print("Applying state: %r" % state)

			self.power = state.power

			while self.power:
				try:
					state = STATE_QUEUE.get_nowait()

					print("Applying state: %r" % state)
				except Empty:
					pass

				self.power = state.power

				self.left_relay.blink(*calc_pwm(
					state.cycle_time, state.operating_ratios[0]))

				self.right_relay.blink(*calc_pwm(
					state.cycle_time, state.operating_ratios[1]))

			self.left_relay.off()
			self.right_relay.off()


control_loop = ControlLoop(LEFT_RELAY, RIGHT_RELAY)

start_new_thread(control_loop.run, ())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((HOST, PORT))
	sock.listen(1)


	conn, addr = sock.accept()

	with conn:
		connected = True

		while connected:
			data = conn.recv(1024)
			decoded_data = None


			if not data: 
				break
			else:
				decoded_data = data.decode()

			try:
				STATE_QUEUE.put(json_loads(decoded_data, 
					object_hook=object_decoder))
			except KeyError:
				connected = False
				conn.close()