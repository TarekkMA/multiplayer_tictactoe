from enum import Enum
import sys
from tile_state import TileState
from os import wait
import socket
from threading import Thread
from typing import Callable, Dict, List

class Packets(Enum):
  CONNECTED = b'\xff'
  TILE_CHANGE = b'\xfe'


class Connection:
  connection: socket.socket
  send_connection: socket.socket
  recive_thread: Thread
  wait_client_thread: Thread
  client_connected_listener: Callable = None
  recive_listener: Callable[[Dict], None] = None

  def __init__(self) -> None:
    self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def serve(self, host, port):
    self.connection.bind((host, port))
    self.connection.listen(1)
    self.wait_client_thread = Thread(target=self.wait_for_client)
    self.wait_client_thread.start()

  def connect(self, host, port):
    self.connection.connect((host, port))
    self.send_connection = self.connection
    self.recive_thread = Thread(
        target=self._recive, args=(self.connection,))
    self.recive_thread.start()

  def wait_for_client(self):
    client_connection, address = self.connection.accept()
    print(f"[LOG] client with {address} is connected")
    self.send_connection = client_connection
    client_connection.send(Packets.CONNECTED.value)
    self.recive_thread = Thread(target=self._recive, args=(client_connection,))
    self.recive_thread.start()
    if self.client_connected_listener:
      self.client_connected_listener()

  def send(self, list: List[bytes]):
    for b in list:
      self.send_connection.send(b)

  def _recive(self, connection: socket.socket):
    while True:
      recv_bytes = connection.recv(1)
      try:
        packet = Packets(recv_bytes)
        payload = {
            'packet': packet
        }
        if packet == Packets.TILE_CHANGE:
          payload['tile_type'] = TileState[connection.recv(1).decode('utf-8')]
          payload['x'] = int.from_bytes(connection.recv(1), 'big')
          payload['y'] = int.from_bytes(connection.recv(1), 'big')

        if self.recive_listener:
          self.recive_listener(payload)
      except ValueError as e:
        print(f'{recv_bytes} is not a known packet')
        sys.exit()
