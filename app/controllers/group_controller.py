import os

import openpyxl
from app.models.group_model import GroupModel
from app.models.message_model import MessageModel
from app.views.tabs.group_creation_tab import GroupCreationTab


class GroupController:
    """그룹생성 탭의 비즈니스 로직을 담당하는 컨트롤러

    DIP 적용: 모델·뷰를 추상 인터페이스(생성자 주입)로 수신 — 직접 생성 없음.
    SRP 적용: 뷰 시그널 → 모델 변경 / 모델 변경 → 뷰 갱신 흐름만 책임.
    """

    def __init__(
        self,
        group_model: GroupModel,
        message_model: MessageModel,
        tab: GroupCreationTab,
    ):
        self._group_model = group_model
        self._message_model = message_model
        self._tab = tab
        self._save_path = ""
        self._wire_signals()
        self._load_initial_data()

    def _wire_signals(self):
        gp = self._tab.group_panel
        fp = self._tab.file_panel
        wp = self._tab.msg_write_panel
        mp = self._tab.msg_list_panel

        # 뷰 액션 → 컨트롤러 핸들러 → 모델 변경
        gp.save_path_changed.connect(self._on_save_path_changed)
        gp.group_selected.connect(self._on_group_selected)
        wp.immediate_send_requested.connect(self._on_immediate_send)

        # 모델 변경 → 뷰 갱신
        self._group_model.groups_changed.connect(gp.set_groups)
        self._message_model.messages_changed.connect(mp.set_messages)

    def _load_initial_data(self):
        """초기 모델 데이터를 뷰에 반영"""
        gp = self._tab.group_panel
        mp = self._tab.msg_list_panel

        gp.set_groups(self._group_model.group_names)
        mp.set_messages(self._message_model.messages)

        names = self._group_model.group_names
        if names:
            self._on_group_selected(names[0])

        self._refresh_preview()

    def _on_group_selected(self, filename: str):
        """선택된 엑셀 파일의 A열 값을 읽어 ChatRoomPanel에 표시"""
        self._tab.room_panel.set_group_name(filename)
        if not filename or not self._save_path:
            self._tab.room_panel.set_rooms([])
            return
        filepath = os.path.join(self._save_path, filename)
        self._tab.room_panel.set_rooms(self._read_column_a(filepath))

    def _read_column_a(self, filepath: str) -> list:
        """엑셀 파일에서 A열의 비어있지 않은 값을 문자열 목록으로 반환"""
        try:
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            ws = wb.active
            values = [
                str(row[0].value)
                for row in ws.iter_rows()
                if row[0].value is not None
            ]
            wb.close()
            return values
        except Exception:
            return []

    def _on_save_path_changed(self, path: str):
        self._save_path = path

    def _on_immediate_send(self, message: str):
        # 실제 전송 로직 구현 위치
        pass

    def _refresh_preview(self):
        """메시지와 파일을 교차 배치한 미리보기 항목 생성"""
        msgs = self._message_model.messages
        files = self._message_model.files
        items = []
        for i, msg in enumerate(msgs):
            items.append(msg)
            if i < len(files):
                items.append("[이미지 첨부]")
        self._tab.preview_panel.set_preview(items)
