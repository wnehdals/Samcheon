import json
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QTextEdit, QScrollArea, QSizePolicy,
    QAbstractItemView, QFileDialog, QStackedWidget, QMenu, QMessageBox,
)
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from app.constants import C
from app.models.message_ticket import MessageTicket
from app.models.message_template import MessageTemplate
from app.views.widgets import h_separator, make_btn

_EXCEL_EXTENSIONS = {'.xlsx', '.xls', '.xlsm', '.xlsb', '.xltx', '.xltm'}
_MIME_TICKET = "application/x-samcheon-ticket"


class GroupListPanel(QWidget):
    """그룹 리스트 패널 (SRP: 저장경로 선택 및 그룹 파일 목록 표시만 담당)"""

    save_path_changed = pyqtSignal(str)  # 선택된 저장경로
    group_selected = pyqtSignal(str)  # 선택된 그룹 파일명

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(220)
        self.setStyleSheet(f"background: {C['white']};")
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

        path_btn = QPushButton("📁 연락처 저장경로")
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

        placeholder = QLabel("연락처 excel 파일 \n경로를 선택해주세요")
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
        self.setMinimumWidth(220)
        self.setStyleSheet(f"background: {C['white']};")
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

    def get_rooms(self) -> list:
        return [self._list_w.item(i).text() for i in range(self._list_w.count())]

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
        ticket_dicts = []
        for item in items:
            ticket = item.data(Qt.UserRole)
            if isinstance(ticket, MessageTicket):
                ticket_dicts.append({"text": ticket.text, "file_path": ticket.file_path})
        data.setText("\n".join(d["text"] for d in ticket_dicts))
        data.setData(_MIME_TICKET, json.dumps(ticket_dicts).encode())
        return data


class FileAttachPanel(QWidget):
    """파일 목록 패널 (SRP: 경로 선택 및 파일 목록 표시만 담당)"""

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(220)
        self.setStyleSheet(f"background: {C['white']};")
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
            full_path = os.path.join(path, f)
            item = QListWidgetItem(f)
            item.setData(Qt.UserRole, MessageTicket(text=f, file_path=full_path))
            self._file_list.addItem(item)
        self._file_header.setText(f"파일 목록  ({len(files)}개)")
        self._stack.setCurrentIndex(1 if files else 0)


class MessageWritePanel(QWidget):
    """텍스트 메시지 작성 패널 (SRP: 메시지 입력 UI 및 사용자 액션 시그널만 담당)"""

    save_new_group_requested = pyqtSignal(str)
    save_group_requested = pyqtSignal(str)
    immediate_send_requested = pyqtSignal(str)
    message_add_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(220)
        self.setStyleSheet(f"background: {C['white']};")
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
        self._msg_edit.setAcceptDrops(False)
        self._msg_edit.setStyleSheet(f"""
            QTextEdit {{
                background: {C['white']};
                color: {C['text']};
                border: 1px solid {C['border']};
                font-size: 12px;
                margin: 0px 0px;
            }}
        """)
        lay.addWidget(self._msg_edit)

        var_btn = make_btn("메시지 변수", height=34, font_size=11)
        var_btn.setStyleSheet(
            f"""
                QPushButton {{
                    background: {C['white']};
                    color: {C['text']};
                    border: 1px solid {C['green']};
                    border-radius: 4px;
                    font-size: 12px;
                    margin: 2px 0px;
                }}
                QPushButton:hover {{ background: #fff9e0; }}
               """
        )
        var_btn.clicked.connect(lambda: self._show_var_menu(var_btn))
        lay.addWidget(var_btn)

        add_btn = make_btn("메시지 추가", height=34, font_size=11)
        add_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {C['white']};
                color: {C['text']};
                border: 1px solid {C['yellow']};
                border-radius: 4px;
                font-size: 12px;
                margin: 2px 0px;
            }}
            QPushButton:hover {{ background: #fff9e0; }}
        """)
        add_btn.clicked.connect(self._on_add_message)
        lay.addWidget(add_btn)

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

    def _show_var_menu(self, btn: QPushButton):
        _VARIABLES = ["친구이름"]
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {C['white']};
                border: 1px solid {C['border']};
                padding: 4px 0px;
                font-size: 12px;
                color: {C['text']};
            }}
            QMenu::item {{
                padding: 6px 20px;
            }}
            QMenu::item:selected {{
                background: #fff9e0;
                color: {C['text']};
            }}
        """)
        for var in _VARIABLES:
            menu.addAction(var, lambda v=var: self._insert_variable(v))
        menu.exec_(btn.mapToGlobal(btn.rect().bottomLeft()))

    def _insert_variable(self, var: str):
        self._msg_edit.insertPlainText(f"#{{{var}}}")

    def _on_add_message(self):
        text = self._msg_edit.toPlainText().strip()
        if text:
            self.message_add_requested.emit(text)
            self._msg_edit.clear()


class MessageListPanel(QWidget):
    """텍스트 메시지 목록 패널 (SRP: 목록 표시만 담당)"""

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(220)
        self.setStyleSheet(f"background: {C['white']};")
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

        self._list_w = _DraggableList()
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

    def set_messages(self, tickets: list):
        """컨트롤러가 모델 변경 시 호출 — 메시지 목록 갱신 (list[MessageTicket])"""
        self._list_w.clear()
        for ticket in tickets:
            item = QListWidgetItem(ticket.text)
            item.setData(Qt.UserRole, ticket)
            self._list_w.addItem(item)
        self._header_lbl.setText(f"텍스트 메시지 목록  ({len(tickets)}개)")

    def add_message(self, text: str):
        """메시지 한 건을 목록 끝에 추가"""
        ticket = MessageTicket(text=text)
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, ticket)
        self._list_w.addItem(item)
        count = self._list_w.count()
        self._header_lbl.setText(f"텍스트 메시지 목록  ({count}개)")


class MessagePreviewPanel(QWidget):
    """메시지 미리보기 패널 (SRP: 미리보기 표시 및 저장 시그널만 담당)"""

    save_requested = pyqtSignal()
    preview_count_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(220)
        self.setStyleSheet(f"background: {C['white']};")
        self._bubble_count = 0
        self._tickets: list = []
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
            f"QScrollArea {{ border: 1px solid {C['border']}; margin: 2px 1px; background: {C['white']}; }}"
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

        self._save_btn = make_btn(
            "저장", bg=C["light"], fg="white", border=C["light"],
            radius=4, font_size=13, bold=True, height=42,
        )
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(lambda: self.save_requested.emit())
        lay.addWidget(self._save_btn)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.DragEnter:
            if event.mimeData().hasFormat(_MIME_TICKET):
                event.acceptProposedAction()
                return True
        elif event.type() == QEvent.Drop:
            raw = bytes(event.mimeData().data(_MIME_TICKET)).decode()
            for d in json.loads(raw):
                self._add_bubble(MessageTicket(text=d["text"], file_path=d.get("file_path", "")))
            event.acceptProposedAction()
            return True
        return super().eventFilter(obj, event)

    def _make_bubble(self, ticket: MessageTicket) -> QLabel:
        bubble = QLabel(ticket.text)
        bubble.setWordWrap(True)
        bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        bubble.setStyleSheet(f"""
            background: {C['yellow']};
            border-radius: 14px;
            padding: 10px 14px;
            font-size: 12px;
            color: #000;
        """)
        bubble.setContextMenuPolicy(Qt.CustomContextMenu)
        bubble.customContextMenuRequested.connect(
            lambda pos, b=bubble: self._on_bubble_context_menu(b, pos)
        )
        return bubble

    def _on_bubble_context_menu(self, bubble: QLabel, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {C['white']};
                border: 1px solid {C['border']};
                padding: 4px 0px;
                font-size: 12px;
                color: {C['text']};
            }}
            QMenu::item {{ padding: 6px 20px; }}
            QMenu::item:selected {{ background: #fff0f0; color: {C['red']}; }}
        """)
        menu.addAction("삭제", lambda: self._remove_bubble(bubble))
        menu.exec_(bubble.mapToGlobal(pos))

    def _remove_bubble(self, bubble: QLabel):
        for i in range(self._preview_layout.count() - 1):
            item = self._preview_layout.itemAt(i)
            if item and item.widget() is bubble:
                self._preview_layout.takeAt(i)
                bubble.deleteLater()
                if i < len(self._tickets):
                    self._tickets.pop(i)
                self._bubble_count -= 1
                self.preview_count_changed.emit(self._bubble_count)
                break

    def _add_bubble(self, ticket: MessageTicket):
        """버블 항목을 stretch 직전에 삽입"""
        idx = self._preview_layout.count() - 1
        bubble = self._make_bubble(ticket)
        self._preview_layout.insertWidget(idx, bubble)
        self._tickets.append(ticket)
        self._bubble_count += 1
        self.preview_count_changed.emit(self._bubble_count)

    @property
    def tickets(self) -> list:
        return list(self._tickets)

    def set_save_enabled(self, enabled: bool):
        self._save_btn.setEnabled(enabled)
        color = C["green"] if enabled else C["light"]
        self._save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border: 1px solid {color};
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }}
        """)

    def set_preview(self, tickets: list):
        """컨트롤러가 호출 — stretch 앞의 버블 위젯을 교체 (list[MessageTicket])"""
        while self._preview_layout.count() > 1:
            item = self._preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._tickets = []
        for i, ticket in enumerate(tickets):
            bubble = self._make_bubble(ticket)
            self._preview_layout.insertWidget(i, bubble)
            self._tickets.append(ticket)
        self._bubble_count = len(tickets)
        self.preview_count_changed.emit(self._bubble_count)


class GroupCreationTab(QWidget):
    """그룹생성 탭 — 하위 패널을 조합하는 컨테이너 뷰"""

    save_completed = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {C['bg']};")
        self._group_selected = False
        self._preview_count = 0

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

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
            lay.addWidget(w, 1)

        self.msg_write_panel.message_add_requested.connect(self.msg_list_panel.add_message)
        self.group_panel.group_selected.connect(self._on_group_selected)
        self.preview_panel.preview_count_changed.connect(self._on_preview_count_changed)
        self.preview_panel.save_requested.connect(self._on_save_clicked)

    def _on_group_selected(self, name: str):
        self._group_selected = bool(name)
        self._update_save_btn()

    def _on_preview_count_changed(self, count: int):
        self._preview_count = count
        self._update_save_btn()

    def _update_save_btn(self):
        self.preview_panel.set_save_enabled(self._group_selected and self._preview_count > 0)

    def _on_save_clicked(self):
        template = MessageTemplate.instance()
        template.clear()
        for name in self.room_panel.get_rooms():
            template.add_friend(name)
        for ticket in self.preview_panel.tickets:
            template.add_ticket(ticket)

        msg = QMessageBox(self)
        msg.setWindowTitle("저장")
        msg.setText("저장되었습니다")
        msg.addButton("확인", QMessageBox.AcceptRole)
        msg.exec_()
        self.save_completed.emit(template)
