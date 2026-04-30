from app.models.group_model import GroupModel
from app.models.message_model import MessageModel
from app.models.history_model import HistoryModel
from app.views.main_window import MainWindow
from app.controllers.group_controller import GroupController
from app.controllers.message_controller import MessageController


class AppController:
    """애플리케이션 최상위 컨트롤러

    모든 모델·뷰·하위 컨트롤러를 생성하고 의존성을 조립하는 단일 진입점.
    DIP 적용: 하위 컨트롤러는 생성자 주입으로 모델·뷰를 수신.
    """

    def __init__(self):
        # 모델 생성 (순수 데이터·상태 계층)
        self._group_model = GroupModel()
        self._message_model = MessageModel()
        self._history_model = HistoryModel()

        # 뷰 생성 (UI 계층)
        self.main_window = MainWindow()

        # 컨트롤러 생성 및 모델·뷰 연결
        self._group_ctrl = GroupController(
            self._group_model,
            self._message_model,
            self.main_window.group_creation_tab,
        )
        self._message_ctrl = MessageController(
            self._message_model,
            self.main_window.message_send_tab,
        )

        # 전송이력: 모델 변경 → 뷰 직접 연결 (중간 로직 불필요)
        self._history_model.history_changed.connect(
            self.main_window.history_tab.set_history
        )
