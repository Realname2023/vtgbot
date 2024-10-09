from sqlalchemy import DateTime, ForeignKey, String, Text, BigInteger, func, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    user_name: Mapped[str]  = mapped_column(String(150), nullable=True)
    full_name: Mapped[str]  = mapped_column(String(500), nullable=True)


class Client(Base):
    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    city: Mapped[str] = mapped_column(String(100))
    org_name: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String(100))
    
    user: Mapped['User'] = relationship(backref='clients')


class Category(Base):
    __tablename__ = 'categories'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    callback: Mapped[str] = mapped_column(String(150))
    edit_text: Mapped[str] = mapped_column(Text)
    row_width: Mapped[str] = mapped_column(String(50))
    buttons_text: Mapped[str] = mapped_column(Text)
    buttons_data : Mapped[str] = mapped_column(Text)


class Goods(Base):
    __tablename__ = 'goods'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    photo: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    verbose_name: Mapped[str] = mapped_column(String(500), nullable=True)
    unit: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    button_texts: Mapped[str] = mapped_column(Text)
    button_datas: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(100))
    is_arenda: Mapped[int] = mapped_column(Integer)
    b_id: Mapped[str] = mapped_column(String(50))

    
class CurrentOrder(Base):
    __tablename__ = 'current_orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    good_id: Mapped[int] = mapped_column(ForeignKey('goods.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(BigInteger)
    arenda_time: Mapped[int] = mapped_column(BigInteger)
    total_price: Mapped[int] = mapped_column(BigInteger)

    user: Mapped['User'] = relationship(backref='current_orders')
    good: Mapped['Goods'] = relationship(backref='current_orders')


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    order_text: Mapped[str] = mapped_column(Text)

    

class Actions(Base):
    __tablename__ = 'actions'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    photo: Mapped[str] = mapped_column(String(1000))
    text: Mapped[str] = mapped_column(Text)
