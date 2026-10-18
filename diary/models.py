from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CaseDraft:
    """Данные для создания нового дела в БД"""

    title: str
    description: str
    initial_comment: str
    start_date: date
    end_date: date


SORT_BY_ID = "id_asc"
SORT_END_DATE_ASC = "end_asc"
SORT_END_DATE_DESC = "end_desc"
