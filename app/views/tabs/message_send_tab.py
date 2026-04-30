from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit,
)
from PyQt5.QtCore import Qt, pyqtSignal
from app.constants import C
from app.views.widgets import h_separator, make_btn, panel_header_widget


class KakaoFriendPanel(QWidget):
    """카톡 친구창 패널 (SRP: 카카오톡 창 안내 UI만 담당)"""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(376)
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

        log_hdr = QLabel("📋 Log")
        log_hdr.setFixedHeight(30)
        log_hdr.setContentsMargins(12, 0, 0, 0)
        log_hdr.setStyleSheet(
            f"color: {C['text']}; font-size: 11px; font-weight: 600; background: {C['white']};"
        )
        lay.addWidget(log_hdr)

        self._log_edit = QTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setFixedHeight(200)
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
        lay.addWidget(self._log_edit)

    def append_log(self, msg: str):
        """컨트롤러가 호출 — 타임스탬프와 함께 로그 추가"""
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_edit.append(f"[{ts}] {msg}")


class AdvancedSettingsPanel(QWidget):
    """고급 설정 패널 (SRP: 설정 입력 UI 및 시그널만 담당)

    DIP 적용: 전송·초기화의 실제 처리는 시그널로 컨트롤러에 위임 —
    이전의 log_fn 콜백 의존성을 제거.
    """

    send_requested = pyqtSignal(int)  # 전송 횟수
    reset_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedWidth(390)
        self.setStyleSheet(f"background: {C['white']};")
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
        lbl = QLabel("전송횟수")
        lbl.setStyleSheet("color: #4d4d4d; font-size: 11px;")
        r1.addWidget(lbl)
        hint = QLabel("0 무한반복")
        hint.setStyleSheet(f"color: {C['gray']}; font-size: 11px;")
        r1.addWidget(hint)
        r1.addStretch()
        self._count_input = QLineEdit("1")
        self._count_input.setFixedSize(52, 26)
        self._count_input.setStyleSheet(
            f"border: 1px solid {C['border']}; font-size: 11px; padding: 2px 4px;"
        )
        r1.addWidget(self._count_input)
        il.addLayout(r1)

        r2 = QHBoxLayout()
        lbl2 = QLabel("종료시간")
        lbl2.setStyleSheet("color: #4d4d4d; font-size: 11px;")
        r2.addWidget(lbl2)
        r2.addStretch()
        il.addLayout(r2)
        il.addWidget(h_separator())

        run_lbl = QLabel("▶ 실행")
        run_lbl.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        il.addWidget(run_lbl)

        save_cnt_btn = make_btn("≡ 채팅방 인원수 저장", border=C["yellow"], height=38, font_size=12)
        il.addWidget(save_cnt_btn)

        reset_btn = make_btn("↺ 초기화", height=38, font_size=12)
        reset_btn.clicked.connect(lambda: self.reset_requested.emit())
        il.addWidget(reset_btn)

        il.addStretch()

        send_btn = make_btn(
            "▶ 전송", bg=C["yellow"], fg=C["title"], border=C["yellow"],
            radius=4, font_size=13, bold=True, height=42,
        )
        send_btn.clicked.connect(self._emit_send)
        il.addWidget(send_btn)

        lay.addWidget(inner)

    def reset(self):
        """컨트롤러가 초기화 완료 후 호출 — 입력값 복원"""
        self._count_input.setText("1")

    def _emit_send(self):
        try:
            count = int(self._count_input.text())
        except ValueError:
            count = 1
        self.send_requested.emit(count)


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
