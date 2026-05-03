import os
import sys
import time
from re import template
from time import sleep

import pyautogui
import pyperclip
from PyQt5.QtCore import QThread, pyqtSignal
import win32api
import win32con
import win32gui
import pygetwindow as gw

from app.constants import SEARCH_ICON_SLEEP
from app.models.message_model import MessageModel
from app.models.message_template import MessageTemplate
from app.models.message_ticket import MessageTicket
from app.views.tabs.message_send_tab import MessageSendTab


def _send_return(hwnd):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)


class SendWorker(QThread):
    """전송 루프를 별도 스레드에서 실행 — UI 블로킹 방지"""

    log_emitted = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, controller, start_idx: int = 0):
        super().__init__()
        self._ctrl = controller
        self._start_idx = start_idx
        self._current_idx = start_idx
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        ctrl = self._ctrl
        tmpl = MessageTemplate.instance()
        friends = tmpl.friends
        messages = tmpl.messageTickets
        TEXT_TERM = tmpl.send_text_term
        FILE_TERM = tmpl.send_file_term
        FRIEND_TERM = tmpl.send_term

        try:
            kakao_window = ctrl.open_kakao()
            kakao_window.activate()

            for idx in range(self._start_idx, len(friends)):
                if self._stop:
                    self._current_idx = idx
                    return

                self._current_idx = idx
                name = friends[idx]

                ctrl.click_search_friend()
                time.sleep(1)
                ctrl.openRoom(name)

                for message in messages:
                    if message.isTextMessage:
                        replaced = message.text.replace('#{친구이름}', name)
                        pyperclip.copy(replaced)
                        pyautogui.hotkey("ctrl", "v")
                        time.sleep(1)
                        pyautogui.keyDown("enter")
                        time.sleep(TEXT_TERM)
                    else:
                        pyperclip.copy(f"background: {message.file_path}/{message}")
                        ctrl._on_click_file_attach()
                        time.sleep(2)
                        pyautogui.hotkey("ctrl", "v")
                        time.sleep(1)
                        pyautogui.keyDown("enter")
                        time.sleep(FILE_TERM)

                pyautogui.keyDown("esc")
                self.log_emitted.emit(f"{name} 전송 완료\t\t{idx + 1}/{len(friends)}")
                ctrl.click_search_close()
                time.sleep(FRIEND_TERM)

        except Exception as e:
            self.log_emitted.emit(str(e))

        self.finished.emit()


class MessageController:
    """메시지 전송 탭의 비즈니스 로직을 담당하는 컨트롤러

    DIP 적용: AdvancedSettingsPanel이 ChatDialogPanel을 직접 참조하던 구조를
    컨트롤러가 두 뷰를 중재하는 구조로 전환 — 뷰 간 결합도 제거.
    """

    def __init__(self, message_model: MessageModel, tab: MessageSendTab):
        self._model = message_model
        self._tab = tab
        self._worker: SendWorker | None = None
        self._resume_idx = 0
        self._wire_signals()

    def resource_path(self, relative_path:str):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def _wire_signals(self):
        adv = self._tab.adv_panel
        adv.send_requested.connect(self._on_send)
        adv.pause_requested.connect(self._on_pause)
        adv.reset_requested.connect(self._on_reset)

    def _on_click_icon(self, iconName, error):
        button_location = pyautogui.locateOnScreen(self.resource_path(iconName), confidence=0.9)
        print(type(button_location))
        if button_location is None:
            raise Exception(error)
        else:
            button_point = pyautogui.center(button_location)
            time.sleep(1)
            pyautogui.click(button_point.x, button_point.y)

    def _on_click_file_attach(self):
        self._on_click_icon("images/attach_icon.png", "ERROR 201 : 파일 첨부 버튼을 찾을 수 없습니다.")

    def _on_send(self, count: int):
        friends = MessageTemplate.instance().friends
        if not friends:
            self._tab.adv_panel.append_log("전송할 대상이 없습니다.")
            self._tab.adv_panel.reset_send_btn()
            return

        start = self._resume_idx
        label = f"전송 재개 — {start + 1}번째부터" if start > 0 else f"전송 시작 — 대상 {len(friends)}명"
        self._tab.adv_panel.append_log(label)

        self._worker = SendWorker(self, start)
        self._worker.log_emitted.connect(self._tab.adv_panel.append_log)
        self._worker.finished.connect(self._on_send_finished)
        self._worker.start()

    def _on_pause(self):
        if self._worker and self._worker.isRunning():
            self._resume_idx = self._worker._current_idx
            self._worker.stop()
            self._tab.adv_panel.append_log(f"일시 중지 — {self._resume_idx + 1}번째에서 중단")

    def _on_send_finished(self):
        self._resume_idx = 0
        self._tab.adv_panel.reset_send_btn()
        self._tab.adv_panel.append_log("전송 완료")


    def _on_reset(self):
        self._tab.adv_panel.reset()
        self._tab.dialog_panel.append_log("초기화 완료")



    def move_kakaotalk_window(self, window_title_keyword, targetWindow):
        hwnd = win32gui.FindWindow(None, window_title_keyword)
        if hwnd:
            x = targetWindow.right   # targetWindow 오른쪽 바로 옆
            y = targetWindow.top     # targetWindow와 동일한 y축
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, 500, 600, win32con.SWP_SHOWWINDOW)
            print(f"[{window_title_keyword}] 창 위치 이동 완료: ({x}, {y})")
        else:
            print(f"[{window_title_keyword}] 창을 찾을 수 없습니다.")

    def open_kakao(self):
        try:
            return gw.getWindowsWithTitle("카카오톡")[0]
        except IndexError:
            raise Exception("ERROR 101 : 카카오톡이 열려있지 않습니다.")

    def click_search_friend(self):
        time.sleep(SEARCH_ICON_SLEEP)
        self._on_click_icon('images/search_icon.png', "ERROR 101 : 검색 버튼을 찾을 수 없습니다.")

    def click_search_close(self):
        time.sleep(SEARCH_ICON_SLEEP)
        self._on_click_icon('images/search_close.png', "ERROR 101 : 검색 버튼을 찾을 수 없습니다.")


    def openRoom(self, name: str):
        pyperclip.copy(name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)
        pyautogui.keyDown("enter")
        time.sleep(1)
        room_window = gw.getWindowsWithTitle(name)[0]

        if room_window is None:
            raise Exception("ERROR 102 : 검색 버튼을 찾을 수 없습니다.")
        else:
            self.move_kakaotalk_window(name, self.open_kakao())


