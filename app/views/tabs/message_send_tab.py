from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QSpinBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from app.constants import C
from app.models.message_template import MessageTemplate
from app.views.widgets import h_separator, make_btn, panel_header_widget


class KakaoFriendPanel(QWidget):
    """카톡 친구창 패널 (SRP: 카카오톡 창 안내 UI만 담당)"""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(400)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(panel_header_widget("카톡 친구창"))
        hint = QLabel("카카오톡 친구창을 열어\n사각형 크기에 맞춰주세요")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"color: {C['gray']}; font-size: 11px;")
        lay.addWidget(hint, 1)


class ChatDialogPanel(QWidget):
    """대화창 + 로그 패널 (SRP: 로그 출력 UI만 담당)"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(panel_header_widget("대화창"))

        dialog_hint = QLabel("대화창을 사각형 크기에 맞춰주세요")
        dialog_hint.setAlignment(Qt.AlignCenter)
        dialog_hint.setStyleSheet(f"color: {C['light']}; font-size: 13px;")
        lay.addWidget(dialog_hint, 1)

        lay.addWidget(h_separator())






class AdvancedSettingsPanel(QWidget):
    """고급 설정 패널 (SRP: 설정 입력 UI 및 시그널만 담당)

    DIP 적용: 전송·초기화의 실제 처리는 시그널로 컨트롤러에 위임 —
    이전의 log_fn 콜백 의존성을 제거.
    """

    send_requested = pyqtSignal(int)
    pause_requested = pyqtSignal()
    reset_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedWidth(390)
        self.setStyleSheet(f"background: {C['white']};")
        self._is_sending = False
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(panel_header_widget("≡ 고급 설정"))

        inner = QWidget()
        inner.setStyleSheet(f"background: {C['white']};")
        il = QVBoxLayout(inner)
        il.setContentsMargins(16, 12, 16, 12)
        il.setSpacing(8)

        r1 = QHBoxLayout()
        lbl = QLabel("다음 상대에게 전송 대기 시간")
        lbl.setStyleSheet("color: #4d4d4d; font-size: 11px;")
        r1.addWidget(lbl)
        r1.addStretch()
        self._count_input = QSpinBox()
        self._count_input.setRange(1, 10)
        self._count_input.setValue(1)
        self._count_input.setFixedSize(64, 26)
        self._count_input.setStyleSheet(f"""
            QSpinBox {{
                border: 1px solid {C['border']};
                font-size: 11px;
                padding: 2px 4px;
            }}
            QSpinBox::up-button {{ width: 16px; }}
            QSpinBox::down-button {{ width: 16px; }}
        """)
        r1.addWidget(self._count_input)
        il.addLayout(r1)
        friend_term_label = QLabel("초")
        friend_term_label.setStyleSheet(f"color: {C['gray']}; font-size: 11px;")
        r1.addWidget(friend_term_label)

        r2 = QHBoxLayout()
        lbl2 = QLabel("텍스트 메시지 전송 대기 시간")
        lbl2.setStyleSheet("color: #4d4d4d; font-size: 11px;")
        r2.addWidget(lbl2)
        r2.addStretch()
        self._count_text_input = QSpinBox()
        self._count_text_input.setRange(1, 10)
        self._count_text_input.setValue(1)
        self._count_text_input.setFixedSize(64, 26)
        self._count_text_input.setStyleSheet(f"""
                   QSpinBox {{
                       border: 1px solid {C['border']};
                       font-size: 11px;
                       padding: 2px 4px;
                   }}
                   QSpinBox::up-button {{ width: 16px; }}
                   QSpinBox::down-button {{ width: 16px; }}
               """)
        r2.addWidget(self._count_text_input)
        il.addLayout(r2)
        text_term_label = QLabel("초")
        text_term_label.setStyleSheet(f"color: {C['gray']}; font-size: 11px;")
        r2.addWidget(text_term_label)


        r3 = QHBoxLayout()
        lbl3 = QLabel("파일 메시지 전송 대기 시간")
        lbl3.setStyleSheet("color: #4d4d4d; font-size: 11px;")
        r3.addWidget(lbl3)
        r3.addStretch()
        self._count_file_input = QSpinBox()
        self._count_file_input.setRange(1, 90)
        self._count_file_input.setValue(3)
        self._count_file_input.setFixedSize(64, 26)
        self._count_file_input.setStyleSheet(f"""
                   QSpinBox {{
                       border: 1px solid {C['border']};
                       font-size: 11px;
                       padding: 2px 4px;
                   }}
                   QSpinBox::up-button {{ width: 16px; }}
                   QSpinBox::down-button {{ width: 16px; }}
               """)
        r3.addWidget(self._count_file_input)
        il.addLayout(r3)
        file_term_label = QLabel("초")
        file_term_label.setStyleSheet(f"color: {C['gray']}; font-size: 11px;")
        r3.addWidget(file_term_label)

        self._count_input.valueChanged.connect(MessageTemplate.instance().set_send_term)
        self._count_text_input.valueChanged.connect(MessageTemplate.instance().set_send_text_term)
        self._count_file_input.valueChanged.connect(MessageTemplate.instance().set_send_file_term)

        il.addWidget(h_separator())

        log_hdr = QLabel("📋 Log")
        log_hdr.setFixedHeight(30)
        log_hdr.setContentsMargins(12, 0, 0, 0)
        log_hdr.setStyleSheet(
            f"color: {C['text']}; font-size: 11px; font-weight: 600; background: {C['white']};"
        )
        il.addWidget(log_hdr)

        self._log_edit = QTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setStyleSheet(f"""
                    QTextEdit {{
                        background: {C['log']};
                        color: #00ff00;
                        border: none;
                        font-family: Consolas, monospace;
                        font-size: 11px;
                        padding: 8px;
                    }}
                """)
        il.addWidget(self._log_edit, 1)

        self._send_btn = make_btn(
            "▶ 전송", bg=C["yellow"], fg=C["title"], border=C["yellow"],
            radius=4, font_size=13, bold=True, height=42,
        )
        self._send_btn.clicked.connect(self._on_send_btn_clicked)
        il.addWidget(self._send_btn)

        lay.addWidget(inner)

    def reset(self):
        """컨트롤러가 초기화 완료 후 호출 — 입력값 복원"""
        self._count_input.setValue(1)

    def _on_send_btn_clicked(self):
        if not self._is_sending:
            self._is_sending = True
            self._send_btn.setText("⏸ 일시 중지")
            self._send_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #888;
                    color: white;
                    border: 1px solid #888;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 0 8px;
                }}
                QPushButton:hover {{ background: #999; }}
                QPushButton:pressed {{ background: #999; }}
            """)
            self.send_requested.emit(self._count_input.value())
        else:
            self._is_sending = False
            self._send_btn.setText("▶ 전송")
            self._send_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C['yellow']};
                    color: {C['title']};
                    border: 1px solid {C['yellow']};
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 0 8px;
                }}
                QPushButton:hover {{ background: #e8b400; }}
                QPushButton:pressed {{ background: #e8b400; }}
            """)
            self.pause_requested.emit()

    def reset_send_btn(self):
        """전송 완료/오류 시 컨트롤러가 호출 — 버튼을 전송 상태로 복원"""
        self._is_sending = False
        self._send_btn.setText("▶ 전송")
        self._send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['yellow']};
                color: {C['title']};
                border: 1px solid {C['yellow']};
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 8px;
            }}
            QPushButton:hover {{ background: #e8b400; }}
            QPushButton:pressed {{ background: #e8b400; }}
        """)

    def append_log(self, msg: str):
        """컨트롤러가 호출 — 타임스탬프와 함께 로그 추가"""
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_edit.append(f"[{ts}] {msg}")

class MessageSendTab(QWidget):
    """메시지 전송 탭 — 하위 패널을 조합하는 컨테이너 뷰"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {C['bg']};")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.kakao_panel = KakaoFriendPanel()
        self.dialog_panel = ChatDialogPanel()
        self.adv_panel = AdvancedSettingsPanel()

        lay.addWidget(self.kakao_panel)
        lay.addWidget(self.dialog_panel, 1)
        lay.addWidget(self.adv_panel)
