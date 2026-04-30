from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PyQt5.QtCore import pyqtSignal
from app.constants import C
from app.views.widgets import make_btn


class HistoryTab(QWidget):
    """전송이력 탭 (SRP: 이력 테이블 표시 및 새로고침 시그널만 담당)"""

    refresh_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {C['white']};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

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
        refresh_btn.clicked.connect(lambda: self.refresh_requested.emit())
        tb.addWidget(refresh_btn)
        lay.addWidget(toolbar)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(["전송일시", "그룹명", "채팅방", "메시지", "결과", "매개체"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet(f"""
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
        lay.addWidget(self._table)

    def set_history(self, entries: list):
        """컨트롤러가 모델 변경 시 호출 — 테이블 전체 갱신"""
        self._table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            self._table.setItem(row, 0, QTableWidgetItem(entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
            self._table.setItem(row, 1, QTableWidgetItem(entry.group))
            self._table.setItem(row, 2, QTableWidgetItem(entry.room))
            self._table.setItem(row, 3, QTableWidgetItem(entry.message))
            self._table.setItem(row, 4, QTableWidgetItem(entry.result))
            self._table.setItem(row, 5, QTableWidgetItem(entry.medium))
