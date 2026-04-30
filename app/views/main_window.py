from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from app.constants import C
from app.views.title_bar import TitleBar
from app.views.tab_bar import TabBar
from app.views.tabs.group_creation_tab import GroupCreationTab
from app.views.tabs.message_send_tab import MessageSendTab
from app.views.tabs.history_tab import HistoryTab
from app.views.settings_window import SettingsWindow


class MainWindow(QMainWindow):
    """메인 윈도우 — 타이틀 바·탭 바·탭 컨텐츠를 조립하는 최상위 뷰"""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(1653, 700)
        self.resize(1700, 820)
        self._settings_win = None
        self._build()

    def _build(self):
        central = QWidget()
        central.setStyleSheet(f"background: {C['bg']};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.title_bar = TitleBar(self)
        self.title_bar.settings_requested.connect(self.open_settings)
        root.addWidget(self.title_bar)

        self.tab_bar = TabBar()
        self.tab_bar.tab_changed.connect(self._switch_tab)
        root.addWidget(self.tab_bar)

        self._stack = QStackedWidget()
        self.group_creation_tab = GroupCreationTab()
        self.message_send_tab = MessageSendTab()
        self.history_tab = HistoryTab()
        self._stack.addWidget(self.group_creation_tab)
        self._stack.addWidget(self.message_send_tab)
        self._stack.addWidget(self.history_tab)
        root.addWidget(self._stack)

    def _switch_tab(self, idx: int):
        self._stack.setCurrentIndex(idx)

    def open_settings(self):
        if self._settings_win is None:
            self._settings_win = SettingsWindow(self)
        self._settings_win.exec_()
