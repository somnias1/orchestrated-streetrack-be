"""Dashboard read schemas. TECHSPEC §4.1, §4.3."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class DashboardDuePeriodicExpenseRead(BaseModel):
    """One periodic subcategory with paid flag for a selected month. §3.3 due-status rule."""

    subcategory_id: uuid.UUID
    subcategory_name: str
    category_id: uuid.UUID
    category_name: str
    due_day: int | None
    paid: bool
