
class MessageTicket:

    def __init__(self, text: str = "", file_path: str = ""):
        self._text: str = text
        self._file_path: str = file_path

    @property
    def text(self) -> str:
        return self._text

    @property
    def file_path(self) -> str:
        return self._file_path

    def isTextMessage(self) -> bool:
        return len(self._file_path) == 0
