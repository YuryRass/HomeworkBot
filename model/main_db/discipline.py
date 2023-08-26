from typing import List

from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database.main_db.database import Base
from model.main_db.discipline_group import association_discipline_to_group
from model.main_db.teacher_discipline import association_teacher_to_discipline


class Discipline(Base):
    __tablename__ = 'disciplines'

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(10), nullable=False)
    path_to_test: Mapped[str] = mapped_column(String(200), nullable=False)
    path_to_answer: Mapped[str] = mapped_column(String(200), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    max_tasks: Mapped[int] = mapped_column(nullable=False)
    max_home_works: Mapped[int] = mapped_column(nullable=False)
    works: Mapped[str] = mapped_column(JSON, nullable=False)  # DisciplineWorksConfig

    groups: Mapped[List["Group"]] = relationship(
        secondary=association_discipline_to_group,
        back_populates="disciplines",
    )

    teachers: Mapped[List["Teacher"]] = relationship(
        secondary=association_teacher_to_discipline,
        back_populates="disciplines",
    )

    def __repr__(self):
        info: str = f'Дисциплина {self.short_name}, ' \
                    f'max_tasks: {self.max_tasks}, ' \
                    f'works: {self.works}]'
        return info
