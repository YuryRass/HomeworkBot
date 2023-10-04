from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database.main_db.database import Base

if TYPE_CHECKING:
    from model.main_db.group import Group
    from model.main_db.assigned_discipline import AssignedDiscipline


class Student(Base):
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    group_id: Mapped[int] = mapped_column(
        ForeignKey('groups.id', ondelete='CASCADE'),
        nullable=False
    )
    telegram_id: Mapped[int] = mapped_column(nullable=True, unique=True)

    group: Mapped["Group"] = relationship(
        back_populates="students"
    )

    homeworks: Mapped[list["AssignedDiscipline"]] = relationship(
        back_populates="student", cascade="all, delete, delete-orphan",
    )

    def __repr__(self):
        info: str = f'Студент [ФИО: {self.full_name}, ' \
                    f'ID группы: {self.group}, ' \
                    f'Telegram ID: {self.telegram_id}]'
        return info
