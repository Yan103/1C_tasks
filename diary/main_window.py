from datetime import date, datetime
from html import escape
from typing import Optional
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import *
from .case_dialog import CaseDialog
from .models import SORT_BY_ID, SORT_END_DATE_ASC, SORT_END_DATE_DESC
from .repository import DiaryRepository
from .styles import STYLESHEET
from . import texts as T


class DiaryWindow(QMainWindow):
    """Отрисовка графического окна приложения"""

    def __init__(self, repository: DiaryRepository):
        super().__init__()
        self.repository = repository
        self.case_rows: list[dict] = []
        self._selected_case_id: Optional[int] = None

        self.setWindowTitle(T.APP_TITLE)
        self.resize(1250, 820)
        self.setMinimumSize(980, 680)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(28, 24, 28, 20)
        root_layout.setSpacing(18)

        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        heading = QLabel(T.APP_TITLE)
        heading.setObjectName("mainTitle")
        subtitle = QLabel(T.WINDOW_SUBTITLE)
        subtitle.setObjectName("mutedText")
        title_box.addWidget(heading)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box, 1)

        self.add_button = QPushButton(T.ADD_CASE)
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self.add_case)
        header_layout.addWidget(self.add_button, 0, Qt.AlignmentFlag.AlignVCenter)
        root_layout.addLayout(header_layout)

        self.stats_label = QLabel(T.SUMMARY_LOADING)
        self.stats_label.setObjectName("summaryLabel")
        root_layout.addWidget(self.stats_label)

        # Для работы с поисковой строкой и фильтрами
        search_card = QFrame()
        search_card.setObjectName("card")
        search_layout = QVBoxLayout(search_card)
        search_layout.setContentsMargins(16, 14, 16, 14)
        search_layout.setSpacing(12)

        search_heading = QLabel(T.SEARCH_SECTION)
        search_heading.setObjectName("sectionTitle")
        search_layout.addWidget(search_heading)

        controls = QHBoxLayout()
        self.title_filter = QLineEdit()
        self.title_filter.setClearButtonEnabled(True)
        self.title_filter.setPlaceholderText(T.TITLE_PLACEHOLDER)
        self.title_filter.returnPressed.connect(self.search_cases)
        controls.addWidget(self.title_filter, 2)
        self.date_filter_enabled = QCheckBox(T.DATE_FILTER)
        controls.addWidget(self.date_filter_enabled)

        self.date_filter = QDateEdit(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDisplayFormat("dd.MM.yyyy")
        self.date_filter.setEnabled(False)
        self.date_filter_enabled.toggled.connect(self.date_filter.setEnabled)
        controls.addWidget(self.date_filter)

        self.search_button = QPushButton(T.SEARCH)
        self.search_button.clicked.connect(self.search_cases)
        controls.addWidget(self.search_button)
        self.clear_button = QPushButton(T.RESET_FILTERS)
        self.clear_button.clicked.connect(self.clear_filters)
        controls.addWidget(self.clear_button)

        self.refresh_button = QPushButton(T.REFRESH_DATABASE)
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.clicked.connect(self.refresh_cases)
        controls.addWidget(self.refresh_button)
        search_layout.addLayout(controls)

        sort_layout = QHBoxLayout()
        self.show_closed_checkbox = QCheckBox(T.SHOW_CLOSED_CASES)
        self.show_closed_checkbox.setChecked(False)
        self.show_closed_checkbox.toggled.connect(lambda _checked: self.refresh_cases())
        sort_layout.addWidget(self.show_closed_checkbox)
        sort_layout.addSpacing(24)

        sort_label = QLabel(T.SORT_LABEL)
        sort_label.setObjectName("mutedText")
        sort_layout.addWidget(sort_label)
        self.sort_combo = QComboBox()
        self.sort_combo.addItem(T.SORT_ID_ASC, SORT_BY_ID)
        self.sort_combo.addItem(T.SORT_END_ASC, SORT_END_DATE_ASC)
        self.sort_combo.addItem(T.SORT_END_DESC, SORT_END_DATE_DESC)
        self.sort_combo.currentIndexChanged.connect(lambda _index: self.refresh_cases())
        sort_layout.addWidget(self.sort_combo, 1)
        search_layout.addLayout(sort_layout)
        root_layout.addWidget(search_card)

        # Табличка с делами
        list_heading_row = QHBoxLayout()
        list_heading = QLabel(T.CASES_SECTION)
        list_heading.setObjectName("sectionTitle")
        self.result_label = QLabel(T.RESULTS_COUNT.format(count=0))
        self.result_label.setObjectName("mutedText")
        list_heading_row.addWidget(list_heading)
        list_heading_row.addStretch(1)
        list_heading_row.addWidget(self.result_label)
        root_layout.addLayout(list_heading_row)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            [T.COLUMN_NUMBER,
             T.COLUMN_TITLE,
             T.COLUMN_START_DATE,
             T.COLUMN_END_DATE,
             T.COLUMN_STATUS,
             T.COLUMN_LAST_COMMENT])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.setMinimumHeight(290)
        self.table.itemSelectionChanged.connect(self.show_selected_details)
        root_layout.addWidget(self.table, 3)

        # Дополнительная панель приложения
        details_card = QFrame()
        details_card.setObjectName("card")
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(16, 12, 16, 12)
        details_layout.setSpacing(8)

        details_header = QHBoxLayout()
        details_title = QLabel(T.DETAILS_SECTION)
        details_title.setObjectName("sectionTitle")
        details_header.addWidget(details_title)
        details_header.addStretch(1)

        self.add_comment_button = QPushButton(T.ADD_COMMENT)
        self.add_comment_button.setEnabled(False)
        self.add_comment_button.clicked.connect(self.add_comment)
        details_header.addWidget(self.add_comment_button)
        self.status_button = QPushButton(T.CLOSE_CASE)
        self.status_button.setObjectName("primaryButton")
        self.status_button.setEnabled(False)
        self.status_button.clicked.connect(self.toggle_case_status)
        details_header.addWidget(self.status_button)
        details_layout.addLayout(details_header)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText(T.DETAILS_PLACEHOLDER)
        self.details_text.setMinimumHeight(150)
        self.details_text.setMaximumHeight(210)
        details_layout.addWidget(self.details_text)
        root_layout.addWidget(details_card, 2)
        self.connection_label = QLabel(T.CONNECTION_INITIAL)
        self.connection_label.setObjectName("statusLine")
        root_layout.addWidget(self.connection_label)
        self.setCentralWidget(root)
        self.setStyleSheet(STYLESHEET)
        self.refresh_cases()

    def _filters(self):
        title = self.title_filter.text().strip()
        selected_date = (self.date_filter.date().toPython() if self.date_filter_enabled.isChecked() else None)
        sort_order = self.sort_combo.currentData() or SORT_BY_ID
        show_closed = self.show_closed_checkbox.isChecked()

        return title, selected_date, sort_order, show_closed

    def refresh_cases(self):
        """Перечитывает данные из БД и сохраняет выбор дела, если эта процедура возможна"""

        previously_selected_id = self._selected_case_id
        self.refresh_button.setEnabled(False)
        self.connection_label.setText(T.DATABASE_REFRESHING)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            title, selected_date, sort_order, show_closed = self._filters()
            rows = self.repository.list_cases(title, selected_date, sort_order, show_closed)
            counts = self.repository.count_cases(title, selected_date)
            active_count = counts["open"]
            closed_count = counts["closed"]
            self.case_rows = rows
            self._populate_table(rows)

            self.stats_label.setText(T.SUMMARY_FORMAT.format(total=active_count + closed_count, active=active_count, closed=closed_count))
            self.result_label.setText(T.RESULTS_COUNT.format(count=len(rows)))
            self.connection_label.setText(T.CONNECTION_READY.format(time=datetime.now().strftime("%H:%M:%S")))

            if rows:
                row_by_id = {int(record["id"]): index for index, record in enumerate(rows)}
                desired_id = previously_selected_id
                if desired_id not in row_by_id:
                    desired_id = int(rows[0]["id"])

                self.table.selectRow(row_by_id[desired_id])
            else:
                self._selected_case_id = None
                self.details_text.clear()
                self.add_comment_button.setEnabled(False)
                self.status_button.setEnabled(False)
                self.details_text.setPlaceholderText(T.NO_MATCHING_CASES)

        except Exception as error:
            self.connection_label.setText(T.DATABASE_REFRESH_FAILED)
            QMessageBox.critical(self, T.DATABASE_ERROR_TITLE, T.DATABASE_ERROR_MESSAGE.format(error=error))
        finally:
            QApplication.restoreOverrideCursor()
            self.refresh_button.setEnabled(True)

    def _populate_table(self, rows: list[dict]):
        """Определяем номер дела в текцщей конфигурации"""
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        for row_index, record in enumerate(rows):
            self.table.insertRow(row_index)
            values = [str(row_index + 1),
                      record["title"],
                      record["start_date"].strftime("%d.%m.%Y"),
                      record["end_date"].strftime("%d.%m.%Y"),
                      T.STATUS_OPEN if record["status"] == "open" else T.STATUS_CLOSED,
                      record["latest_comment"] or "—"]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, int(record["id"]))
                if column in (0, 2, 3, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column == 4:
                    item.setForeground(QColor("#18794e") if record["status"] == "open" else QColor("#c62828"))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                if column == 5:
                    item.setToolTip(value)
                self.table.setItem(row_index, column, item)

        self.table.blockSignals(False)

    def search_cases(self):
        self.refresh_cases()

    def clear_filters(self):
        self.title_filter.clear()
        self.date_filter_enabled.setChecked(False)
        self.show_closed_checkbox.blockSignals(True)
        self.show_closed_checkbox.setChecked(False)
        self.show_closed_checkbox.blockSignals(False)
        self.sort_combo.blockSignals(True)
        self.sort_combo.setCurrentIndex(0)
        self.sort_combo.blockSignals(False)
        self.refresh_cases()

    def add_case(self):
        dialog = CaseDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            case_id = self.repository.create_case(dialog.draft())
        except Exception as error:
            QMessageBox.critical(self, T.SAVE_CASE_ERROR_TITLE, T.SAVE_CASE_ERROR_MESSAGE.format(error=error))
            return

        self.title_filter.clear()
        self.date_filter_enabled.setChecked(False)
        self.refresh_cases()
        self.connection_label.setText(T.CASE_CREATED.format(case_id=case_id))

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and int(item.data(Qt.ItemDataRole.UserRole)) == case_id:
                self.table.selectRow(row)
                break

    @staticmethod
    def _format_timestamp(value: datetime):
        if value.tzinfo is not None:
            value = value.astimezone()
        return value.strftime("%d.%m.%Y %H:%M")

    def show_selected_details(self):
        row_index = self.table.currentRow()
        if row_index < 0 or self.table.item(row_index, 0) is None:
            self._selected_case_id = None
            self.add_comment_button.setEnabled(False)
            self.status_button.setEnabled(False)
            return

        case_id = int(self.table.item(row_index, 0).data(Qt.ItemDataRole.UserRole))
        self._selected_case_id = case_id
        self.add_comment_button.setEnabled(True)
        record = next((row for row in self.case_rows if int(row["id"]) == case_id), None)

        if record is None:
            return
        self.status_button.setEnabled(True)
        self.status_button.setText(
            T.CLOSE_CASE if record["status"] == "open" else T.REOPEN_CASE
        )

        try:
            comments = self.repository.get_comments(case_id)
        except Exception as error:
            self.details_text.setPlainText(T.COMMENT_LOAD_ERROR.format(error=error))
            return

        description = escape(record["description"].strip() or T.NO_DESCRIPTION)
        description = description.replace("\n", "<br>")
        html_parts = [f"<p><b>{escape(T.DESCRIPTION_HEADING)}</b></p>",
                      f"<p>{description}</p>",
                      f"<p><b>{escape(T.COMMENTS_HEADING)}</b></p>"]

        if comments:
            for comment in comments:
                timestamp = escape(self._format_timestamp(comment["created_at"]))
                comment_text = escape(comment["text"]).replace("\n", "<br>")
                html_parts.append(f'<p><b>[{timestamp}]</b>&nbsp;&nbsp;{comment_text}</p>')
        else:
            html_parts.append(f"<p>{escape(T.NO_COMMENTS)}</p>")

        self.details_text.setHtml("\n".join(html_parts))

    def add_comment(self):
        if self._selected_case_id is None:
            return

        text, accepted = QInputDialog.getMultiLineText(self, T.COMMENT_PROMPT_TITLE, T.COMMENT_PROMPT)
        if not accepted:
            return
        if not text.strip():
            QMessageBox.information(self, T.EMPTY_COMMENT_TITLE, T.EMPTY_COMMENT_MESSAGE)
            return

        try:
            self.repository.add_comment(self._selected_case_id, text)
        except Exception as error:
            QMessageBox.critical(self, T.DATABASE_ERROR_TITLE, T.COMMENT_SAVE_ERROR.format(error=error))
            return

        selected_id = self._selected_case_id
        self.refresh_cases()
        self.connection_label.setText(T.COMMENT_SAVED)
        self._select_case_by_id(selected_id)

    def _select_case_by_id(self, case_id: Optional[int]):
        if case_id is None:
            return

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and int(item.data(Qt.ItemDataRole.UserRole)) == case_id:
                self.table.selectRow(row)
                return

    def toggle_case_status(self):
        if self._selected_case_id is None:
            return

        record = next((row for row in self.case_rows if int(row["id"]) == self._selected_case_id), None)
        if record is None:
            return

        new_status = "closed" if record["status"] == "open" else "open"
        action = T.STATUS_CLOSE_ACTION if new_status == "closed" else T.STATUS_REOPEN_ACTION
        answer = QMessageBox.question(self, T.STATUS_CHANGE_TITLE, T.STATUS_CHANGE_CONFIRM.format(action=action, title=record["title"]))
        if answer != QMessageBox.StandardButton.Yes:
            return

        selected_id = self._selected_case_id
        try:
            self.repository.set_case_status(selected_id, new_status)
        except Exception as error:
            QMessageBox.critical(self, T.DATABASE_ERROR_TITLE, T.STATUS_SAVE_ERROR.format(error=error))
            return

        self.refresh_cases()
        self.connection_label.setText(T.CASE_UPDATED_STATUS)
        self._select_case_by_id(selected_id)
