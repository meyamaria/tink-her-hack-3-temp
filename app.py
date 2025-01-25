from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import threading
import time
from plyer import notification

app = Flask(__name__)

# Global variables to store notification intervals and data
WATER_INTERVAL = 3600  # 1 hour in seconds
SCREEN_INTERVAL = 10800  # 3 hours in seconds
STRETCH_INTERVAL = 7200  # 2 hours in seconds
user_data = []  # List to store sleep details


def send_priority_notification(title, message, priority=1):
    """Send desktop notifications with customizable priority."""
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )
    except Exception as e:
        print(f"Notification error: {e}")


def create_interval_reminder(title, message, interval_seconds):
    """Create a reminder that runs at fixed intervals."""
    while True:
        send_priority_notification(title, message)
        time.sleep(interval_seconds)


def sleep_and_stretch_reminder(sleep_time, wake_time, stretch_interval):
    """Advanced sleep and stretch reminder with precise timing."""
    last_stretch_time = time.time()

    while True:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%I:%M %p")

        # Sleep time notification
        if formatted_time == sleep_time:
            send_priority_notification(
                "Bedtime 🌙",
                "It's time to get some well-deserved rest!",
                priority=2
            )

        # Wake up notification
        if formatted_time == wake_time:
            send_priority_notification(
                "Good Morning! 🌞",
                "Rise and shine! A new day begins.",
                priority=1
            )

        # Periodic stretch reminders
        current_stretch_time = time.time()
        if current_stretch_time - last_stretch_time >= stretch_interval:
            send_priority_notification(
                "Stretch Break 🧘",
                "Time to stretch and move your body!",
                priority=3
            )
            last_stretch_time = current_stretch_time

        time.sleep(60)  # Check every minute


@app.route('/')
def home():
    return render_template('index.html', user_data=user_data)


@app.route('/set_notifications', methods=['POST'])
def set_notifications():
    try:
        # Collect form data
        name = request.form['name']
        sleep_hours = int(request.form['sleep_hours'])
        hour = int(request.form['hour'])
        minute = int(request.form['minute'])
        ampm = request.form['ampm']

        # Validate input
        if not all([name, sleep_hours, hour, minute, ampm]):
            return "Error: Please fill all fields."

        # Calculate sleep and wake times
        sleep_time = f"{hour:02d}:{minute:02d} {ampm}"
        wake_hour = (hour + sleep_hours) % 12 or 12
        wake_time = f"{wake_hour:02d}:{minute:02d} {ampm}"

        # Save user data
        user_data.append({
            "name": name,
            "sleep_time": sleep_time,
            "wake_time": wake_time,
            "sleep_hours": sleep_hours
        })

        # Start background threads for reminders
        threading.Thread(
            target=create_interval_reminder,
            args=("Hydration Alert 💧", "Time to drink water!", WATER_INTERVAL),
            daemon=True
        ).start()

        threading.Thread(
            target=create_interval_reminder,
            args=("Screen Break 🖥️", "Take a break from your screen!", SCREEN_INTERVAL),
            daemon=True
        ).start()

        threading.Thread(
            target=sleep_and_stretch_reminder,
            args=(sleep_time, wake_time, STRETCH_INTERVAL),
            daemon=True
        ).start()

        return redirect(url_for('home'))

    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == '__main__':
    app.run(debug=True)