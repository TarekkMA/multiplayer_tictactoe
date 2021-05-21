from typing import Callable, List
from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import (
    QGridLayout, QMessageBox, QPushButton, QSizePolicy)
import sys
from enum import Enum

GAME_SZIE = 3


class TileState(Enum):
  EMPTY = ""
  X = "X"
  O = "O"


class GameState():
  winner: TileState
  _state: List[TileState]
  _board_size: int
  _listener: Callable

  def __init__(self, board_size: int, listener: Callable) -> None:
    self._board_size = board_size
    self._state = [TileState.EMPTY] * (board_size * board_size)
    self._listener = listener
    self.winner = None

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
    index = self._index(x, y)
    self._state[index] = state
    self.check_winner()
    self._listener()

  def check_tiles_winner(self, tiles: List[TileState]) -> TileState:
    first_tile = tiles[0]
    has_winner = len(set(tiles)) == 1
    if has_winner and first_tile != TileState.EMPTY:
      return first_tile

  def check_winner(self):
    for cols in range(0, self._board_size):
      tiles_to_check = [self.get(x, cols) for x in range(0, self._board_size)]
      winner = self.check_tiles_winner(tiles_to_check)
      if winner:
        self.declare_winnder(winner)
        return

    for cols in range(0, self._board_size):
      tiles_to_check = [self.get(cols, y) for y in range(0, self._board_size)]
      winner = self.check_tiles_winner(tiles_to_check)
      if winner:
        self.declare_winnder(winner)
        return

    tiles_to_check = [self.get(z, z) for z in range(0, self._board_size)]
    winner = self.check_tiles_winner(tiles_to_check)
    if winner:
      self.declare_winnder(winner)
      return

    tiles_to_check = [self.get(z, self._board_size - z - 1)
                      for z in range(0, self._board_size)]
    winner = self.check_tiles_winner(tiles_to_check)
    if winner:
      self.declare_winnder(winner)
      return

    if self._state.count(TileState.EMPTY) == 0:
      self.declare_winnder(TileState.EMPTY)

  def declare_winnder(self, winner: TileState):
    self.winner = winner


class GameWindow(QtWidgets.QWidget):

  grid: QGridLayout
  game_state: GameState
  turn: TileState

  def __init__(self):
    super().__init__()
    self.game_state = GameState(GAME_SZIE, self._refresh_ui)
    self.turn = TileState.X
    self._init_window()
    self._init_ui()

  def _init_window(self):
    self.resize(800, 800)
    self.setWindowTitle("Multiplayer Tic Tac Teo")
    self.show()

  def _init_ui(self):
    self.grid = QGridLayout()
    self.setLayout(self.grid)

    for y in range(0, GAME_SZIE):
      for x in range(0, GAME_SZIE):
        button = QPushButton()
        button.setText(self.game_state.get(x, y).value)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.clicked.connect(self.get_tile_clicked_listener(button, x, y))
        self.grid.addWidget(button, y, x)

  def _get_button_at(self, x, y) -> QPushButton:
    return self.grid.itemAtPosition(y, x).widget()

  def _refresh_ui(self):
    for y in range(0, GAME_SZIE):
      for x in range(0, GAME_SZIE):
        txt = self.game_state.get(x, y).value
        self._get_button_at(x, y).setText(txt)

    winner = self.game_state.winner
    if winner:
      msgBox = QMessageBox()
      if winner == TileState.EMPTY:
        msgBox.setText(f"Tie")
      else:
        msgBox.setText(f"Winner is {winner.value}")
      msgBox.exec()
      self.game_state.new_game()

  def end_turn(self):
    if self.turn == TileState.X:
      self.turn = TileState.O
    else:
      self.turn = TileState.X

  def get_tile_clicked_listener(self, button: QPushButton, x: int, y: int):
    def click_action():
      if self.game_state.get(x, y) == TileState.EMPTY:
        self.game_state.set(x, y, self.turn)
        self.end_turn()
    return click_action


if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)

  window = GameWindow()

  sys.exit(app.exec())
