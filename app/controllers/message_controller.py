from app.models.message_model import MessageModel
from app.views.tabs.message_send_tab import MessageSendTab


class MessageController:
    """메시지 전송 탭의 비즈니스 로직을 담당하는 컨트롤러

    DIP 적용: AdvancedSettingsPanel이 ChatDialogPanel을 직접 참조하던 구조를
    컨트롤러가 두 뷰를 중재하는 구조로 전환 — 뷰 간 결합도 제거.
    """

    def __init__(self, message_model: MessageModel, tab: MessageSendTab):
        self._model = message_model
        self._tab = tab
        self._wire_signals()

    def _wire_signals(self):
        adv = self._tab.adv_panel
        adv.send_requested.connect(self._on_send)
        adv.reset_requested.connect(self._on_reset)

    def _on_send(self, count: int):
        self._tab.dialog_panel.append_log(f"전송 시작 (횟수: {count})")

    def _on_reset(self):
        self._tab.adv_panel.reset()
        self._tab.dialog_panel.append_log("초기화 완료")
