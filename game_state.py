from enum import Enum
from typing import Callable, List


class TileState(Enum):
  EMPTY = ""
  X = "X"
  O = "O"


class GameState():
  turn: TileState
  winner: TileState
  _state: List[TileState]
  _board_size: int
  _listener: Callable

  def __init__(self, board_size: int, listener: Callable) -> None:
    self._board_size = board_size
    self._state = [TileState.EMPTY] * (board_size * board_size)
    self._listener = listener
    self.winner = None
    self.turn = TileState.X

  def new_game(self):
    self._state = [TileState.EMPTY] * (self._board_size * self._board_size)
    self.winner = None
    self._listener()

  def _index(self, x, y):
    return y * self._board_size + x

  def get(self, x: int, y: int):
    index = self._index(x, y)
    return self._state[index]

  def set(self, x: int, y: int, state: TileState):
    if self.get(x, y) == TileState.EMPTY:
      index = self._index(x, y)
      self._state[index] = state
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
    
    self._listener()
