import os
import sys
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from diary import texts as T
from diary.config import DEFAULT_DSN
from diary.main_window import DiaryWindow
from diary.repository import DiaryRepository


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(T.APP_TITLE)
    app.setFont(QFont("Noto Sans", 10))

    dsn = os.environ.get("DIARY_DSN", DEFAULT_DSN)
    repository = DiaryRepository(dsn)
    window = DiaryWindow(repository)

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
