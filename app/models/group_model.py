from PyQt5.QtCore import QObject, pyqtSignal


class GroupModel(QObject):
    """그룹 및 채팅방 데이터를 관리하는 모델 (SRP: 데이터 상태만 책임)"""

    groups_changed = pyqtSignal(list)  # list[str] 그룹 이름 목록

    def __init__(self):
        super().__init__()
        self._data: dict = {}

    @property
    def group_names(self) -> list:
        return list(self._data.keys())

    def rooms_for(self, group: str) -> list:
        return list(self._data.get(group, []))

    def add_group(self, name: str):
        if name and name not in self._data:
            self._data[name] = []
            self.groups_changed.emit(self.group_names)

    def remove_group(self, name: str):
        if name in self._data:
            del self._data[name]
            self.groups_changed.emit(self.group_names)
