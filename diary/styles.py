# Стили для дизайна самого приложения

STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f4f6fb;
    color: #1f2937;
    font-family: 'Segoe UI', 'Noto Sans', sans-serif;
    font-size: 13px;
}
QLabel#mainTitle { font-size: 27px; font-weight: 700; color: #111827; }
QLabel#dialogTitle { font-size: 21px; font-weight: 700; color: #111827; }
QLabel#sectionTitle { font-size: 15px; font-weight: 650; color: #111827; }
QLabel#mutedText { color: #6b7280; }
QLabel#summaryLabel {
    padding: 10px 14px; border-radius: 10px;
    background-color: #e9eefb; color: #344a78; font-weight: 600;
}
QLabel#statusLine { color: #6b7280; padding-left: 2px; }
QFrame#card {
    background-color: #ffffff; border: 1px solid #e3e8f1; border-radius: 12px;
}
QLineEdit, QDateEdit, QPlainTextEdit, QTextEdit, QComboBox {
    background-color: #ffffff; border: 1px solid #d7deea;
    border-radius: 7px; padding: 8px; selection-background-color: #c9d9ff;
}
QLineEdit:focus, QDateEdit:focus, QPlainTextEdit:focus,
QTextEdit:focus, QComboBox:focus { border: 1px solid #6487d8; }
QPushButton {
    background-color: #ffffff; border: 1px solid #d6deeb;
    border-radius: 7px; padding: 8px 12px; font-weight: 600;
}
QPushButton:hover { background-color: #f1f5fb; }
QPushButton:disabled { color: #9ca3af; background-color: #f3f4f6; }
QPushButton#primaryButton {
    color: #ffffff; background-color: #315ccf; border: 1px solid #315ccf;
    padding: 11px 16px; font-weight: 700;
}
QPushButton#primaryButton:hover { background-color: #254bb0; }
QPushButton#primaryButton:pressed { background-color: #1e429e; }
QPushButton#secondaryButton { color: #2f52a1; }
QTableWidget {
    background-color: #ffffff; alternate-background-color: #f8faff;
    border: 1px solid #e3e8f1; border-radius: 10px; gridline-color: #edf0f5;
    selection-background-color: #e2eaff; selection-color: #1f2937;
}
QHeaderView::section {
    background-color: #f8f9fc; color: #4b5563; font-weight: 650;
    padding: 10px 8px; border: none; border-bottom: 1px solid #e4e8f0;
}
QCheckBox { spacing: 7px; color: #374151; }
"""
