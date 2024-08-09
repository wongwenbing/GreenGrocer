import smtplib
from email.message import EmailMessage

# creates SMTP session
# s = smtplib.SMTP('smtp.gmail.com', 587)
# # start TLS for security
# s.starttls()
# # Authentication
# s.login("staff.greengrocerr@gmail.com", "fjad oapl nsac lkfa")
# # message to be sent
# message = "Message_you_need_to_send"
# # sending the mail
# s.sendmail("staff.greengrocer@gmail.com", "aniskyguy331@gmail.com", message)
# # terminating the session
# s.quit()

EMAIL_ADDRESS = 'staff.greengrocerr@gmail.com'
EMAIL_PASSWORD = 'fjad oapl nsac lkfa'

msg = EmailMessage()
msg['Subject'] = 'Report Generated Successfully!'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'aniskyguy331@gmail.com'
msg.set_content('This is to inform you that the report has been generated successfully.')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)
