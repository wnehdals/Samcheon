from datetime import datetime
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from app.constants import C, APP_VERSION, EXPIRE_DATE


class TitleBar(QWidget):
    """커스텀 타이틀 바 뷰 (SRP: UI 표시 및 윈도우 제어 시그널 발행만 담당)

    DIP 적용: 설정 열기는 settings_requested 시그널로 위임 — 직접 호출 없음.
    """

    settings_requested = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self._main_win = parent
        self._drag_pos = None
        self.setFixedHeight(40)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C['title']};")
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_expire)
        self._timer.start(1000)

    def _build(self):

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 0, 0)
        lay.setSpacing(0)

        icon = QLabel()
        icon.setFixedSize(22, 22)
        icon.setStyleSheet(f"background: {C['yellow']}; border-radius: 11px;")
        lay.addWidget(icon)
        lay.addSpacing(8)

        name = QLabel(f"삼촌카톡 PRO  {APP_VERSION}")
        name.setStyleSheet("color: white; font-size: 13px; font-weight: 600;")
        lay.addWidget(name)
        lay.addSpacing(20)

        self._expire_lbl = QLabel()
        self._expire_lbl.setStyleSheet(f"color: {C['light']}; font-size: 11px;")
        lay.addWidget(self._expire_lbl)
        self._update_expire()

        lay.addStretch()

        settings_btn = self._win_btn("⚙", fg=C["light"], bg="transparent", hover="#3a3a3a")
        settings_btn.clicked.connect(lambda: self.settings_requested.emit())
        lay.addWidget(settings_btn)

        min_btn = self._win_btn("─", fg="white", bg=C["hover"], hover="#3a3a3a")
        min_btn.clicked.connect(self._main_win.showMinimized)
        lay.addWidget(min_btn)

        self._max_btn = self._win_btn("□", fg="white", bg=C["hover"], hover="#3a3a3a")
        self._max_btn.clicked.connect(self._toggle_max)
        lay.addWidget(self._max_btn)

        close_btn = self._win_btn("✕", fg="white", bg=C["red"], hover="#f03030")
        close_btn.clicked.connect(self._main_win.close)
        lay.addWidget(close_btn)

    def _win_btn(self, text: str, fg: str, bg: str, hover: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(40, 40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {fg};
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{ background: {hover}; }}
        """)
        return btn

    def _update_expire(self):
        now = datetime.now()
        delta = EXPIRE_DATE - now
        total_h = int(delta.total_seconds() // 3600)
        rem_m = int((delta.total_seconds() % 3600) // 60)
        rem_s = int(delta.total_seconds() % 60)
        exp_str = EXPIRE_DATE.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
        self._expire_lbl.setText(
            f"{exp_str}까지  (남은시간 {total_h}시간 {rem_m}분 {rem_s}초)  ● 시스템 정상"
        )

    def _toggle_max(self):
        if self._main_win.isMaximized():
            self._main_win.showNormal()
        else:
            self._main_win.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self._main_win.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self._main_win.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        self._toggle_max()
