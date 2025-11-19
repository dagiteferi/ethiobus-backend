from fastapi import HTTPException

def process_mock_payment(payment_code: str) -> str:
    """
    Processes a mock payment.
    """
    if payment_code != "1234":
        raise HTTPException(status_code=400, detail="Invalid payment code. Use '1234'.")
    
    # In a real application, you would integrate with a payment gateway
    # and get a real payment reference.
    return f"MOCK-PAYMENT-{payment_code}"
