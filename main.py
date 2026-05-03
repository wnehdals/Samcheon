#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""이지카톡 PRO — 진입점"""

import sys
from PyQt5.QtWidgets import QApplication
from app.controllers.app_controller import AppController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    controller = AppController()
    controller.main_window.show()
    sys.exit(app.exec_())
