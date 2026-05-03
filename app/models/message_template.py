from app.models.message_ticket import MessageTicket


class MessageTemplate:

    _instance: 'MessageTemplate | None' = None

    @classmethod
    def instance(cls) -> 'MessageTemplate':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._friends: list[str] = []
        self._messageTickets: list[MessageTicket] = []
        self._send_term: int = 1
        self._send_text_term: int = 1
        self._send_file_term: int = 3

    @property
    def friends(self) -> list:
        return list(self._friends)

    @property
    def messageTickets(self) -> list:
        return list(self._messageTickets)

    @property
    def send_term(self) -> int:
        return self._send_term

    @property
    def send_text_term(self) -> int:
        return self._send_text_term

    @property
    def send_file_term(self) -> int:
        return self._send_file_term

    def set_send_term(self, value: int):
        self._send_term = value

    def set_send_text_term(self, value: int):
        self._send_text_term = value

    def set_send_file_term(self, value: int):
        self._send_file_term = value

    def add_friend(self, name: str):
        self._friends.append(name)

    def add_ticket(self, ticket: MessageTicket):
        self._messageTickets.append(ticket)

    def clear(self):
        self._friends.clear()
        self._messageTickets.clear()
