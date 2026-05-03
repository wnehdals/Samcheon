from PyQt5.QtCore import QObject, pyqtSignal
from app.models.message_ticket import MessageTicket


class MessageModel(QObject):
    """메시지 및 첨부파일 데이터를 관리하는 모델 (SRP: 데이터 상태만 책임)"""

    messages_changed = pyqtSignal(list)  # list[str]
    files_changed = pyqtSignal(list)     # list[str]

    def __init__(self):
        super().__init__()
        self._messages: list = []
        self._files: list = []
        self._save_path: str = ""

    @property
    def messages(self) -> list:
        return list(self._messages)

    @property
    def files(self) -> list:
        return list(self._files)

    @property
    def save_path(self) -> str:
        return self._save_path

    def add_message(self, text: str):
        if text:
            self._messages.append(MessageTicket(text=text))
            self.messages_changed.emit(self.messages)

    def add_file(self, path: str):
        if path:
            self._files.append(path)
            self.files_changed.emit(self.files)

    def set_save_path(self, path: str):
        self._save_path = path
