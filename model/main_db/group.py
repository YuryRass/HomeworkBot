from typing import List, TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.main_db.database import Base
from model.main_db.discipline_group import association_discipline_to_group
from model.main_db.teacher_group import association_teacher_to_group

if TYPE_CHECKING:
    from model.main_db.student import Student
    from model.main_db.teacher import Teacher
    from model.main_db.discipline import Discipline


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str] = Column(String(20), unique=True)

    students: Mapped[List["Student"]] = relationship(
        back_populates="group",
        cascade="all, delete, delete-orphan",
        lazy='selectin',
    )

    disciplines: Mapped[List["Discipline"]] = relationship(
        secondary=association_discipline_to_group,
        back_populates="groups",
        lazy='selectin',
    )

    teachers: Mapped[List["Teacher"]] = relationship(
        secondary=association_teacher_to_group,
        back_populates="groups",
        lazy='selectin',
    )

    def __repr__(self):
        return f'Группа [ID: {self.id}, Название: {self.group_name}]'
