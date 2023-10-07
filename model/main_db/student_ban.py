from sqlalchemy.orm import mapped_column, Mapped

from database.main_db.database import Base, bigint


class StudentBan(Base):
    __tablename__ = 'banlist'

    telegram_id: Mapped[bigint] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return f'StudentBan [ID: {self.telegram_id}]'
