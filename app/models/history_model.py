from dataclasses import dataclass
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class HistoryEntry:
    """전송이력 한 건의 불변 데이터 객체"""
    timestamp: datetime
    group: str
    room: str
    message: str
    result: str
    medium: str


class HistoryModel(QObject):
    """전송이력 데이터를 관리하는 모델 (SRP: 데이터 상태만 책임)"""

    history_changed = pyqtSignal(list)  # list[HistoryEntry]

    def __init__(self):
        super().__init__()
        self._entries: list = []

    @property
    def entries(self) -> list:
        return list(self._entries)

    def add_entry(self, entry: HistoryEntry):
        self._entries.append(entry)
        self.history_changed.emit(self.entries)

    def clear(self):
        self._entries.clear()
        self.history_changed.emit(self.entries)
