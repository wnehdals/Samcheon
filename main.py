#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이지카톡 PRO v1.11.0
카카오톡 메시지 자동전송 프로그램
"""

import sys
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget,
    QFrame, QStackedWidget, QScrollArea, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QInputDialog, QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

# ────── 앱 상수 ──────
APP_VERSION = "v1.11.0"
EXPIRE_DATE = datetime(2099, 12, 31, 23, 59, 59)

# ────── 색상 상수 ──────
C = {
    "title":   "#1a1a1a",
    "bg":      "#f2f2f2",
    "white":   "#ffffff",
    "yellow":  "#f5c800",
    "green":   "#16a046",
    "border":  "#e0e0e0",
    "text":    "#333333",
    "gray":    "#808080",
    "light":   "#b3b3b3",
    "red":     "#d92626",
    "panel":   "#fafafa",
    "log":     "#141414",
    "hover":   "#262626",
}

CHANGELOG = """\
[1.11.0]
- 전송 중 창 최소화 기능 추가
- 전송 중 창 최소화 시 플로팅 되어 진행상황 표시

[1.10.0]
- 즉시전송 기능 추가

[1.9.1]
- 모바일 앱에서 실패 채팅방을 재전송할 수 있도록 기능 개선

[1.9.0]
- 전송이력 중 전송실패 항목 재전송하는 기능 추가
- PC, 모바일 중 어떤 매개체로 전송하였는지 이력항목 추가
- 전송이력 새로고침 기능 추가

[1.8.1]
- 전체 자동등록, 채팅방 열기, 전송 중 방 열기, 인원수 조회 실행 시 프로세스 속도 조절 적용되도록 수정

[1.8.0]
- 설정(톱니바퀴) → 업데이트 메뉴에 업데이트 이력 추가
- 설정(톱니바퀴) → 카톡버그 방지용 설정 추가
"""


# ────── 공통 헬퍼 ──────
def h_separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet(f"background: {C['border']}; border: none;")
    return line


def make_btn(text, bg=None, fg=None, border=None, radius=4, font_size=11, bold=False, height=34):
    bg = bg or C["white"]
    fg = fg or C["text"]
    border = border or C["border"]
    weight = "bold" if bold else "normal"
    btn = QPushButton(text)
    btn.setFixedHeight(height)
    hover_bg = "#e8b400" if bg == C["yellow"] else ("#128a3c" if bg == C["green"] else C["panel"])
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg};
            color: {fg};
            border: 1px solid {border};
            border-radius: {radius}px;
            font-size: {font_size}px;
            font-weight: {weight};
            padding: 0 8px;
        }}
        QPushButton:hover {{ background: {hover_bg}; }}
        QPushButton:pressed {{ background: {hover_bg}; }}
    """)
    return btn


def panel_header_widget(title: str) -> QWidget:
    w = QWidget()
    w.setStyleSheet(f"background: {C['white']};")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)
    lbl = QLabel(title)
    lbl.setFixedHeight(28)
    lbl.setContentsMargins(12, 0, 0, 0)
    lbl.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
    lay.addWidget(lbl)
    lay.addWidget(h_separator())
    return w


# ────── 타이틀 바 ──────
class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_win = parent
        self._drag_pos = None
        self.setFixedHeight(40)
        self.setStyleSheet(f"background: {C['title']};")
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_expire)
        self._timer.start(1000)

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 0, 0)
        lay.setSpacing(0)

        # 앱 아이콘 (노란 원형)
        icon = QLabel()
        icon.setFixedSize(22, 22)
        icon.setStyleSheet(f"background: {C['yellow']}; border-radius: 11px;")
        lay.addWidget(icon)
        lay.addSpacing(8)

        # 앱 이름
        name = QLabel(f"이지카톡 PRO  {APP_VERSION}")
        name.setStyleSheet("color: white; font-size: 13px; font-weight: 600;")
        lay.addWidget(name)
        lay.addSpacing(20)

        # 만료 / 상태 정보
        self.expire_lbl = QLabel()
        self.expire_lbl.setStyleSheet(f"color: {C['light']}; font-size: 11px;")
        lay.addWidget(self.expire_lbl)
        self._update_expire()

        lay.addStretch()

        # 설정 버튼
        settings_btn = self._win_btn("⚙", fg=C["light"], bg="transparent", hover="#3a3a3a")
        settings_btn.clicked.connect(self.main_win.open_settings)
        lay.addWidget(settings_btn)

        # 최소화
        min_btn = self._win_btn("─", fg="white", bg=C["hover"], hover="#3a3a3a")
        min_btn.clicked.connect(self.main_win.showMinimized)
        lay.addWidget(min_btn)

        # 최대화
        self.max_btn = self._win_btn("□", fg="white", bg=C["hover"], hover="#3a3a3a")
        self.max_btn.clicked.connect(self._toggle_max)
        lay.addWidget(self.max_btn)

        # 닫기
        close_btn = self._win_btn("✕", fg="white", bg=C["red"], hover="#f03030")
        close_btn.clicked.connect(self.main_win.close)
        lay.addWidget(close_btn)

    def _win_btn(self, text, fg, bg, hover):
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
        self.expire_lbl.setText(
            f"{exp_str}까지  (남은시간 {total_h}시간 {rem_m}분 {rem_s}초)  ● 시스템 정상"
        )

    def _toggle_max(self):
        if self.main_win.isMaximized():
            self.main_win.showNormal()
        else:
            self.main_win.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.main_win.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.main_win.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        self._toggle_max()


# ────── 탭 바 ──────
class TabBar(QWidget):
    tab_changed = pyqtSignal(int)
    TAB_NAMES = ["그룹생성", "메시지 전송", "전송이력"]

    def __init__(self):
        super().__init__()
        self.setFixedHeight(44)
        self.setStyleSheet(f"background: {C['white']}; border-bottom: 1px solid {C['border']};")
        self._buttons = []
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 0, 0)
        lay.setSpacing(0)
        for i, name in enumerate(self.TAB_NAMES):
            btn = QPushButton(name)
            btn.setFixedHeight(44)
            btn.setStyleSheet(self._style(i == 0))
            btn.clicked.connect(lambda _, idx=i: self._click(idx))
            self._buttons.append(btn)
            lay.addWidget(btn)
        lay.addStretch()

    def _style(self, active: bool) -> str:
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

    def _click(self, idx: int):
        for i, btn in enumerate(self._buttons):
            btn.setStyleSheet(self._style(i == idx))
        self.tab_changed.emit(idx)


# ════════════════════════════════════
#  Screen 1 — 그룹생성 패널들
# ════════════════════════════════════

class GroupListPanel(QWidget):
    """왼쪽: 그룹 리스트 (220px)"""
    group_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        self.groups = ["테스트2"]
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.header_lbl = QLabel()
        self.header_lbl.setFixedHeight(28)
        self.header_lbl.setContentsMargins(12, 0, 0, 0)
        self.header_lbl.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(self.header_lbl)
        lay.addWidget(h_separator())

        add_btn = QPushButton("+ 새 그룹추가")
        add_btn.setFixedHeight(34)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['white']};
                color: {C['text']};
                border: 1px solid {C['yellow']};
                border-radius: 4px;
                font-size: 12px;
                margin: 6px 10px;
            }}
            QPushButton:hover {{ background: #fff9e0; }}
        """)
        add_btn.clicked.connect(self._add_group)
        lay.addWidget(add_btn)

        self.list_w = QListWidget()
        self.list_w.setStyleSheet(f"""
            QListWidget {{
                background: {C['white']};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                height: 36px;
                border-bottom: 1px solid {C['border']};
                padding-left: 10px;
                color: {C['text']};
                font-size: 12px;
            }}
            QListWidget::item:selected {{
                background: #fff9e0;
                border-left: 3px solid {C['yellow']};
            }}
        """)
        self.list_w.currentTextChanged.connect(self.group_selected.emit)
        lay.addWidget(self.list_w)
        self._refresh()

    def _refresh(self):
        self.list_w.clear()
        for g in self.groups:
            self.list_w.addItem(g)
        self.header_lbl.setText(f"그룹 리스트  ({len(self.groups)}개)")

    def _add_group(self):
        name, ok = QInputDialog.getText(self, "새 그룹추가", "그룹 이름:")
        if ok and name.strip():
            self.groups.append(name.strip())
            self._refresh()


class ChatRoomPanel(QWidget):
    """채팅방 리스트 (261px)"""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(261)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        self.rooms = ["김친구", "박친구"]
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.header_lbl = QLabel("테스트2")
        self.header_lbl.setFixedHeight(28)
        self.header_lbl.setContentsMargins(12, 0, 0, 0)
        self.header_lbl.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(self.header_lbl)
        lay.addWidget(h_separator())

        # 검색 행
        search_row = QWidget()
        search_row.setFixedHeight(44)
        search_row.setStyleSheet(f"background: {C['white']};")
        sr = QHBoxLayout(search_row)
        sr.setContentsMargins(10, 6, 10, 6)
        sr.setSpacing(4)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("채팅방 이름 검색")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {C['border']};
                border-radius: 4px;
                font-size: 11px;
                padding: 2px 6px;
            }}
        """)
        sr.addWidget(self.search_input)
        s_btn = make_btn("검색", height=30, font_size=10)
        s_btn.setFixedWidth(46)
        sr.addWidget(s_btn)
        lay.addWidget(search_row)

        # 통계 행
        stats_w = QWidget()
        stats_w.setFixedHeight(28)
        stats_w.setStyleSheet(f"background: {C['panel']};")
        st = QHBoxLayout(stats_w)
        st.setContentsMargins(12, 0, 12, 0)
        self.stats_lbl = QLabel(f"친구 {len(self.rooms)} ")
        self.stats_lbl.setStyleSheet(f"color: #666; font-size: 11px;")
        st.addWidget(self.stats_lbl)
        st.addStretch()
        lay.addWidget(stats_w)
        lay.addWidget(h_separator())

        self.list_w = QListWidget()
        self.list_w.setStyleSheet(f"""
            QListWidget {{
                background: {C['white']};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                height: 36px;
                border-bottom: 1px solid {C['border']};
                padding-left: 10px;
                color: {C['text']};
                font-size: 12px;
            }}
            QListWidget::item:selected {{
                background: #fff9e0;
                border-left: 3px solid {C['yellow']};
            }}
        """)
        for r in self.rooms:
            self.list_w.addItem(r)
        lay.addWidget(self.list_w)

    def set_group(self, name: str):
        self.header_lbl.setText(name)


class FileAttachPanel(QWidget):
    """파일 첨부 + 텍스트 메시지 작성 (253px)"""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(253)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        self.files = ["이미지 첨부 파일.png", "동영상 첨부 파일.mp4"]
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # 파일 목록 헤더
        self.file_header = QLabel(f"파일 목록  ({len(self.files)}개)")
        self.file_header.setFixedHeight(28)
        self.file_header.setContentsMargins(12, 0, 0, 0)
        self.file_header.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(self.file_header)
        lay.addWidget(h_separator())

        # 파일 리스트
        self.file_list = QListWidget()
        self.file_list.setFixedHeight(110)
        self.file_list.setAcceptDrops(True)
        self.file_list.setDragDropMode(QAbstractItemView.DropOnly)
        self.file_list.setStyleSheet(f"""
            QListWidget {{
                background: {C['panel']};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                height: 48px;
                border: 1px solid #d1d1d1;
                margin: 2px 8px;
                padding-left: 8px;
                color: {C['text']};
                font-size: 11px;
            }}
            QListWidget::item:selected {{ background: #fff9e0; }}
        """)
        for f in self.files:
            self.file_list.addItem(f)
        lay.addWidget(self.file_list)

        # 파일 저장경로
        path_btn = make_btn("📁 파일 저장경로", height=34, font_size=11)
        path_btn.setStyleSheet(path_btn.styleSheet() + "margin: 6px 10px;")
        path_btn.clicked.connect(self._choose_path)
        lay.addWidget(path_btn)
        lay.addWidget(h_separator())

        # 텍스트 메시지 작성 헤더
        msg_hdr = QLabel("텍스트 메시지 작성")
        msg_hdr.setFixedHeight(28)
        msg_hdr.setContentsMargins(12, 0, 0, 0)
        msg_hdr.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(msg_hdr)
        lay.addWidget(h_separator())

        # 메시지 입력
        self.msg_edit = QTextEdit()
        self.msg_edit.setPlaceholderText("메시지를 입력하세요...")
        self.msg_edit.setStyleSheet(f"""
            QTextEdit {{
                background: {C['white']};
                color: {C['text']};
                border: 1px solid {C['border']};
                font-size: 12px;
                margin: 6px 10px;
            }}
        """)
        lay.addWidget(self.msg_edit)

        # 메시지 변수 / 메시지 추가
        for label in ("메시지 변수", "메시지 추가"):
            btn = make_btn(label, height=34, font_size=11)
            btn.setStyleSheet(btn.styleSheet() + "margin: 2px 10px;")
            lay.addWidget(btn)

        lay.addWidget(h_separator())

        # 새 그룹저장 / 그룹저장
        save_row = QWidget()
        save_row.setStyleSheet(f"background: {C['white']};")
        sr = QHBoxLayout(save_row)
        sr.setContentsMargins(10, 6, 10, 6)
        sr.setSpacing(4)
        sr.addWidget(make_btn("⬛ 새 그룹저장", height=38, font_size=11))
        sr.addWidget(make_btn("⬛ 그룹저장", bg=C["yellow"], fg=C["title"], border=C["yellow"], height=38, font_size=11))
        lay.addWidget(save_row)

        # 즉시전송
        lay.addWidget(make_btn("▶ 즉시전송", bg=C["green"], fg="white", border=C["green"],
                               radius=4, font_size=13, bold=True, height=42))

    def _choose_path(self):
        QFileDialog.getExistingDirectory(self, "파일 저장경로 선택")


class MessageListPanel(QWidget):
    """텍스트 메시지 목록 (276px)"""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(276)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        self.messages = ["좋은 하루 보내세요", "오늘 와주셔서 감사합니다."]
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.header_lbl = QLabel(f"텍스트 메시지 목록  ({len(self.messages)}개)")
        self.header_lbl.setFixedHeight(28)
        self.header_lbl.setContentsMargins(12, 0, 0, 0)
        self.header_lbl.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(self.header_lbl)
        lay.addWidget(h_separator())

        self.list_w = QListWidget()
        self.list_w.setStyleSheet(f"""
            QListWidget {{
                background: {C['white']};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                height: 48px;
                border: 1px solid #d1d1d1;
                margin: 2px 8px;
                padding: 4px 8px;
                color: {C['text']};
                font-size: 11px;
                background: {C['panel']};
            }}
            QListWidget::item:selected {{ background: #fff9e0; }}
        """)
        for m in self.messages:
            self.list_w.addItem(m)
        lay.addWidget(self.list_w)


class MessagePreviewPanel(QWidget):
    """메시지 미리보기 / 저장 (390px, 확장 가능)"""

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(390)
        self.setStyleSheet(f"background: {C['white']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        header = QLabel("메시지 작성")
        header.setFixedHeight(28)
        header.setContentsMargins(12, 0, 0, 0)
        header.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(header)
        lay.addWidget(h_separator())

        # 미리보기 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: 1px solid {C['border']}; margin: 6px 10px; background: {C['white']}; }}
        """)
        preview_w = QWidget()
        preview_w.setStyleSheet(f"background: {C['white']};")
        pv = QVBoxLayout(preview_w)
        pv.setContentsMargins(12, 12, 12, 12)
        pv.setSpacing(8)

        bubbles = ["좋은 하루 보내세요", "[이미지 첨부]", "오늘 와주셔서 감사합니다.", "[이미지 첨부]"]
        for msg in bubbles:
            b = QLabel(msg)
            b.setWordWrap(True)
            b.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            b.setStyleSheet(f"""
                background: {C['yellow']};
                border-radius: 14px;
                padding: 10px 14px;
                font-size: 12px;
                color: #000;
            """)
            pv.addWidget(b)
        pv.addStretch()
        scroll.setWidget(preview_w)
        lay.addWidget(scroll)
        lay.addWidget(h_separator())

        lay.addWidget(make_btn("저장", bg=C["green"], fg="white", border=C["green"],
                               radius=4, font_size=13, bold=True, height=42))


class GroupCreationTab(QWidget):
    """Screen 1 — 그룹생성"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {C['bg']};")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.group_panel = GroupListPanel()
        self.room_panel = ChatRoomPanel()
        self.file_panel = FileAttachPanel()
        self.msg_list_panel = MessageListPanel()
        self.preview_panel = MessagePreviewPanel()

        self.group_panel.group_selected.connect(self.room_panel.set_group)

        for w in (self.group_panel, self.room_panel, self.file_panel,
                  self.msg_list_panel, self.preview_panel):
            lay.addWidget(w)


# ════════════════════════════════════
#  Screen 2 — 메시지 전송 패널들
# ════════════════════════════════════

class KakaoFriendPanel(QWidget):
    """카톡 친구창 자리 (376px)"""

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
    """대화창 + 로그 패널"""

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
        log_hdr.setStyleSheet(f"color: {C['text']}; font-size: 11px; font-weight: 600; background: {C['white']};")
        lay.addWidget(log_hdr)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFixedHeight(200)
        self.log_edit.setStyleSheet(f"""
            QTextEdit {{
                background: {C['log']};
                color: #00ff00;
                border: none;
                font-family: Consolas, monospace;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        lay.addWidget(self.log_edit)

    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_edit.append(f"[{ts}] {msg}")


class AdvancedSettingsPanel(QWidget):
    """고급 설정 (390px)"""

    def __init__(self, log_fn=None):
        super().__init__()
        self.setFixedWidth(390)
        self.setStyleSheet(f"background: {C['white']};")
        self.log_fn = log_fn
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

        # 전송횟수
        r1 = QHBoxLayout()
        lbl = QLabel("전송횟수")
        lbl.setStyleSheet(f"color: #4d4d4d; font-size: 11px;")
        r1.addWidget(lbl)
        hint = QLabel("0 무한반복")
        hint.setStyleSheet(f"color: {C['gray']}; font-size: 11px;")
        r1.addWidget(hint)
        r1.addStretch()
        self.count_input = QLineEdit("1")
        self.count_input.setFixedSize(52, 26)
        self.count_input.setStyleSheet(f"border: 1px solid {C['border']}; font-size: 11px; padding: 2px 4px;")
        r1.addWidget(self.count_input)
        il.addLayout(r1)

        # 종료시간
        r2 = QHBoxLayout()
        lbl2 = QLabel("종료시간")
        lbl2.setStyleSheet(f"color: #4d4d4d; font-size: 11px;")
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
        reset_btn.clicked.connect(self._reset)
        il.addWidget(reset_btn)

        il.addStretch()

        send_btn = make_btn("▶ 전송", bg=C["yellow"], fg=C["title"], border=C["yellow"],
                            radius=4, font_size=13, bold=True, height=42)
        send_btn.clicked.connect(self._send)
        il.addWidget(send_btn)

        lay.addWidget(inner)

    def _reset(self):
        self.count_input.setText("1")
        if self.log_fn:
            self.log_fn("초기화 완료")

    def _send(self):
        if self.log_fn:
            self.log_fn(f"전송 시작 (횟수: {self.count_input.text()})")


class MessageSendTab(QWidget):
    """Screen 2 — 메시지 전송"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {C['bg']};")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.kakao_panel = KakaoFriendPanel()
        self.dialog_panel = ChatDialogPanel()
        self.adv_panel = AdvancedSettingsPanel(log_fn=self.dialog_panel.log)

        lay.addWidget(self.kakao_panel)
        lay.addWidget(self.dialog_panel, 1)
        lay.addWidget(self.adv_panel)


# ════════════════════════════════════
#  Screen 3 — 설정 (별도 다이얼로그)
# ════════════════════════════════════

class SettingsWindow(QDialog):
    NAV_ITEMS = [
        ("🔄 업데이트", "_update_page"),
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
        self._nav_buttons = []
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # 네비게이션
        nav = QWidget()
        nav.setFixedWidth(220)
        nav.setStyleSheet(f"background: {C['panel']}; border-right: 1px solid {C['border']};")
        nv = QVBoxLayout(nav)
        nv.setContentsMargins(0, 0, 0, 0)
        nv.setSpacing(0)

        title = QLabel("설정")
        title.setFixedHeight(40)
        title.setContentsMargins(16, 0, 0, 0)
        title.setStyleSheet(f"color: #262626; font-size: 14px; font-weight: bold;")
        nv.addWidget(title)
        nv.addWidget(h_separator())

        self.stack = QStackedWidget()

        for i, (label, page_fn) in enumerate(self.NAV_ITEMS):
            btn = QPushButton(label)
            btn.setFixedHeight(44)
            btn.setStyleSheet(self._nav_style(i == 0))
            btn.clicked.connect(lambda _, idx=i: self._nav_click(idx))
            self._nav_buttons.append(btn)
            nv.addWidget(btn)

            if page_fn and hasattr(self, page_fn):
                self.stack.addWidget(getattr(self, page_fn)())
            else:
                ph = QLabel("준비 중입니다.")
                ph.setAlignment(Qt.AlignCenter)
                ph.setStyleSheet(f"color: {C['gray']}; font-size: 13px;")
                self.stack.addWidget(ph)

        nv.addStretch()
        lay.addWidget(nav)
        lay.addWidget(self.stack, 1)

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
        self.stack.setCurrentIndex(idx)

    def _update_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background: {C['white']};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(30, 20, 30, 20)
        lay.setSpacing(10)

        title = QLabel("🔄 업데이트")
        title.setStyleSheet(f"color: #262626; font-size: 16px; font-weight: bold;")
        lay.addWidget(title)
        lay.addWidget(h_separator())

        for ver_text in (f"현재 버전    {APP_VERSION}", f"최신 버전    {APP_VERSION}"):
            lbl = QLabel(ver_text)
            lbl.setStyleSheet(f"color: #4d4d4d; font-size: 12px;")
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
        change_lbl.setStyleSheet(f"color: #262626; font-size: 13px; font-weight: bold;")
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


# ════════════════════════════════════
#  Screen 4 — 전송이력
# ════════════════════════════════════

class HistoryTab(QWidget):
    """Screen 4 — 전송이력"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {C['white']};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # 툴바
        toolbar = QWidget()
        toolbar.setFixedHeight(44)
        toolbar.setStyleSheet(f"background: {C['white']}; border-bottom: 1px solid {C['border']};")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(14, 0, 14, 0)
        tb.setSpacing(10)
        title = QLabel("🕐 전송이력  (최근 7일 · 7일 경과 시 자동 삭제)")
        title.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        tb.addWidget(title)
        tb.addStretch()
        refresh_btn = make_btn("↺ 새로고침", height=30, font_size=11)
        refresh_btn.setFixedWidth(90)
        tb.addWidget(refresh_btn)
        lay.addWidget(toolbar)

        # 테이블
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["전송일시", "그룹명", "채팅방", "메시지", "결과", "매개체"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                font-size: 12px;
                color: {C['text']};
                gridline-color: {C['border']};
            }}
            QTableWidget::item {{ padding: 6px; }}
            QHeaderView::section {{
                background: {C['panel']};
                border: none;
                border-bottom: 1px solid {C['border']};
                border-right: 1px solid {C['border']};
                font-size: 12px;
                font-weight: 600;
                color: {C['text']};
                padding: 6px;
            }}
            QTableWidget::item:alternate {{ background: #f9f9f9; }}
        """)
        lay.addWidget(self.table)


# ════════════════════════════════════
#  메인 윈도우
# ════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(1100, 700)
        self.resize(1400, 820)
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
        root.addWidget(self.title_bar)

        self.tab_bar = TabBar()
        self.tab_bar.tab_changed.connect(self._switch_tab)
        root.addWidget(self.tab_bar)

        self.stack = QStackedWidget()
        self.stack.addWidget(GroupCreationTab())
        self.stack.addWidget(MessageSendTab())
        self.stack.addWidget(HistoryTab())
        root.addWidget(self.stack)

    def _switch_tab(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def open_settings(self):
        if self._settings_win is None:
            self._settings_win = SettingsWindow(self)
        self._settings_win.exec_()


# ────── 진입점 ──────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("맑은 고딕", 9))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
