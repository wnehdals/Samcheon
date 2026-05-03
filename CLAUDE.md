# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**이지카톡 PRO** (`v1.11.0`) — 카카오톡 메시지 자동 전송 데스크탑 앱.  
엑셀 파일에서 채팅방 목록을 읽어 친구별로 텍스트·파일 메시지를 순차 전송한다.

## Language Preference

모든 응답과 코드 주석은 한국어로 작성한다. 예외 메시지 등 기술적 문자열은 원문 유지.

### 에이전트 라우팅

코드 작성 시 pyqt-expert-agent, python-expert-agent를 선택한다.

## Running

```bash
python main.py
```

가상환경 사용 (`.venv/`). 패키지 설치:

```bash
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install Pillow opencv-python  # 이미지 인식 의존성 (requirements.txt 미포함)
```

## Environment

- **Python** 3.12.6 (`.venv/` 가상환경)
- **OS** Windows 11 (pywin32 의존, Windows 전용)
- **GUI** PyQt5 (Fusion 스타일)
- **자동화** pyautogui + pyperclip + pywin32 + pygetwindow
- **이미지 인식** OpenCV + Pillow + pyscreeze (`pyautogui.locateOnScreen` 사용)
- **데이터** openpyxl (엑셀 A열 → 채팅방 목록 읽기)

## Architecture

MVC 패턴. SOLID 원칙 적용.

```
View (pyqtSignal 발행)
  ↓
Controller (신호 처리 → 모델 변경 / 뷰 갱신)
  ↓↑
Model (pyqtSignal로 변경 통보)
```

**의존성 조립**: `AppController.__init__`에서 모든 모델·뷰·하위 컨트롤러를 생성하고 주입한다. 하위 컨트롤러는 생성자 주입으로 모델·뷰를 받는다 (DIP).

## Project Structure

```
main.py                          # 진입점 — QApplication 생성, AppController 시작
app/
  constants.py                   # 색상 팔레트(C), APP_VERSION, EXPIRE_DATE, SEARCH_ICON_SLEEP
  models/
    group_model.py               # GroupModel — 그룹명 딕셔너리 관리
    message_model.py             # MessageModel — 메시지·파일 목록 관리
    message_ticket.py            # MessageTicket — 텍스트/파일 메시지 데이터 객체
    message_template.py          # MessageTemplate (싱글톤) — 전송 대상·메시지·대기시간 전역 상태
    history_model.py             # HistoryModel — 전송이력 (HistoryEntry dataclass)
  controllers/
    app_controller.py            # AppController — 의존성 조립 루트
    group_controller.py          # GroupController — 그룹생성 탭 비즈니스 로직
    message_controller.py        # MessageController + SendWorker(QThread) — 전송 자동화
  views/
    main_window.py               # MainWindow — 타이틀 바·탭 바·QStackedWidget 조립
    title_bar.py                 # TitleBar — 프레임리스 드래그·윈도우 제어·만료시간 표시
    tab_bar.py                   # TabBar — 탭 네비게이션
    widgets.py                   # h_separator(), make_btn(), panel_header_widget() 팩토리
    settings_window.py           # SettingsWindow — 설정 다이얼로그
    tabs/
      group_creation_tab.py      # GroupCreationTab + 6개 하위 패널
      message_send_tab.py        # MessageSendTab + KakaoFriendPanel, ChatDialogPanel, AdvancedSettingsPanel
      history_tab.py             # HistoryTab — 전송이력 테이블
images/                          # 아이콘 이미지 (pyautogui 이미지 인식용)
  search_icon.png                # 카카오톡 친구 검색 버튼
  search_close.png               # 검색 닫기 버튼
  attach_icon.png                # 파일 첨부 버튼
  friend.png / x_icon.png
```

## Key Classes

### MessageTemplate (싱글톤)
`MessageTemplate.instance()`로 접근. `friends` (전송 대상 채팅방 이름 목록), `messageTickets`, `send_term` / `send_text_term` / `send_file_term` 보유. `clear()` 후 재사용.  
`GroupCreationTab._on_save_clicked`에서 싱글톤에 친구·티켓을 채운 뒤 `save_completed` 신호를 발행한다.

### SendWorker (QThread)
`MessageController`가 전송 버튼 클릭 시 생성. `start_idx`부터 `friends` 리스트를 순회하며 카카오톡을 pyautogui/pywin32로 제어한다.  
`_stop` 플래그로 중단, `_current_idx`로 현재 위치 추적 → 일시 중지 후 재개 지원.  
로그는 `log_emitted(str)` 시그널로 메인 스레드에 전달 (스레드 안전).

### AdvancedSettingsPanel
`send_requested(int)` / `pause_requested()` / `reset_requested()` 신호 보유.  
`reset_send_btn()` — 전송 완료 시 컨트롤러가 호출해 버튼을 "▶ 전송" 상태로 복원.

## Design Conventions

- **뷰 간 직접 참조 금지** — 뷰는 신호만 발행, 컨트롤러가 다른 뷰를 갱신한다.
- **GUI 호출은 메인 스레드에서만** — `SendWorker`에서 UI 직접 접근 대신 `pyqtSignal` 사용.
- **open_kakao()** — 카카오톡 창을 못 찾으면 `append_log` 대신 `Exception` raise (워커 스레드에서 호출되므로).
- **resource_path()** — PyInstaller 빌드와 개발 환경 양쪽에서 이미지 경로 처리.
- **색상** — `app/constants.py`의 `C` 딕셔너리만 사용. 하드코딩 금지.
- **새 위젯** — `make_btn()`, `h_separator()`, `panel_header_widget()` 팩토리 우선 사용.
- **메시지 변수** — `#{친구이름}` 치환은 `SendWorker.run()` 내 `message.text.replace('#{친구이름}', name)`으로 처리.
