def normalize_nigerian_phone(phone: str) -> str:
    phone = phone.strip().replace(" ", "")
    
    if phone.startswith("0") and len(phone) == 11:
        return "+234" + phone[1:]
    elif phone.startswith("234") and len(phone) == 13:
        return "+" + phone
    
    return phone
