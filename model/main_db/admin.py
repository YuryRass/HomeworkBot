from sqlalchemy.orm import mapped_column, Mapped

from database.main_db.database import Base, bigint


class Admin(Base):
    __tablename__ = 'admin'

    telegram_id: Mapped[bigint] = mapped_column(primary_key=True)
    teacher_mode: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f'Admin [ID: {self.telegram_id}]'
