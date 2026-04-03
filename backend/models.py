from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import date, datetime
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    memberships = relationship("Membership", back_populates="user")


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    start_date = Column(Date, default=date.today)

    user = relationship("User", back_populates="memberships")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(Date)
    location = Column(String)
    description = Column(String, nullable=False)
    capacity = Column(Integer, default=100)
    price = Column(Integer)


class Newsletter(Base):
    __tablename__ = "newsletter"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    message = Column(String)    


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String)
    booked_at = Column(DateTime, default=datetime.utcnow)
    qr_code = Column(String)

    event = relationship("Event")
    ticket_image = Column(String)

class Payment(Base):

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    event_id = Column(Integer)
    razorpay_payment_id = Column(String)
    razorpay_order_id = Column(String)
    amount = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
