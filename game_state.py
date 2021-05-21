from enum import Enum, Flag
from network import Connection, Packets
from typing import Callable, List
from tile_state import TileState


class GameState():
  user_tile_type: TileState
  turn: TileState
  winner: TileState
  _state: List[TileState]
  _board_size: int
  _listener: Callable
  multi_palyer_connection: Connection = None

  def __init__(self, board_size: int, listener: Callable, is_server: bool = None) -> None:
    self._board_size = board_size
    self._state = [TileState.EMPTY] * (board_size * board_size)
    self._listener = listener
    self.winner = None
    self.turn = TileState.X
    self.user_tile_type = TileState.X
    self.setup_multiplayer_connection(is_server)

  def setup_multiplayer_connection(self, is_server: bool = None):
    if is_server != None:
      self.multi_palyer_connection = Connection()
      if is_server:
        self.multi_palyer_connection.serve("localhost", 8080)
        self.multi_palyer_connection.wait_client_thread.join()
      else:
        self.multi_palyer_connection.connect("localhost", 8080)
        self.user_tile_type = TileState.O

      self.multi_palyer_connection.recive_listener = self.multiplayer_event

  def multiplayer_event(self, payload):
    if payload['packet'] == Packets.TILE_CHANGE:
      tile_type = payload['tile_type']
      x = payload['x']
      y = payload['y']

      self.set(x, y, tile_type, from_network=True)

  def new_game(self):
    self._state = [TileState.EMPTY] * (self._board_size * self._board_size)
    self.winner = None
    self._listener()

  def _index(self, x, y):
    return y * self._board_size + x

  def get(self, x: int, y: int):
    index = self._index(x, y)
    return self._state[index]

  def set(self, x: int, y: int, state: TileState, /, from_network=False):
    current_value = self.get(x, y)
    if current_value == TileState.EMPTY:
      index = self._index(x, y)
      self._state[index] = state
      if not from_network and self.multi_palyer_connection:
        self.multi_palyer_connection.send(
            [Packets.TILE_CHANGE.value, bytes(state.value, 'utf-8'), bytes([x]), bytes([y])])
      self.check_winner()
      self.end_turn()

  def _check_tiles_winner(self, tiles: List[TileState]) -> TileState:
    first_tile = tiles[0]
    has_winner = len(set(tiles)) == 1
    if has_winner and first_tile != TileState.EMPTY:
      return first_tile

  def check_winner(self):
    for cols in range(0, self._board_size):
      tiles_to_check = [self.get(x, cols) for x in range(0, self._board_size)]
      winner = self._check_tiles_winner(tiles_to_check)
      if winner:
        self._declare_winnder(winner)
        return

    for cols in range(0, self._board_size):
      tiles_to_check = [self.get(cols, y) for y in range(0, self._board_size)]
      winner = self._check_tiles_winner(tiles_to_check)
      if winner:
        self._declare_winnder(winner)
        return

    tiles_to_check = [self.get(z, z) for z in range(0, self._board_size)]
    winner = self._check_tiles_winner(tiles_to_check)
    if winner:
      self._declare_winnder(winner)
      return

    tiles_to_check = [self.get(z, self._board_size - z - 1)
                      for z in range(0, self._board_size)]
    winner = self._check_tiles_winner(tiles_to_check)
    if winner:
      self._declare_winnder(winner)
      return

    if self._state.count(TileState.EMPTY) == 0:
      self._declare_winnder(TileState.EMPTY)

  def _declare_winnder(self, winner: TileState):
    self.winner = winner

  def end_turn(self):
    if self.turn == TileState.X:
      self.turn = TileState.O
    else:
      self.turn = TileState.X

    if not self.multi_palyer_connection:
      self.user_tile_type = self.turn

    self._listener()
