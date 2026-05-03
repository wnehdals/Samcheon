from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from app.constants import C


class TabBar(QWidget):
    """탭 네비게이션 바 뷰 (SRP: 탭 선택 UI 및 시그널 발행만 담당)"""

    tab_changed = pyqtSignal(int)
    TAB_NAMES = ["그룹생성", "메시지 전송", "전송이력"]

    def __init__(self):
        super().__init__()
        self.setFixedHeight(44)
        self.setStyleSheet(f"background: {C['white']}; border-bottom: 1px solid {C['border']};")
        self._buttons: list = []
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 0, 0)
        lay.setSpacing(0)
        for i, name in enumerate(self.TAB_NAMES):
            btn = QPushButton(name)
            btn.setFixedHeight(44)
            btn.setStyleSheet(self._tab_style(i == 0))
            btn.clicked.connect(lambda _, idx=i: self._on_click(idx))
            self._buttons.append(btn)
            lay.addWidget(btn)
        lay.addStretch()

    def _tab_style(self, active: bool) -> str:
        if active:
            return f"""
                QPushButton {{
                    background: transparent;
                    color: {C['text']};
                    border: none;
                    border-bottom: 3px solid {C['yellow']};
                    font-size: 13px;
                    font-weight: bold;
                    padding: 0 12px;
                }}
            """
        return f"""
            QPushButton {{
                background: transparent;
                color: {C['gray']};
                border: none;
                font-size: 13px;
                padding: 0 12px;
            }}
            QPushButton:hover {{ color: {C['text']}; }}
        """

    def _on_click(self, idx: int):
        for i, btn in enumerate(self._buttons):
            btn.setStyleSheet(self._tab_style(i == idx))
        self.tab_changed.emit(idx)

    def select_tab(self, idx: int):
        self._on_click(idx)

    def set_active_tab(self, idx: int):
        """tab_changed 시그널 없이 스타일만 갱신"""
        for i, btn in enumerate(self._buttons):
            btn.setStyleSheet(self._tab_style(i == idx))
