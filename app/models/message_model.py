from PyQt5.QtCore import QObject, pyqtSignal


class MessageModel(QObject):
    """메시지 및 첨부파일 데이터를 관리하는 모델 (SRP: 데이터 상태만 책임)"""

    messages_changed = pyqtSignal(list)  # list[str]
    files_changed = pyqtSignal(list)     # list[str]

    def __init__(self):
        super().__init__()
        self._messages: list = ["좋은 하루 보내세요", "오늘 와주셔서 감사합니다."]
        self._files: list = ["이미지 첨부 파일.png", "동영상 첨부 파일.mp4"]
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
            self._messages.append(text)
            self.messages_changed.emit(self.messages)

    def add_file(self, path: str):
        if path:
            self._files.append(path)
            self.files_changed.emit(self.files)

    def set_save_path(self, path: str):
        self._save_path = path
