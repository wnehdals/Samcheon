import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QTextEdit, QScrollArea, QSizePolicy,
    QAbstractItemView, QFileDialog, QStackedWidget,
)
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from app.constants import C
from app.views.widgets import h_separator, make_btn

_EXCEL_EXTENSIONS = {'.xlsx', '.xls', '.xlsm', '.xlsb', '.xltx', '.xltm'}


class GroupListPanel(QWidget):
    """그룹 리스트 패널 (SRP: 저장경로 선택 및 그룹 파일 목록 표시만 담당)"""

    save_path_changed = pyqtSignal(str)   # 선택된 저장경로
    group_selected = pyqtSignal(str)      # 선택된 그룹 파일명

    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        self._save_path = ""
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._header_lbl = QLabel("그룹 파일 목록  (0개)")
        self._header_lbl.setFixedHeight(28)
        self._header_lbl.setContentsMargins(12, 0, 0, 0)
        self._header_lbl.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(self._header_lbl)
        lay.addWidget(h_separator())

        path_btn = QPushButton("📁 그룹파일 저장경로")
        path_btn.setFixedHeight(34)
        path_btn.setStyleSheet(f"""
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
        path_btn.clicked.connect(self._browse_save_path)
        lay.addWidget(path_btn)

        self._stack = QStackedWidget()

        placeholder = QLabel("그룹파일 경로를\n선택해주세요")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #aaa; font-size: 12px;")
        self._stack.addWidget(placeholder)  # index 0

        self._list_w = QListWidget()
        self._list_w.setSelectionMode(QAbstractItemView.SingleSelection)
        self._list_w.setStyleSheet(f"""
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
        self._list_w.currentTextChanged.connect(self.group_selected)
        self._stack.addWidget(self._list_w)  # index 1

        lay.addWidget(self._stack)

    def _browse_save_path(self):
        """파일 탐색기로 저장경로 선택 후 그룹 파일 목록 갱신"""
        path = QFileDialog.getExistingDirectory(self, "그룹파일 저장경로 선택", self._save_path or "")
        if path:
            self._save_path = path
            self.save_path_changed.emit(path)
            self._load_excel_files(path)

    def _load_excel_files(self, path: str):
        """선택된 경로의 그룹 파일만 목록에 표시하고 첫 항목 자동 선택"""
        try:
            files = sorted(
                f for f in os.listdir(path)
                if os.path.splitext(f)[1].lower() in _EXCEL_EXTENSIONS
            )
        except OSError:
            files = []
        self._list_w.clear()
        for f in files:
            self._list_w.addItem(f)
        self._header_lbl.setText(f"그룹 파일 목록  ({len(files)}개)")
        if files:
            self._list_w.setCurrentRow(0)
            self._stack.setCurrentIndex(1)
        else:
            self._stack.setCurrentIndex(0)

    def set_groups(self, groups: list):
        """컨트롤러 하위 호환용 — 외부에서 목록 갱신 시 사용"""
        self._list_w.clear()
        for g in groups:
            self._list_w.addItem(g)
        self._header_lbl.setText(f"그룹 파일 목록  ({len(groups)}개)")
        if groups:
            self._list_w.setCurrentRow(0)
            self._stack.setCurrentIndex(1)
        else:
            self._stack.setCurrentIndex(0)


class ChatRoomPanel(QWidget):
    """친구 리스트 패널 (SRP: 채팅방 목록 표시만 담당)"""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(261)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        self._all_rooms: list = []
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._header_lbl = QLabel()
        self._header_lbl.setFixedHeight(28)
        self._header_lbl.setContentsMargins(12, 0, 0, 0)
        self._header_lbl.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(self._header_lbl)
        lay.addWidget(h_separator())

        search_row = QWidget()
        search_row.setFixedHeight(44)
        search_row.setStyleSheet(f"background: {C['white']};")
        sr = QHBoxLayout(search_row)
        sr.setContentsMargins(10, 6, 10, 6)
        sr.setSpacing(4)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("친구 이름 검색")
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {C['border']};
                border-radius: 4px;
                font-size: 11px;
                padding: 2px 6px;
                color: {C['text']};
            }}
        """)
        sr.addWidget(self._search_input)
        s_btn = make_btn("검색", height=30, font_size=10)
        s_btn.setFixedWidth(46)
        s_btn.clicked.connect(self._apply_search)
        sr.addWidget(s_btn)
        lay.addWidget(search_row)

        stats_w = QWidget()
        stats_w.setFixedHeight(28)
        stats_w.setStyleSheet(f"background: {C['panel']};")
        st = QHBoxLayout(stats_w)
        st.setContentsMargins(12, 0, 12, 0)
        self._stats_lbl = QLabel()
        self._stats_lbl.setStyleSheet("color: #666; font-size: 11px;")
        st.addWidget(self._stats_lbl)
        st.addStretch()
        lay.addWidget(stats_w)
        lay.addWidget(h_separator())

        self._list_w = QListWidget()
        self._list_w.setStyleSheet(f"""
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
        lay.addWidget(self._list_w)

    def set_group_name(self, name: str):
        self._header_lbl.setText(name)

    def set_rooms(self, rooms: list):
        self._all_rooms = rooms
        self._search_input.clear()
        self._render_rooms(rooms)

    def _apply_search(self):
        keyword = self._search_input.text().strip()
        filtered = [r for r in self._all_rooms if keyword in r] if keyword else self._all_rooms
        self._render_rooms(filtered)

    def _render_rooms(self, rooms: list):
        self._list_w.clear()
        for r in rooms:
            self._list_w.addItem(r)
        self._stats_lbl.setText(f"총 {len(rooms)}개")


class _DraggableList(QListWidget):
    """드래그 시 text/plain MIME도 함께 제공해 QTextEdit에 드롭 가능한 리스트"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setDefaultDropAction(Qt.CopyAction)

    def mimeData(self, items):
        data = super().mimeData(items)
        data.setText("\n".join(item.text() for item in items))
        return data


class FileAttachPanel(QWidget):
    """파일 목록 패널 (SRP: 경로 선택 및 파일 목록 표시만 담당)"""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(253)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        self._save_path = ""
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._file_header = QLabel("파일 목록  (0개)")
        self._file_header.setFixedHeight(28)
        self._file_header.setContentsMargins(12, 0, 0, 0)
        self._file_header.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(self._file_header)
        lay.addWidget(h_separator())

        path_btn = QPushButton("📁 파일 저장경로")
        path_btn.setFixedHeight(34)
        path_btn.setStyleSheet(f"""
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
        path_btn.clicked.connect(self._browse_save_path)
        lay.addWidget(path_btn)

        self._stack = QStackedWidget()

        placeholder = QLabel("파일 저장경로를\n선택해주세요")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #aaa; font-size: 12px;")
        self._stack.addWidget(placeholder)  # index 0

        self._file_list = _DraggableList()
        self._file_list.setStyleSheet(f"""
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
        self._stack.addWidget(self._file_list)  # index 1

        lay.addWidget(self._stack)

    def _browse_save_path(self):
        """파일 탐색기로 저장경로 선택 후 파일 목록 갱신"""
        path = QFileDialog.getExistingDirectory(self, "파일 저장경로 선택", self._save_path or "")
        if path:
            self._save_path = path
            self._load_all_files(path)

    def _load_all_files(self, path: str):
        """선택된 경로의 모든 파일을 목록에 표시"""
        try:
            files = sorted(
                f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
            )
        except OSError:
            files = []
        self._file_list.clear()
        for f in files:
            self._file_list.addItem(f)
        self._file_header.setText(f"파일 목록  ({len(files)}개)")
        self._stack.setCurrentIndex(1 if files else 0)


class MessageWritePanel(QWidget):
    """텍스트 메시지 작성 패널 (SRP: 메시지 입력 UI 및 사용자 액션 시그널만 담당)"""

    save_new_group_requested = pyqtSignal(str)
    save_group_requested = pyqtSignal(str)
    immediate_send_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(253)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        msg_hdr = QLabel("텍스트 메시지 작성")
        msg_hdr.setFixedHeight(28)
        msg_hdr.setContentsMargins(12, 0, 0, 0)
        msg_hdr.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(msg_hdr)
        lay.addWidget(h_separator())

        self._msg_edit = QTextEdit()
        self._msg_edit.setPlaceholderText("메시지를 입력하세요...")
        self._msg_edit.setStyleSheet(f"""
            QTextEdit {{
                background: {C['white']};
                color: {C['text']};
                border: 1px solid {C['border']};
                font-size: 12px;
                margin: 6px 10px;
            }}
        """)
        lay.addWidget(self._msg_edit)

        for label in ("메시지 변수", "메시지 추가"):
            btn = make_btn(label, height=34, font_size=11)
            btn.setStyleSheet(btn.styleSheet() + "margin: 2px 10px;")
            lay.addWidget(btn)

        lay.addWidget(h_separator())

        save_row = QWidget()
        save_row.setStyleSheet(f"background: {C['white']};")
        sr = QHBoxLayout(save_row)
        sr.setContentsMargins(10, 6, 10, 6)
        sr.setSpacing(4)

        spaceLabel = QLabel()
        spaceLabel.setStyleSheet(f"background-color: {C['white']};")
        spaceLabel.setFixedHeight(20)
        lay.addWidget(spaceLabel)

class MessageListPanel(QWidget):
    """텍스트 메시지 목록 패널 (SRP: 목록 표시만 담당)"""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(276)
        self.setStyleSheet(f"background: {C['white']}; border-right: 1px solid {C['border']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._header_lbl = QLabel()
        self._header_lbl.setFixedHeight(28)
        self._header_lbl.setContentsMargins(12, 0, 0, 0)
        self._header_lbl.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
        lay.addWidget(self._header_lbl)
        lay.addWidget(h_separator())

        self._list_w = QListWidget()
        self._list_w.setStyleSheet(f"""
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
        lay.addWidget(self._list_w)

    def set_messages(self, messages: list):
        """컨트롤러가 모델 변경 시 호출 — 메시지 목록 갱신"""
        self._list_w.clear()
        for m in messages:
            self._list_w.addItem(m)
        self._header_lbl.setText(f"텍스트 메시지 목록  ({len(messages)}개)")


class MessagePreviewPanel(QWidget):
    """메시지 미리보기 패널 (SRP: 미리보기 표시 및 저장 시그널만 담당)"""

    save_requested = pyqtSignal()

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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: 1px solid {C['border']}; margin: 6px 10px; background: {C['white']}; }}"
        )
        self._preview_container = QWidget()
        self._preview_container.setStyleSheet(f"background: {C['white']};")
        self._preview_layout = QVBoxLayout(self._preview_container)
        self._preview_layout.setContentsMargins(12, 12, 12, 12)
        self._preview_layout.setSpacing(8)
        self._preview_layout.addStretch()
        scroll.setWidget(self._preview_container)

        # 스크롤 뷰포트에 드롭 이벤트 수신
        scroll.viewport().setAcceptDrops(True)
        scroll.viewport().installEventFilter(self)

        lay.addWidget(scroll)
        lay.addWidget(h_separator())

        save_btn = make_btn(
            "저장", bg=C["green"], fg="white", border=C["green"],
            radius=4, font_size=13, bold=True, height=42,
        )
        save_btn.clicked.connect(lambda: self.save_requested.emit())
        lay.addWidget(save_btn)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.DragEnter:
            if event.mimeData().hasText():
                event.acceptProposedAction()
                return True
        elif event.type() == QEvent.Drop:
            for line in event.mimeData().text().splitlines():
                line = line.strip()
                if line:
                    self._add_bubble(line)
            event.acceptProposedAction()
            return True
        return super().eventFilter(obj, event)

    def _add_bubble(self, text: str):
        """버블 항목을 stretch 직전에 삽입"""
        idx = self._preview_layout.count() - 1
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        bubble.setStyleSheet(f"""
            background: {C['yellow']};
            border-radius: 14px;
            padding: 10px 14px;
            font-size: 12px;
            color: #000;
        """)
        self._preview_layout.insertWidget(idx, bubble)

    def set_preview(self, items: list):
        """컨트롤러가 호출 — stretch 앞의 버블 위젯을 교체"""
        while self._preview_layout.count() > 1:
            item = self._preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, msg in enumerate(items):
            bubble = QLabel(msg)
            bubble.setWordWrap(True)
            bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            bubble.setStyleSheet(f"""
                background: {C['yellow']};
                border-radius: 14px;
                padding: 10px 14px;
                font-size: 12px;
                color: #000;
            """)
            self._preview_layout.insertWidget(i, bubble)


class GroupCreationTab(QWidget):
    """그룹생성 탭 — 하위 패널을 조합하는 컨테이너 뷰"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {C['bg']};")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.group_panel = GroupListPanel()
        self.room_panel = ChatRoomPanel()
        self.file_panel = FileAttachPanel()
        self.msg_write_panel = MessageWritePanel()
        self.msg_list_panel = MessageListPanel()
        self.preview_panel = MessagePreviewPanel()

        for w in (
            self.group_panel, self.room_panel, self.file_panel,
            self.msg_write_panel, self.msg_list_panel, self.preview_panel,
        ):
            lay.addWidget(w)
