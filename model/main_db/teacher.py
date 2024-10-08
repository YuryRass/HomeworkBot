from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.main_db.database import Base, bigint
from model.main_db.teacher_discipline import association_teacher_to_discipline
from model.main_db.teacher_group import association_teacher_to_group

if TYPE_CHECKING:
    from model.main_db.discipline import Discipline
    from model.main_db.group import Group


class Teacher(Base):
    __tablename__ = 'teachers'

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    telegram_id: Mapped[bigint] = mapped_column(nullable=False, unique=True)

    disciplines: Mapped[list["Discipline"]] = relationship(
        secondary=association_teacher_to_discipline,
        back_populates="teachers",
    )

    groups: Mapped[list["Group"]] = relationship(
        secondary=association_teacher_to_group,
        back_populates="teachers",
    )

    def __repr__(self):
        info: str = f'Преподаватель [ФИО: {self.full_name}, ' \
                    f'Telegram ID: {self.telegram_id}]'
        return info
