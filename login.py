import customtkinter as ctk
import json
import os
from company import CompanyList
import sys

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AuthSystem:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Secure Authentication")
        self.window.geometry("450x650")
        self.window.resizable(False, False)
        self.window.configure(fg_color="#2B2B2B")

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bind Enter key to the window
        self.window.bind("<Return>", lambda event: self.login())

        # Initialize user data storage
        self.users_file = "users.json"
        self.remember_me_file = "remember_me.json"
        self.remembered_user = self.load_remembered_user()

        self.create_login_frame()
        self.create_signup_frame()
        self.show_login_frame()

        self.window.mainloop()

    def on_closing(self):
        self.window.destroy()
        sys.exit()

    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(
            self.window, 
            corner_radius=25,
            fg_color="#363636",
            border_width=2,
            border_color="#4A4A4A"
        )
        self.login_frame.pack_propagate(False)
        self.login_frame.configure(width=380, height=580)

        # Login UI Elements
        self.login_label = ctk.CTkLabel(
            self.login_frame, 
            text="Welcome Back!",
            font=("Roboto Medium", 24),
            text_color="#FFFFFF"
        )
        self.login_label.pack(pady=(40, 30))

        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            width=300,
            height=45,
            placeholder_text="Username",
            font=("Roboto", 14),
            border_color="#4A4A4A",
            fg_color="#2B2B2B"
        )
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            width=300,
            height=45,
            show="•",
            placeholder_text="Password",
            font=("Roboto", 14),
            border_color="#4A4A4A",
            fg_color="#2B2B2B"
        )
        self.password_entry.pack(pady=10)

        self.remember_me = ctk.CTkCheckBox(
            self.login_frame, 
            text="Remember Me",
            font=("Roboto", 12),
            checkbox_width=20,
            checkbox_height=20,
            text_color="#A0A0A0"
        )
        self.remember_me.pack(pady=10)

        if self.remembered_user:
            self.username_entry.insert(0, self.remembered_user)
            self.remember_me.select()

        self.login_button = ctk.CTkButton(
            self.login_frame, 
            text="Login",
            command=self.login,
            width=300,
            height=45,
            font=("Roboto Medium", 16),
            corner_radius=8,
            fg_color="#1E90FF",
            hover_color="#0066CC"
        )
        self.login_button.pack(pady=(20, 15))

        self.separator = ctk.CTkLabel(
            self.login_frame, 
            text="───────── OR ─────────",
            text_color="#A0A0A0",
            font=("Roboto", 12)
        )
        self.separator.pack(pady=10)

        self.signup_link = ctk.CTkLabel(
            self.login_frame, 
            text="Create New Account",
            cursor="hand2",
            font=("Roboto Medium", 12),
            text_color="#1E90FF"
        )
        self.signup_link.pack(pady=5)
        self.signup_link.bind("<Button-1>", lambda e: self.show_signup_frame())

        self.error_label = ctk.CTkLabel(
            self.login_frame, 
            text="",
            text_color="#FF4444",
            font=("Roboto", 12)
        )
        self.error_label.pack(pady=5)

    def create_signup_frame(self):
        self.signup_frame = ctk.CTkFrame(
            self.window, 
            corner_radius=25,
            fg_color="#363636",
            border_width=2,
            border_color="#4A4A4A"
        )
        self.signup_frame.pack_propagate(False)
        self.signup_frame.configure(width=380, height=580)

        # Signup UI Elements
        self.signup_label = ctk.CTkLabel(
            self.signup_frame, 
            text="Create Account",
            font=("Roboto Medium", 24),
            text_color="#FFFFFF"
        )
        self.signup_label.pack(pady=(40, 20))

        self.new_user_entry = ctk.CTkEntry(
            self.signup_frame,
            width=300,
            height=45,
            placeholder_text="Username",
            font=("Roboto", 14),
            border_color="#4A4A4A",
            fg_color="#2B2B2B"
        )
        self.new_user_entry.pack(pady=10)

        self.new_pass_entry = ctk.CTkEntry(
            self.signup_frame,
            width=300,
            height=45,
            show="•",
            placeholder_text="Password",
            font=("Roboto", 14),
            border_color="#4A4A4A",
            fg_color="#2B2B2B"
        )
        self.new_pass_entry.pack(pady=10)

        self.confirm_pass_entry = ctk.CTkEntry(
            self.signup_frame,
            width=300,
            height=45,
            show="•",
            placeholder_text="Confirm Password",
            font=("Roboto", 14),
            border_color="#4A4A4A",
            fg_color="#2B2B2B"
        )
        self.confirm_pass_entry.pack(pady=10)

        self.signup_button = ctk.CTkButton(
            self.signup_frame, 
            text="Sign Up",
            command=self.signup,
            width=300,
            height=45,
            font=("Roboto Medium", 16),
            corner_radius=8,
            fg_color="#1E90FF",
            hover_color="#0066CC"
        )
        self.signup_button.pack(pady=(20, 15))

        self.separator_signup = ctk.CTkLabel(
            self.signup_frame, 
            text="───────── OR ─────────",
            text_color="#A0A0A0",
            font=("Roboto", 12)
        )
        self.separator_signup.pack(pady=10)

        self.login_link = ctk.CTkLabel(
            self.signup_frame, 
            text="Already Registered? Login",
            cursor="hand2",
            font=("Roboto Medium", 12),
            text_color="#1E90FF"
        )
        self.login_link.pack(pady=5)
        self.login_link.bind("<Button-1>", lambda e: self.show_login_frame())

        self.signup_error_label = ctk.CTkLabel(
            self.signup_frame, 
            text="",
            text_color="#FF4444",
            font=("Roboto", 12)
        )
        self.signup_error_label.pack(pady=5)

    def show_login_frame(self):
        self.signup_frame.pack_forget()
        self.login_frame.pack(pady=35)
        self.window.geometry("450x650")

    def show_signup_frame(self):
        self.login_frame.pack_forget()
        self.signup_frame.pack(pady=35)
        self.window.geometry("450x650")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text="Please fill in all fields")
            return

        users = self.load_users()
        if username in users:
            if users[username]["password"] == password:
                if self.remember_me.get():
                    self.save_remembered_user(username)
                else:
                    self.delete_remembered_user()
                
                self.error_label.configure(text="")
                self.window.destroy()
                CompanyList(username).mainloop()
                return
        self.error_label.configure(text="Invalid credentials")

    def signup(self):
        username = self.new_user_entry.get()
        password = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()

        if not username or not password or not confirm_pass:
            self.signup_error_label.configure(text="Please fill in all fields")
            return

        if password != confirm_pass:
            self.signup_error_label.configure(text="Passwords don't match")
            return

        users = self.load_users()
        if username in users:
            self.signup_error_label.configure(text="Username already exists")
            return

        users[username] = {"password": password}
        self.save_users(users)

        self.signup_error_label.configure(text="Signup successful!", text_color="green")
        self.new_user_entry.delete(0, "end")
        self.new_pass_entry.delete(0, "end")
        self.confirm_pass_entry.delete(0, "end")
        self.show_login_frame()

    def load_users(self):
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}

    def save_users(self, users):
        try:
            with open(self.users_file, "w") as f:
                json.dump(users, f, indent=4)
        except Exception as e:
            print(f"Error saving users: {e}")

    def load_remembered_user(self):
        try:
            if os.path.exists(self.remember_me_file):
                with open(self.remember_me_file, "r") as f:
                    data = json.load(f)
                    return data.get("username")
            return None
        except Exception as e:
            print(f"Error loading remembered user: {e}")
            return None

    def save_remembered_user(self, username):
        try:
            data = {"username": username}
            with open(self.remember_me_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving remembered user: {e}")

    def delete_remembered_user(self):
        try:
            if os.path.exists(self.remember_me_file):
                os.remove(self.remember_me_file)
        except Exception as e:
            print(f"Error deleting remembered user: {e}")

if __name__ == "__main__":
    AuthSystem()