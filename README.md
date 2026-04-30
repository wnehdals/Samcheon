# Samcheon

이지카톡 PRO — 카카오톡 메시지 자동전송 프로그램

## 설치 및 실행

```bash
pip install -r requirements.txt
python main.py
```

## 프로젝트 구조

```
Samcheon/
├── main.py                          # 진입점 (16줄)
└── app/
    ├── constants.py                 # 앱 상수 (색상, 버전, 체인지로그)
    ├── models/                      # Model 계층 — 데이터·상태 관리
    │   ├── group_model.py           # 그룹·채팅방 데이터
    │   ├── message_model.py         # 메시지·첨부파일 데이터
    │   └── history_model.py         # 전송이력 데이터
    ├── views/                       # View 계층 — UI 표시 및 시그널 발행
    │   ├── widgets.py               # 공통 위젯 팩토리
    │   ├── title_bar.py
    │   ├── tab_bar.py
    │   ├── tabs/
    │   │   ├── group_creation_tab.py
    │   │   ├── message_send_tab.py
    │   │   └── history_tab.py
    │   ├── settings_window.py
    │   └── main_window.py
    └── controllers/                 # Controller 계층 — 모델↔뷰 연결
        ├── group_controller.py
        ├── message_controller.py
        └── app_controller.py        # 최상위 의존성 조립
```

## 아키텍처: MVC 패턴

### Model
- UI에 대한 의존성 없이 순수 데이터와 상태만 보유
- 상태 변경 시 `pyqtSignal`을 발행하여 관심 있는 구독자에게 통보
- `QObject`를 상속하여 Qt 시그널/슬롯 시스템에 참여

### View
- 데이터를 직접 보유하지 않음 — 컨트롤러가 `set_*(data)` 메서드를 호출하여 갱신
- 사용자 액션은 시그널(`pyqtSignal`)로만 외부에 알림 — 모델·다른 뷰를 직접 참조하지 않음
- UI 입력 수집(예: `QInputDialog`)은 뷰의 책임이며, 수집한 값을 시그널에 담아 발행

### Controller
- 모델 시그널 → 뷰 갱신 메서드 연결
- 뷰 시그널 → 모델 변경 메서드 연결
- 뷰 간 상호작용(예: A패널 로그 → B패널 출력)을 중재
- `AppController`가 모든 모델·뷰·하위 컨트롤러를 생성하고 조립

## 적용된 SOLID 원칙

### S — 단일 책임 원칙 (SRP)

각 클래스는 한 가지 이유로만 변경된다.

| 클래스 | 책임 |
|---|---|
| `GroupModel` | 그룹·채팅방 데이터 상태 관리 |
| `GroupListPanel` | 그룹 목록 표시 + 사용자 입력 시그널 발행 |
| `GroupController` | 모델↔뷰 연결 및 그룹 관련 비즈니스 로직 |

**개선 전:** `GroupListPanel`이 `self.groups` 데이터를 직접 보유하고, 그룹 추가 로직까지 처리  
**개선 후:** 데이터는 `GroupModel`, 로직은 `GroupController`, 뷰는 표시와 시그널 발행만 담당

### O — 개방-폐쇄 원칙 (OCP)

기존 코드를 수정하지 않고 기능을 확장할 수 있다.

`SettingsWindow`의 설정 페이지 추가:

```python
# 기존 코드 수정 없이 리스트에 항목만 추가
_NAV_ITEMS = [
    ("🔄 업데이트", "_build_update_page"),
    ("🖥 등록 디바이스", None),
    ("📁 파일 저장경로", None),
    # ↓ 새 페이지 추가 — 다른 코드 변경 불필요
    ("🔔 알림 설정", "_build_notification_page"),
]
```

### L — 리스코프 치환 원칙 (LSP)

`QObject` 기반 모델들은 시그널 인터페이스가 동일하여 컨트롤러가 구체 타입에 의존하지 않고 교체 가능하다.

### I — 인터페이스 분리 원칙 (ISP)

뷰는 자신에게 필요한 메서드만 노출한다.

```python
# GroupListPanel — 그룹 목록 관련 메서드만 제공
def set_groups(self, groups: list): ...

# ChatRoomPanel — 채팅방 관련 메서드만 제공
def set_group_name(self, name: str): ...
def set_rooms(self, rooms: list): ...
```

컨트롤러는 전체 뷰 객체가 아닌 필요한 패널의 메서드만 호출한다.

### D — 의존성 역전 원칙 (DIP)

고수준 모듈이 저수준 구현에 직접 의존하지 않는다.

**개선 전 (DIP 위반):**
```python
# AdvancedSettingsPanel이 ChatDialogPanel의 구현 메서드를 직접 참조
AdvancedSettingsPanel(log_fn=self.dialog_panel.log)
```

**개선 후 (DIP 적용):**
```python
# AdvancedSettingsPanel은 시그널만 발행
class AdvancedSettingsPanel(QWidget):
    send_requested = pyqtSignal(int)
    reset_requested = pyqtSignal()

# MessageController가 두 뷰를 중재 — 뷰 간 직접 결합 없음
class MessageController:
    def _on_send(self, count: int):
        self._tab.dialog_panel.append_log(f"전송 시작 (횟수: {count})")

    def _on_reset(self):
        self._tab.adv_panel.reset()
        self._tab.dialog_panel.append_log("초기화 완료")
```

모든 컨트롤러는 생성자 주입으로 모델·뷰를 수신하며, `AppController`가 전체 의존성을 조립한다.
