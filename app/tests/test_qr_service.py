import pytest
import base64
from unittest.mock import patch
from app.services.qr_service import generate_qr_code_png_base64, create_qr_token
from app.schemas.booking import BookingInDB
from app.core.config import settings
from datetime import datetime, timedelta
import jwt

# Mock settings for testing purposes
@pytest.fixture(autouse=True)
def mock_settings():
    with patch('app.core.config.settings') as mock_settings:
        mock_settings.SECRET_KEY = "supersecretkey"
        mock_settings.ALGORITHM = "HS256"
        yield mock_settings

def test_generate_qr_code_png_base64():
    # Test data - a dummy token for QR code generation
    dummy_token = "thisisadummytokenforqr"
    
    # Generate QR code
    qr_image_base64 = generate_qr_code_png_base64(dummy_token)
    
    # Verify result
    assert qr_image_base64 is not None
    assert isinstance(qr_image_base64, str)
    
    # Try to decode the base64 string to ensure it's valid
    try:
        decoded_image = base64.b64decode(qr_image_base64)
        # Check if it's a PNG by looking at the magic number (first few bytes)
        # PNG magic number: 89 50 4E 47 0D 0A 1A 0A
        assert decoded_image[:8] == b'\x89PNG\r\n\x1a\n'
    except Exception as e:
        pytest.fail(f"Failed to decode base64 QR image or verify PNG format: {e}")

def test_create_qr_token(mock_settings):
    # Create a dummy BookingInDB object
    booking_data = {
        "id": 1,
        "trip_id": 101,
        "passenger_id": 201,
        "seat_number": "A1",
        "is_paid": True,
        "payment_ref": "PAY123",
        "qr_token": None,
        "booked_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    booking = BookingInDB(**booking_data)

    token = create_qr_token(booking)

    assert isinstance(token, str)
    assert len(token) > 0

    # Verify the token can be decoded (optional, but good for completeness)
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_payload["booking_id"] == booking.id
    assert decoded_payload["passenger_id"] == booking.passenger_id
    assert decoded_payload["trip_id"] == booking.trip_id
    # Check expiration is roughly 1 day from now
    assert datetime.fromtimestamp(decoded_payload["exp"]) > datetime.utcnow()
    assert datetime.fromtimestamp(decoded_payload["exp"]) < datetime.utcnow() + timedelta(days=1, seconds=5) # Allow a small buffer
