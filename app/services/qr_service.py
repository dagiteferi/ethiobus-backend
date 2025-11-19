import qrcode
import base64
from io import BytesIO
from jose import jwt, JWTError
from datetime import datetime, timedelta

from app.core.config import settings
from app.schemas.booking import BookingInDB

def create_qr_token(booking: BookingInDB) -> str:
    """
    Creates a JWT token for the QR code.
    """
    to_encode = {
        "booking_id": booking.id,
        "passenger_id": booking.passenger_id,
        "trip_id": booking.trip_id,
        "exp": datetime.utcnow() + timedelta(days=1) # QR valid for 1 day
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_qr_token(token: str) -> dict | None:
    """
    Verifies a QR token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_qr_code_png_base64(token: str) -> str:
    """
    Generates a QR code and returns it as a base64 encoded PNG.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str
