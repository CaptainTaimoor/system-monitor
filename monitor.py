import psutil
import yagmail
from email_config import EMAIL, APP_PASSWORD, TO_EMAIL

def send_alert(subject, message):
    yag = yagmail.SMTP(EMAIL, APP_PASSWORD)
    yag.send(to=TO_EMAIL, subject=subject, contents=message)

def check_system():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    print("🔍 System Health Check:")
    print(f"CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%")

    if cpu > 80:
        send_alert("⚠️ High CPU Usage", f"CPU usage is {cpu}%")
    if memory > 80:
        send_alert("⚠️ High Memory Usage", f"Memory usage is {memory}%")
    if disk > 90:
        send_alert("⚠️ Low Disk Space", f"Disk usage is {disk}%")

if __name__ == "__main__":
    check_system()

