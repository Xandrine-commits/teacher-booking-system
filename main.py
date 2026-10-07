from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, Teacher, TeacherAvailability, Booking, Payment, CallSession
from passlib.context import CryptContext
from app.schemas import (
    UserCreate,
    UserLogin,
    TeacherCreate,
    TeacherAvailabilityCreate,
    BookingCreate,
    PaymentCreate,
    CallSessionCreate
)
from app.auth.jwt import create_access_token,verify_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime

app = FastAPI(title="Teacher booking & Voice call System")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    payload = verify_access_token(token)

    if not payload:
        return None

    return payload

def require_role(required_role: str):
    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        if not current_user:
            return None

        if current_user.get("role") != required_role:
            return None

        return current_user
    return role_checker


@app.get("/")
def root():
    return {"message": "Teacher Booking API is running"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return {
        "users_count": len(users),
    }

@app.get("/me")
def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    
    if not current_user:
        return {"message": "Invalid or expired token"}

    return {
        "user_id": current_user.get("user_id"),
        "role": current_user.get("role"),
    }

@app.get("/student-only")
def student_only(
    current_user: dict = Depends(require_role("student"))
):
    if not current_user:
        return {"message": "Access denied"}

    return {
        "message": "Welcome student!",
        "user_id": current_user.get("user_id")
    }

@app.get("/teachers")
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teacher).filter(Teacher.IsActive == True).all()

    return teachers

@app.get("/teachers/{teacher_id}/availability")
def get_teacher_availability(
    teacher_id: int,
    db: Session = Depends(get_db)
):
    availability = db.query(TeacherAvailability).filter(
        TeacherAvailability.TeacherId == teacher_id,
        TeacherAvailability.IsActive == True
    ).all()

    return availability

@app.get("/bookings")
def get_my_bookings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return {"message": "Invalid or expired token"}

    bookings = db.query(Booking).filter(
        Booking.StudentId == current_user.get("user_id")
    ).all()

    return bookings

@app.get("/bookings/{booking_id}")
def get_booking(
    booking_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return {"message": "Invalid or expired token"}

    booking = db.query(Booking).filter(
        Booking.BookingId == booking_id,
        Booking.StudentId == current_user.get("user_id")
    ).first()

    if not booking:
        return{"message": "Booking not found"}

    return booking

@app.get("/payments/{payment_id}")
def get_payment(
    payment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return {"message": "Invalid or expired token"}

    payment = db.query(Payment).filter(
        Payment.PaymentId == payment_id
    ).first()

    if not payment:
        return {"message": "Payment not found"}

    booking = db.query(Booking).filter(
        Booking.BookingId == payment.BookingId,
        Booking.StudentId == current_user.get("user_id")
    ).first()

    if not booking:
        return {"message": "Payment not found"}

    return payment

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.Password)

    new_user = User(
        FirstName=user.FirstName,
        LastName=user.LastName,
        Email=user.Email,
        PasswordHash=hashed_password,
        Role=user.Role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.UserId,
    }

@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.Email == user.Email).first()

    if not existing_user:
        return {"message": "Invalid email or password"}

    password_valid = pwd_context.verify(user.Password, existing_user.PasswordHash)

    if not password_valid:
        return {"message": "Invalid email or password"}

    access_token = create_access_token({
        "user_id": existing_user.UserId,
        "role": existing_user.Role
    })

    return {
    "message": "Login successful",
    "access_token": access_token,
    "token_type": "bearer"
}

@app.post("/teachers")
def create_teacher(
    teacher: TeacherCreate,
    db: Session = Depends(get_db)
):
    new_teacher = Teacher(
        UserId=teacher.UserId,
        FirstName=teacher.FirstName,
        LastName=teacher.LastName,
        Bio=teacher.Bio,
        Specialization=teacher.Specialization,
        HourlyRate=teacher.HourlyRate
    )

    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)

    return {
        "message": "Teacher created successfully",
        "teacher_id": new_teacher.TeacherId
    }

@app.post("/teachers/{teacher_id}/availability")
def create_teacher_availability(
    teacher_id: int,
    availability: TeacherAvailabilityCreate,
    db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).filter(
        Teacher.TeacherId == teacher_id
    ).first()

    if not teacher:
        return {"message": "Teacher not found"}

    new_availability = TeacherAvailability(
        TeacherId=teacher_id,
        DayOfWeek=availability.DayOfWeek,
        StartTime=availability.StartTime,
        EndTime=availability.EndTime
    )

    db.add(new_availability)
    db.commit()
    db.refresh(new_availability)

    return {
        "message": "Teacher availability created successfully",
        "availability_id": new_availability.AvailabilityId
    }

@app.post("/bookings")
def create_booking(
    booking: BookingCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return {"message": "Invalid or expired token"}

    teacher = db.query(Teacher).filter(
        Teacher.TeacherId == booking.TeacherId,
        Teacher.IsActive == True
    ).first()

    if not teacher:
        return {"message": "Teacher not found"}

    if booking.EndDateTime <= booking.StartDateTime:
        return {
            "message": "End time must be later than start time"
        }

    day_of_week = booking.StartDateTime.isoweekday()

    availability = db.query(TeacherAvailability).filter(
        TeacherAvailability.TeacherId == booking.TeacherId,
        TeacherAvailability.DayOfWeek == day_of_week,
        TeacherAvailability.IsActive == True,
        TeacherAvailability.StartTime <= booking.StartDateTime.time(),
        TeacherAvailability.EndTime >= booking.EndDateTime.time()
    ).first()

    if not availability:
        return {
            "message": "Booking time is outside the teacher's availability"
        }

    existing_booking = db.query(Booking).filter(
        Booking.TeacherId == booking.TeacherId,
        Booking.Status.in_(["Pending", "Paid", "Confirmed"]),
        Booking.StartDateTime < booking.EndDateTime,
        Booking.EndDateTime > booking.StartDateTime
    ).first()

    if existing_booking:
        return {
            "message": "Teacher is already booked for this time"
        }

    new_booking = Booking(
        StudentId=current_user.get("user_id"),
        TeacherId=booking.TeacherId,
        StartDateTime=booking.StartDateTime,
        EndDateTime=booking.EndDateTime,
        Status="Pending"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {
        "message": "Booking created successfully",
        "booking_id": new_booking.BookingId
    }

@app.post("/payments")
def create_payment(
    payment: PaymentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return {"message": "Invalid or expired token"}

    booking = db.query(Booking).filter(
        Booking.BookingId == payment.BookingId,
        Booking.StudentId == current_user.get("user_id")
    ).first()

    if not booking:
        return {"message": "Booking not found"}

    if booking.Status != "Pending":
        return {
            "message": "This booking is not available for payment"
        }

    teacher = db.query(Teacher).filter(
        Teacher.TeacherId == booking.TeacherId
    ).first()

    if not teacher:
        return { "message": "Teacher not found"}

    new_payment = Payment(
        BookingId=booking.BookingId,
        Amount=teacher.HourlyRate,
        PaymentMethod=payment.PaymentMethod,
        Status="Pending"
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return {
        "message": "Payment created successfully",
        "payment_id": new_payment.PaymentId,
        "booking_id": booking.BookingId,
        "amount": new_payment.Amount,
        "status": new_payment.Status
    }

@app.post("/payments/{payment_id}/confirm")
def confirm_payment(
    payment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return {"message": "Invalid or expired token"}

    payment = db.query(Payment).filter(
        Payment.PaymentId == payment_id
    ).first()

    if not payment:
        return{"message": "Payment not found"}

    booking = db.query(Booking).filter(
        Booking.BookingId == payment.BookingId,
        Booking.StudentId == current_user.get("user_id")
    ).first()

    if not booking:
        return {"message":"Payment not found"}

    if payment.Status != "Pending":
        return {
            "message": "Payment is not pending"
        }

    payment.Status = "Paid"
    payment.PaidAt = datetime.now()

    booking.Status = "Paid"

    db.commit()
    db.refresh(payment)
    db.refresh(booking)

    return {
        "message": "Payment confirmed successfully",
        "payment_id": payment.PaymentId,
        "payment_status": payment.Status,
        "booking_id": booking.BookingId,
        "booking_status": booking.Status
    }

@app.post("/call-sessions")
def create_call_session(
    call_session: CallSessionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return {"message": "Invalid or expired token"}

    booking = db.query(Booking).filter(
        Booking.BookingId == call_session.BookingId,
        Booking.StudentId == current_user.get("user_id")
    ).first()

    if not booking:
        return { "message": "Booking not found"}

    if booking.Status != "Paid":
        return {
            "message": "Booking must be paid before creating a call session"
        }

    existing_session = db.query(CallSession).filter(
        CallSession.BookingId == booking.BookingId
    ).first()

    if existing_session:
        return {
            "message": "Call session already exists"
        }

    new_call_session = CallSession(
        BookingId=booking.BookingId,
        Provider="Pending",
        RoomId=f"booking-{booking.BookingId}",
        Status="Scheduled",
        StartDateTime=booking.StartDateTime,
        EndDateTime=booking.EndDateTime
    )

    db.add(new_call_session)
    db.commit()
    db.refresh(new_call_session)

    return {
         "message": "Call session created successfully",
        "call_session_id": new_call_session.CallSessionId,
        "booking_id": new_call_session.BookingId,
        "provider": new_call_session.Provider,
        "room_id": new_call_session.RoomId,
        "status": new_call_session.Status,
        "start_date_time": new_call_session.StartDateTime,
        "end_date_time": new_call_session.EndDateTime
    }

    
