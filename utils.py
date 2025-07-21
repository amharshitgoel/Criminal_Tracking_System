import re

def is_valid_aadhaar(aadhaar):
    """
    Validates if the Aadhaar number is exactly 12 digits.
    Must be numeric only.
    """
    return bool(re.fullmatch(r'\d{12}', aadhaar))

def is_valid_mobile(mobile):
    """
    Validates a mobile number:
    - Must be 10 digits
    - Must start with any digit from 1 to 9 (i.e., not 0)
    """
    return bool(re.fullmatch(r'[1-9]\d{9}', mobile))