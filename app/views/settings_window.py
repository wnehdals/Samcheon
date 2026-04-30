from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QTextEdit, QWidget,
)
from PyQt5.QtCore import Qt
from app.constants import C, APP_VERSION, CHANGELOG
from app.views.widgets import h_separator


class SettingsWindow(QDialog):
    """설정 다이얼로그 (SRP: 설정 화면 UI만 담당)

    OCP 적용: NAV_ITEMS 리스트에 항목만 추가하면 새 설정 페이지를 확장 가능.
    """

    _NAV_ITEMS = [
        ("🔄 업데이트", "_build_update_page"),
        ("🖥 등록 디바이스", None),
        ("📁 파일 저장경로", None),
        ("🐛 카톡 버그방지", None),
        ("🎧 고객센터", None),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.setMinimumSize(820, 620)
        self.setStyleSheet(f"background: {C['white']};")
        self._nav_buttons: list = []
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        nav = QWidget()
        nav.setFixedWidth(220)
        nav.setStyleSheet(f"background: {C['panel']}; border-right: 1px solid {C['border']};")
        nv = QVBoxLayout(nav)
        nv.setContentsMargins(0, 0, 0, 0)
        nv.setSpacing(0)

        title = QLabel("설정")
        title.setFixedHeight(40)
        title.setContentsMargins(16, 0, 0, 0)
        title.setStyleSheet("color: #262626; font-size: 14px; font-weight: bold;")
        nv.addWidget(title)
        nv.addWidget(h_separator())

        self._stack = QStackedWidget()

        for i, (label, builder) in enumerate(self._NAV_ITEMS):
            btn = QPushButton(label)
            btn.setFixedHeight(44)
            btn.setStyleSheet(self._nav_style(i == 0))
            btn.clicked.connect(lambda _, idx=i: self._nav_click(idx))
            self._nav_buttons.append(btn)
            nv.addWidget(btn)

            if builder and hasattr(self, builder):
                self._stack.addWidget(getattr(self, builder)())
            else:
                ph = QLabel("준비 중입니다.")
                ph.setAlignment(Qt.AlignCenter)
                ph.setStyleSheet(f"color: {C['gray']}; font-size: 13px;")
                self._stack.addWidget(ph)

        nv.addStretch()
        lay.addWidget(nav)
        lay.addWidget(self._stack, 1)

    def _nav_style(self, active: bool) -> str:
        if active:
            return f"""
                QPushButton {{
                    background: {C['white']};
                    color: #262626;
                    border: none;
                    border-left: 3px solid {C['yellow']};
                    font-size: 12px;
                    font-weight: 600;
                    text-align: left;
                    padding-left: 13px;
                }}
            """
        return f"""
            QPushButton {{
                background: transparent;
                color: #666;
                border: none;
                font-size: 12px;
                text-align: left;
                padding-left: 16px;
            }}
            QPushButton:hover {{ background: {C['white']}; color: #262626; }}
        """

    def _nav_click(self, idx: int):
        for i, btn in enumerate(self._nav_buttons):
            btn.setStyleSheet(self._nav_style(i == idx))
        self._stack.setCurrentIndex(idx)

    def _build_update_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background: {C['white']};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(30, 20, 30, 20)
        lay.setSpacing(10)

        title = QLabel("🔄 업데이트")
        title.setStyleSheet("color: #262626; font-size: 16px; font-weight: bold;")
        lay.addWidget(title)
        lay.addWidget(h_separator())

        for ver_text in (f"현재 버전    {APP_VERSION}", f"최신 버전    {APP_VERSION}"):
            lbl = QLabel(ver_text)
            lbl.setStyleSheet("color: #4d4d4d; font-size: 12px;")
            lay.addWidget(lbl)

        up_btn = QPushButton("🔄 최신 버전입니다")
        up_btn.setFixedSize(500, 44)
        up_btn.setStyleSheet("""
            QPushButton {
                background: #b0c7ed;
                color: #405999;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        lay.addWidget(up_btn)

        change_lbl = QLabel("변경 사항")
        change_lbl.setStyleSheet("color: #262626; font-size: 13px; font-weight: bold;")
        lay.addWidget(change_lbl)

        changelog_edit = QTextEdit()
        changelog_edit.setReadOnly(True)
        changelog_edit.setMaximumWidth(500)
        changelog_edit.setFixedHeight(380)
        changelog_edit.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid #d9d9d9;
                background: {C['white']};
                color: #404040;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        changelog_edit.setPlainText(CHANGELOG)
        lay.addWidget(changelog_edit)
        lay.addStretch()
        return page
