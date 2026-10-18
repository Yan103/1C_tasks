from typing import Optional
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import *
from .models import CaseDraft
from . import texts as T


class CaseDialog(QDialog):
    """Ветка создания самого дела"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(T.CASE_DIALOG_TITLE)
        self.setMinimumWidth(500)
        self.setModal(True)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(T.CASE_TITLE_PLACEHOLDER)

        self.description_input = QPlainTextEdit()
        self.description_input.setPlaceholderText(T.CASE_DESCRIPTION_PLACEHOLDER)
        self.description_input.setFixedHeight(95)

        self.comment_input = QPlainTextEdit()
        self.comment_input.setPlaceholderText(T.CASE_INITIAL_COMMENT_PLACEHOLDER)
        self.comment_input.setFixedHeight(80)

        today = QDate.currentDate()
        self.start_input = QDateEdit(today)
        self.start_input.setCalendarPopup(True)
        self.start_input.setDisplayFormat("dd.MM.yyyy")

        self.end_input = QDateEdit(today.addDays(7))
        self.end_input.setCalendarPopup(True)
        self.end_input.setDisplayFormat("dd.MM.yyyy")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.addRow(T.CASE_TITLE_LABEL, self.title_input)
        form.addRow(T.CASE_DESCRIPTION_LABEL, self.description_input)
        form.addRow(T.CASE_INITIAL_COMMENT_LABEL, self.comment_input)
        form.addRow(T.CASE_START_DATE_LABEL, self.start_input)
        form.addRow(T.CASE_END_DATE_LABEL, self.end_input)

        self.hint = QLabel(T.CASE_FORM_HINT)
        self.hint.setObjectName("mutedText")
        self.hint.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(T.SAVE_CASE)
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(T.CANCEL)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)
        heading = QLabel(T.NEW_CASE_HEADING)
        heading.setObjectName("dialogTitle")
        layout.addWidget(heading)
        layout.addLayout(form)
        layout.addWidget(self.hint)
        layout.addWidget(buttons)

    def _validate_and_accept(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, T.MISSING_TITLE_TITLE, T.MISSING_TITLE_MESSAGE)
            self.title_input.setFocus()
            return

        if self.start_input.date() > self.end_input.date():
            QMessageBox.warning(self, T.INVALID_DATES_TITLE, T.INVALID_DATES_MESSAGE)
            return

        self.accept()

    def draft(self):
        return CaseDraft(
            title=self.title_input.text().strip(),
            description=self.description_input.toPlainText().strip(),
            initial_comment=self.comment_input.toPlainText().strip(),
            start_date=self.start_input.date().toPython(),
            end_date=self.end_input.date().toPython())
