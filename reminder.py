import customtkinter as ctk
from datetime import datetime, timedelta
import time
import threading
import winsound
from tkcalendar import DateEntry
import platform
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ReliableReminderApp(ctk.CTk):
    def __init__(self ,master=None):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_closing_master)
        self.title("Task Reminder Pro")
        self.geometry("600x600")
        self.master = master
        self.reminders = []
        self.running = True
        self.configure_grid()
        self.create_widgets()
        self.start_worker_thread()

    def on_closing_master(self):
        self.destroy()
        sys.exit()

    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        for i in range(8): self.grid_rowconfigure(i, weight=1)

    def create_widgets(self):
        # Header
        self.header = ctk.CTkLabel(self, text="TASK REMINDER",
                                   font=("Arial", 24, "bold"), text_color="#2CC985")
        self.header.grid(row=0, column=0, pady=20)

        # Input Frame
        input_frame = ctk.CTkFrame(self, corner_radius=15)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Task Input
        self.task_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter task description...",
                                       width=400, height=40, border_color="#2CC985")
        self.task_entry.pack(pady=10, padx=20, fill="x")

        # Date and Time Picker
        time_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        time_frame.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(time_frame, text="Date:").pack(side="left", padx=5)
        self.date_picker = DateEntry(time_frame, date_pattern="yyyy-mm-dd",
                                     font=("Arial", 12), background="#2CC985")
        self.date_picker.pack(side="left", padx=5)

        ctk.CTkLabel(time_frame, text="Time:").pack(side="left", padx=5)
        self.time_picker = ctk.CTkEntry(time_frame, placeholder_text="HH:MM",
                                        width=100, height=30)
        self.time_picker.pack(side="left", padx=5)

        back_btn = ctk.CTkButton(
            input_frame,
            text="<- back",
            command=self.go_back,
            fg_color="transparent",
            font=("Tahoma", 14),
            hover_color="#444444"
        )
        back_btn.pack(side="left", padx=5)


        # Set Reminder Button
        self.set_btn = ctk.CTkButton(input_frame, text="➕ Set Reminder",
                                     command=self.set_reminder, fg_color="#2CC985",
                                     hover_color="#1EAE6F", font=("Arial", 14))
        self.set_btn.pack(side="left", padx=50)



        # Reminders List
        self.reminders_frame = ctk.CTkScrollableFrame(self, corner_radius=15)
        self.reminders_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

    def go_back(self):
        # Destroy current app window
        self.destroy()
        # Show the parent CompanyList window
        self.master.deiconify()

    def create_reminder_card(self, reminder):
        card = ctk.CTkFrame(self.reminders_frame, corner_radius=10)
        card.pack(pady=5, padx=5, fill="x")

        # Progress Bar
        progress_bar = ctk.CTkProgressBar(card, orientation="horizontal",
                                          height=5, fg_color="#1E1E1E",
                                          progress_color="#2CC985")
        progress_bar.set(0)
        progress_bar.pack(fill="x", padx=10)
        reminder["progress_bar"] = progress_bar

        # Content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=5)

        text = f"⏰ {reminder['time'].strftime('%d %b %Y %H:%M')} - {reminder['task']}"
        ctk.CTkLabel(content_frame, text=text, anchor="w").pack(side="left", fill="x", expand=True)

        # Cancel Button
        cancel_btn = ctk.CTkButton(content_frame, text="✖", width=30, height=30,
                                   fg_color="transparent", hover_color="#FF4444",
                                   command=lambda: self.cancel_reminder(reminder))
        cancel_btn.pack(side="right")

        return card

    def set_reminder(self):
        task = self.task_entry.get()
        date = self.date_picker.get_date()
        time_str = self.time_picker.get()

        try:
            if not task:
                raise ValueError("Please enter a task description")

            reminder_time = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            current_time = datetime.now()

            # if reminder_time <= current_time:
            #     raise ValueError("Please select a future time")

            # ابتدا دیکشنری یادآوری بدون progress_bar بساز
            reminder = {
                "task": task,
                "time": reminder_time,
                "card": None,
                "progress_bar": None,
                "created": datetime.now(),
                "triggered": False  # کلید اضافه شده برای جلوگیری از KeyError
            }

            # کارت و نوار پیشرفت را بساز، و progress_bar را در خود reminder ذخیره کن
            card = self.create_reminder_card(reminder)
            reminder["card"] = card

            # حالا که reminder کامل شد، آن را به لیست اضافه کن
            self.reminders.append(reminder)
            self.clear_inputs()

        except ValueError as e:
            self.show_error(str(e))

    def start_worker_thread(self):
        def worker():
            while self.running:
                now = datetime.now()

                # Update progress bars
                for reminder in self.reminders:
                    if now < reminder["time"]:
                        total = (reminder["time"] - reminder["created"]).total_seconds()
                        elapsed = (now - reminder["created"]).total_seconds()
                        progress = min(elapsed / total, 1.0)
                        reminder["progress_bar"].set(progress)

                # Check reminders
                for reminder in self.reminders[:]:
                    if not reminder["triggered"] and now >= reminder["time"]:
                        self.trigger_alert(reminder)
                        reminder["triggered"] = True
                        self.after(500, lambda r=reminder: self.cancel_reminder(r))

                time.sleep(0.1)

        threading.Thread(target=worker, daemon=True).start()

    def trigger_alert(self, reminder):
        # Play sound
        if platform.system() == "Windows":
            winsound.Beep(1000, 1000)
        else:
            print("\a")  # System beep for other OS

        # Show alert
        self.after(0, lambda: self.show_alert_window(reminder["task"]))

    def show_alert_window(self, task):
        alert_window = ctk.CTkToplevel(self)
        alert_window.title("Reminder!")
        alert_window.geometry("300x150")
        alert_window.grab_set()

        ctk.CTkLabel(alert_window, text="🔔 Time's Up!", font=("Arial", 16)).pack(pady=10)
        ctk.CTkLabel(alert_window, text=f"Task: {task}").pack()
        ctk.CTkButton(alert_window, text="OK", command=alert_window.destroy,
                      fg_color="#2CC985").pack(pady=10)

    def cancel_reminder(self, reminder):
        if reminder in self.reminders:
            reminder["card"].destroy()
            self.reminders.remove(reminder)

    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("300x150")
        error_window.grab_set()

        ctk.CTkLabel(error_window, text="⚠️ Error!", font=("Arial", 16)).pack(pady=10)
        ctk.CTkLabel(error_window, text=message).pack()
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy,
                      fg_color="#FF4444").pack(pady=10)

    def clear_inputs(self):
        self.task_entry.delete(0, "end")
        self.time_picker.delete(0, "end")
        self.date_picker.set_date(datetime.now())

    def on_closing(self):
        self.running = False
        self.destroy()


if __name__ == "__main__":
    app = ReliableReminderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()