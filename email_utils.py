import smtplib
from email.mime.text import MIMEText
import random

# Generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# 📧 Send the OTP to a user's email
def send_otp_email(to_email):
    sender_email = "h8622498@gmail.com"         
    app_password = "tyeu ckkg wqrg azux"   

    otp = generate_otp()

    message = MIMEText(f"🔐 Your OTP for Criminal Tracking System is: {otp}")
    message['Subject'] = "Email Verification - Criminal Tracking System"
    message['From'] = sender_email
    message['To'] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)
        server.quit()

        print(f"✅ OTP sent to {to_email}")
        return otp
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        return None

# 🧪 Optional: Standalone test
if __name__ == "__main__":
    test_email = input("📧 Enter your email to receive a test OTP: ").strip()
    send_otp_email(test_email)