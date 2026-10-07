from pydantic import BaseModel, EmailStr
from datetime import time, datetime


class UserCreate(BaseModel): 
    FirstName: str
    LastName: str
    Email: EmailStr
    Password: str
    Role: str


class UserLogin(BaseModel):
    Email: EmailStr
    Password: str


class TeacherCreate(BaseModel):
    UserId: int
    FirstName: str
    LastName: str
    Bio: str | None = None
    Specialization: str | None = None
    HourlyRate: float


class TeacherAvailabilityCreate(BaseModel):
    DayOfWeek: int
    StartTime: time
    EndTime: time


class BookingCreate(BaseModel):
    TeacherId: int
    StartDateTime: datetime
    EndDateTime: datetime


class PaymentCreate(BaseModel):
    BookingId: int
    PaymentMethod: str

class CallSessionCreate(BaseModel):
    BookingId: int