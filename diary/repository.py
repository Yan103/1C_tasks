from datetime import date
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from .models import SORT_BY_ID, SORT_END_DATE_ASC, SORT_END_DATE_DESC, CaseDraft


class DiaryRepository:
    """Доступ к PostgreSQL + подготовка результатов для отображения"""

    def __init__(self, dsn: str):
        self._dsn = dsn

    def _connect(self):
        return psycopg.connect(self._dsn, connect_timeout=4, row_factory=dict_row)

    def check_connection(self):
        with self._connect() as connection:
            connection.execute("SELECT 1 FROM cases LIMIT 1").fetchone()

    def list_cases(self, title_query: str = "", on_date: Optional[date] = None, sort_order: str = SORT_BY_ID, show_closed: bool = False):
        """Подготавливаем дела по заданным фильтрам"""

        order_by_options = {SORT_BY_ID: "c.id ASC", SORT_END_DATE_ASC: "c.end_date ASC, c.id ASC", SORT_END_DATE_DESC: "c.end_date DESC, c.id ASC"}
        order_by = order_by_options.get(sort_order, order_by_options[SORT_BY_ID])

        query = f"""
            SELECT
                c.id,
                c.title,
                c.description,
                c.start_date,
                c.end_date,
                c.status,
                c.created_at,
                c.updated_at,
                c.closed_at,
                COUNT(cm.id)::INTEGER AS comment_count,
                (
                    SELECT cm2.text
                    FROM comments AS cm2
                    WHERE cm2.case_id = c.id
                    ORDER BY cm2.created_at DESC, cm2.id DESC
                    LIMIT 1
                ) AS latest_comment
            FROM cases AS c
            LEFT JOIN comments AS cm ON cm.case_id = c.id
            WHERE TRUE
        """
        parameters: list[object] = []

        clean_title = title_query.strip()
        if clean_title:
            query += " AND c.title ILIKE %s"
            parameters.append(f"%{clean_title}%")

        if on_date is not None:
            query += " AND c.start_date <= %s AND c.end_date >= %s"
            parameters.extend([on_date, on_date])

        # По умолчанию показываются только активные дела (для показа открытых есть специальная кнопка)
        if not show_closed:
            query += " AND c.status = %s"
            parameters.append("open")

        query += f" GROUP BY c.id ORDER BY {order_by}"
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
            return list(rows)

    def count_cases(self, title_query: str = "", on_date: Optional[date] = None,):
        """Считаем активные и закрытые дела с учётом фильтров"""

        query = """
            SELECT
                COUNT(*) FILTER (WHERE c.status = 'open')::INTEGER   AS open_count,
                COUNT(*) FILTER (WHERE c.status = 'closed')::INTEGER AS closed_count
            FROM cases AS c
            WHERE TRUE
        """
        parameters: list[object] = []

        clean_title = title_query.strip()
        if clean_title:
            query += " AND c.title ILIKE %s"
            parameters.append(f"%{clean_title}%")

        if on_date is not None:
            query += " AND c.start_date <= %s AND c.end_date >= %s"
            parameters.extend([on_date, on_date])

        with self._connect() as connection:
            row = connection.execute(query, parameters).fetchone()

        if row is None:
            return {"open": 0, "closed": 0}

        return {"open": int(row["open_count"]), "closed": int(row["closed_count"]),}

    def create_case(self, draft: CaseDraft):
        """Создаёт дело и первый комментарий"""

        if not draft.title.strip():
            raise ValueError("Название дела не может быть пустым")
        if draft.end_date < draft.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала дела")

        with self._connect() as connection:
            row = connection.execute(
                """
                INSERT INTO cases (title, description, start_date, end_date)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (draft.title.strip(), draft.description.strip(), draft.start_date, draft.end_date)
            ).fetchone()
            if row is None:
                raise RuntimeError("БД не вернула ID созданного дела")

            case_id = int(row["id"])
            comment = draft.initial_comment.strip()
            if comment:
                connection.execute("INSERT INTO comments (case_id, text) VALUES (%s, %s)", (case_id, comment))
            return case_id

    def get_comments(self, case_id: int):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, text, created_at
                FROM comments
                WHERE case_id = %s
                ORDER BY created_at ASC, id ASC
                """,
                (case_id,)
            ).fetchall()
            return list(rows)

    def add_comment(self, case_id: int, text: str):
        if not text.strip():
            raise ValueError("Комментарий не может быть пустым")
        with self._connect() as connection:
            connection.execute("INSERT INTO comments (case_id, text) VALUES (%s, %s)", (case_id, text.strip()))
            connection.execute("UPDATE cases SET updated_at = CURRENT_TIMESTAMP WHERE id = %s", (case_id,))

    def set_case_status(self, case_id: int, new_status: str):
        if new_status not in {"open", "closed"}:
            raise ValueError("Неизвестный статус дела")

        with self._connect() as connection:
            row = connection.execute("SELECT id FROM cases WHERE id = %s FOR UPDATE", (case_id,)).fetchone()
            if row is None:
                raise LookupError("Дело отсутствует в базе данных")

            connection.execute(
                """
                UPDATE cases
                SET status = %s,
                    closed_at = CASE
                        WHEN %s = 'closed' THEN CURRENT_TIMESTAMP
                        ELSE NULL
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (new_status, new_status, case_id))
