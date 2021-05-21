from game_state import GameState, TileState
from typing import Callable, List
from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import (
    QBoxLayout, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton, QSizePolicy, QVBoxLayout)
import sys
from PySide6.QtCore import Qt
from enum import Enum
from network import Connection
from tile_state import TileState

GAME_SZIE = 5

class GameWindow(QtWidgets.QWidget):

  grid: QGridLayout
  label: QLabel
  game_state: GameState

  def __init__(self, is_server: bool):
    super().__init__()
    self.is_server = is_server
    self.game_state = GameState(GAME_SZIE, self._refresh_ui)
    self._init_window()
    self._init_ui()
    self.game_state.setup_multiplayer_connection(is_server)

  def _init_window(self):
    self.resize(800, 800)

    if self.is_server == None:
      postfix = "single player"
    else:
      if self.is_server:
        postfix = "multi player (server)"
      else:
        postfix = "multi player (client)"

    self.setWindowTitle(f"Multiplayer Tic Tac Teo - {postfix}")
    self.show()

  def _init_ui(self):
    hbox = QVBoxLayout()
    self.setLayout(hbox)
    self.label = QLabel()
    self.label.setText(f"Turn {self.game_state.turn.value}")
    f: QtGui.QFont = self.label.font()
    f.setPixelSize(50)
    self.label.setFont(f)
    hbox.addWidget(self.label, alignment=Qt.AlignCenter)
    self.grid = QGridLayout()
    hbox.addLayout(self.grid)

    for y in range(0, GAME_SZIE):
      for x in range(0, GAME_SZIE):
        button = QPushButton()
        button.setText(self.game_state.get(x, y).value)
        f: QtGui.QFont = button.font()
        f.setPixelSize(50)
        button.setFont(f)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.clicked.connect(self.get_tile_clicked_listener(button, x, y))
        self.grid.addWidget(button, y, x)

  def _get_button_at(self, x, y) -> QPushButton:
    return self.grid.itemAtPosition(y, x).widget()

  def _refresh_ui(self):
    self.label.setText(f"Turn {self.game_state.turn.value}")

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

  def get_tile_clicked_listener(self, button: QPushButton, x: int, y: int):
    def click_action():
      if self.game_state.user_tile_type == self.game_state.turn:
        self.game_state.set(x, y, self.game_state.user_tile_type)
    return click_action


if __name__ == "__main__":
  is_server = None
  if len(sys.argv) == 2:
    is_server = sys.argv[1] == "server"

  app = QtWidgets.QApplication(sys.argv)

  window = GameWindow(is_server)

  sys.exit(app.exec())
