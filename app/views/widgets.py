from PyQt5.QtWidgets import QFrame, QPushButton, QWidget, QVBoxLayout, QLabel
from app.constants import C


def h_separator() -> QFrame:
    """수평 구분선 위젯 팩토리"""
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet(f"background: {C['border']}; border: none;")
    return line


def make_btn(
    text: str,
    bg: str = None,
    fg: str = None,
    border: str = None,
    radius: int = 4,
    font_size: int = 11,
    bold: bool = False,
    height: int = 34,
) -> QPushButton:
    """스타일이 적용된 버튼 팩토리 (OCP: 파라미터로 외형 확장)"""
    bg = bg or C["white"]
    fg = fg or C["text"]
    border = border or C["border"]
    weight = "bold" if bold else "normal"
    hover_bg = (
        "#e8b400" if bg == C["yellow"]
        else ("#128a3c" if bg == C["green"] else C["panel"])
    )
    btn = QPushButton(text)
    btn.setFixedHeight(height)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg};
            color: {fg};
            border: 1px solid {border};
            border-radius: {radius}px;
            font-size: {font_size}px;
            font-weight: {weight};
            padding: 0 8px;
        }}
        QPushButton:hover {{ background: {hover_bg}; }}
        QPushButton:pressed {{ background: {hover_bg}; }}
    """)
    return btn


def panel_header_widget(title: str) -> QWidget:
    """패널 상단 헤더 위젯 팩토리"""
    w = QWidget()
    w.setStyleSheet(f"background: {C['white']};")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)
    lbl = QLabel(title)
    lbl.setFixedHeight(28)
    lbl.setContentsMargins(12, 0, 0, 0)
    lbl.setStyleSheet(f"color: {C['text']}; font-size: 12px; font-weight: 600;")
    lay.addWidget(lbl)
    lay.addWidget(h_separator())
    return w
