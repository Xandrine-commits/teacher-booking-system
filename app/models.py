from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Time, text
from app.database import Base


class User(Base):
    __tablename__ = "Users"

    UserId = Column(Integer, primary_key=True, index=True)
    FirstName = Column(String(100), nullable=False)
    LastName = Column(String(100), nullable=False)
    Email = Column(String(255), unique=True, nullable=False)
    PasswordHash = Column(String(255), nullable=False)
    Role = Column(String(20), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False, server_default=text("GETDATE()"))


class Teacher(Base):
    __tablename__ = "Teachers"

    TeacherId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, nullable=False)
    FirstName = Column(String(100), nullable=False)
    LastName = Column(String(100), nullable=False)
    Bio = Column(String(1000), nullable=True)
    Specialization = Column(String(255), nullable=True)
    HourlyRate = Column(Numeric(10, 2), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(
        DateTime,
        nullable=False,
        server_default=text("GETDATE()")
    )


class TeacherAvailability(Base):
    __tablename__ = "TeacherAvailability"

    AvailabilityId = Column(Integer, primary_key=True, index=True)
    TeacherId = Column(Integer, nullable=False)
    DayOfWeek = Column(Integer, nullable=False)
    StartTime = Column(Time, nullable=False)
    EndTime = Column(Time, nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)


class Booking(Base):
    __tablename__ = "Bookings"

    BookingId = Column(Integer, primary_key=True, index=True)
    StudentId = Column(Integer, nullable=False)
    TeacherId = Column(Integer, nullable=False)
    StartDateTime = Column(DateTime, nullable=False)
    EndDateTime = Column(DateTime, nullable=False)
    Status = Column(String(20), nullable=False, default="Pending")
    CreatedAt = Column(
        DateTime,
        nullable=False,
        server_default=text("GETDATE()")
    )


class Payment(Base):
    __tablename__ = "Payments"

    PaymentId = Column(Integer, primary_key=True, index=True)
    BookingId = Column(Integer, nullable=False)
    Amount = Column(Numeric(10, 2), nullable=False)
    PaymentMethod = Column(String(30), nullable=False)
    TransactionId = Column(String(255), nullable=True)
    Status = Column(String(30), nullable=False, default="Pending")
    PaidAt = Column(DateTime, nullable=True)
    CreatedAt = Column(
        DateTime,
        nullable=False,
        server_default=text("GETDATE()")
    )

class CallSession(Base):
    __tablename__ = "CallSessions"

    CallSessionId = Column(Integer, primary_key=True, index=True)
    BookingId = Column(Integer, nullable=False)
    Provider = Column(String(50), nullable=False)
    RoomId = Column(String(255), nullable=False)
    Status = Column(String(30), nullable=False, default="Scheduled")
    StartDateTime = Column(DateTime, nullable=False)
    EndDateTime = Column(DateTime, nullable=False)
    CreatedAt = Column(
        DateTime,
        nullable=False,
        server_default=text("GETDATE()")
    )