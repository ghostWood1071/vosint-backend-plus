import smtplib
from email.mime.text import MIMEText
from jinja2 import Template
from app.email.models import EmailModel
from db.init_db import get_collection_client
from fastapi_jwt_auth import AuthJWT
from fastapi import Depends
import urllib.parse

async def exec_forgot_password(req: EmailModel, authorize: AuthJWT = Depends()):
    base_url = "http://localhost:4300"

    # find user
    users_client = get_collection_client("users")
    user = await users_client.find_one({"email": req.email})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa tồn tại",
        )
    
    access_token = authorize.create_access_token(subject=str(user["_id"]))
    encoded_token = urllib.parse.quote_plus(access_token)

    # send email
    subject = "[VOSINT3-Plus] Quên mật khẩu"
    sender = "danglong2407@gmail.com"
    password = "qryw svrc dixr crsq"

    recipients = [req.email]

    # with open('../../templates/email/reset-password.html', 'r') as f:
    with open("templates/email/reset-password.html", "r") as f:
        template = Template(f.read())

    link = f"{base_url}/reset-password/{user['username']}/{encoded_token}"

    context = {
        "subject": subject,
        "link": link,
        "content": f"Nếu nút không hoạt động, sao chép và dán đường dẫn này lên trình duyệt: {link}"
    }

    html = template.render(context)
    html_message = MIMEText(html, 'html')
    html_message['Subject'] = context['subject']
    html_message['From'] = sender
    html_message['To'] = ', '.join(recipients)

    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, html_message.as_string())
       
    return "Message sent!"
