import customtkinter
import tkinter
import json
import os
import re
import psutil
import subprocess
import pyautogui
import pygetwindow as gw
import win32gui
import win32con
import logging
import time
from functools import partial
from Report import WorkReportApp
from configs import *
from contacts import CompanyApp
from reminder import ReliableReminderApp
from todo import ToDoUI


class CompanyList(customtkinter.CTk):

    def __init__(self ,user=''):
        super().__init__()
        self.file_path = "companies_list.json"
        self.data = []
        self.config_path = os.path.join(os.path.expanduser("~"), "company_manager_config.json")

        # self.attributes("-fullscreen", True)

        self.user = user

        logging.basicConfig(
            filename='app_errors.log',
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        if not os.path.exists(self.config_path):
            self.create_default_config()
            
        self.load_config()

        # Configure window
        self.title("Company List")
        self.geometry("1200x800")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        
        self.process_name_anydesk = self.config["anydesk"]["process_name"]
        self.window_title_anydesk = self.config["anydesk"]["window_title"]
        self.executable_path_anydesk = self.config["anydesk"]["executable_path"]


        # Font configuration
        self.farsi_font = customtkinter.CTkFont(family="Tahoma", size=14)

        # Column configuration (updated for Call button)
        # select , company , remote ,moadian , is_dorsan , remote_btn , contacts_btn
        self.column_weights = [1, 6, 4, 4, 2 , 2, 2]
        self.column_widths = [50, 300, 150, 150, 80 ,100 ,100]

        # Main container
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.radio_var = tkinter.IntVar(value=-1)  # Create variable here
        self.rows = []

        # self.create_widgets()

        self.radio_var.trace_add("write", self.update_row_highlight)

        self.create_widgets()
        # self.create_widgets_company()
        self.load_from_file()
        self.refresh_display()


    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
        except Exception as e:
            self.show_error(f"Error loading config: {str(e)}")
            self.create_default_config()


    def create_default_config(self):
        default_config = {
            "phone": {
                "process_name": "3CXPhone.exe",
                "window_title": "3CX",
                "executable_path": "E:\\share\\3CXPhone\\3CXPhone.exe"
            },
            "anydesk": {
                "process_name": "Anydesk.exe",
                "window_title": "Anydesk",
                "executable_path": "C:\\Path\\To\\AnyDesk.exe"
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        self.config = default_config


    def create_widgets(self):
        # Search Section
        search_frame = customtkinter.CTkFrame(self.main_frame)
        search_frame.pack(fill="x", padx=10, pady=10)

        self.search_entry = customtkinter.CTkEntry(
            search_frame,
            placeholder_text="Search..",
            width=800
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.search_companies)

        # Input Section
        input_frame = customtkinter.CTkFrame(self.main_frame)
        input_frame.pack(fill="x", padx=10, pady=10)

        # Company Name
        self.name_entry = customtkinter.CTkEntry(
            input_frame,
            placeholder_text="Company Name",
            width=250,
            font=self.farsi_font
        )
        self.name_entry.grid(row=0, column=0, padx=5, pady=5)

        # IP Address
        self.ip_entry = customtkinter.CTkEntry(
            input_frame,
            placeholder_text="Remote",
            width=150
        )
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        # moadian
        self.moadian_entry = customtkinter.CTkEntry(
            input_frame,
            placeholder_text="moadian",
            width=150
        )
        self.moadian_entry.grid(row=0, column=2, padx=5, pady=5)

        # is_dorsan Checkbox
        self.is_dorsan_var = tkinter.IntVar(value=0)
        self.is_dorsan_check = customtkinter.CTkCheckBox(
            input_frame,
            text="Is Dorsan",
            variable=self.is_dorsan_var
        )
        self.is_dorsan_check.grid(row=0, column=3, padx=5, pady=5)

        # Buttons
        button_frame = customtkinter.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.add_button = customtkinter.CTkButton(
            button_frame,
            text="Add Company ➕",
            command=self.add_company,
            text_color='black',
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            width=120
        )
        self.add_button.grid(row=0, column=0, padx=5)

        self.edit_button = customtkinter.CTkButton(
            button_frame,
            text="Edit Selected 🔄",
            command=self.enable_edit_mode,
            width=120,
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            text_color='black',
            fg_color="#f0ad4e"
        )
        self.edit_button.grid(row=0, column=1, padx=5)

        self.delete_button = customtkinter.CTkButton(
            button_frame,
            text="Delete Selected 🗑️",
            command=self.delete_company,
            fg_color="#d9534f",
            font=("Segoe UI Emoji", 14),
            text_color='black',
            hover_color="#A5D6A7",
            width=120
        )
        self.delete_button.grid(row=0, column=2, padx=5)

        self.config_button = customtkinter.CTkButton(
            button_frame,
            text="Edit Config ✏️",
            command=self.open_config_file,
            width=120,
            text_color='black',
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            fg_color="#5bc0de"
        )
        self.config_button.grid(row=0, column=3, padx=5)

        self.report_button = customtkinter.CTkButton(
            button_frame,
            text="Report 📝",
            command=self.open_report,
            width=120,
            text_color='black',
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            fg_color="#c45bde"
        )
        self.report_button.grid(row=0, column=4, padx=5)

        self.reminder_button = customtkinter.CTkButton(
            button_frame,
            text="Alarm 🚨",
            command=self.open_reminder,
            width=120,
            text_color='black',
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            fg_color="#B03052"
        )
        self.reminder_button.grid(row=0, column=5, padx=5)

        self.todo_btn = customtkinter.CTkButton(
            button_frame,
            text="Todo ✅ ",
            command=self.open_todo,
            width=120,
            text_color='black',
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            fg_color="#05C95D"
        )
        self.todo_btn.grid(row=0, column=6, padx=5)

        # Table Section
        list_container = customtkinter.CTkFrame(self.main_frame)
        list_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        self.header_frame = customtkinter.CTkFrame(list_container)
        self.header_frame.pack(fill="x", pady=(0, 5))

        for col, weight in enumerate(self.column_weights):
            self.header_frame.grid_columnconfigure(col, weight=weight, uniform="cols")

        columns = ["Select", "Company Name", "Remote", "Moadian", "Is Dorsan", "Contacts" ,"Remote"]
        for col, (text, width) in enumerate(zip(columns, self.column_widths)):
            customtkinter.CTkLabel(
                self.header_frame,
                text=text,
                width=width,
                anchor="w",
                font=customtkinter.CTkFont(weight="bold"),
                state="disabled"
            ).grid(row=0, column=col, padx=5, sticky="ew")

        customtkinter.CTkFrame(self.header_frame, height=2, fg_color="gray30").grid(
            row=1, column=0, columnspan=len(columns), sticky="ew")

        # Table Body
        self.scrollable_frame = customtkinter.CTkScrollableFrame(list_container)
        self.scrollable_frame.pack(fill="both", expand=True)

        for col, weight in enumerate(self.column_weights):
            self.scrollable_frame.grid_columnconfigure(col, weight=weight, uniform="cols")


        # Radio button variable
        self.radio_var = tkinter.IntVar(value=-1)


    def update_row_highlight(self, *args):
        selected_idx = self.radio_var.get()
        for idx, row_frame in enumerate(self.rows):
            if idx == selected_idx:
                # Use theme-aware colors
                row_frame.configure(fg_color=("gray70", "gray30"))
            else:
                row_frame.configure(fg_color="transparent")
        # Force update the scrollable frame
        self.scrollable_frame.update_idletasks()
    

    def add_company(self):
        name = self.name_entry.get().strip()
        ip = self.ip_entry.get().strip()
        moadian = self.moadian_entry.get().strip()
        is_dorsan = self.is_dorsan_var.get()

        if not all([name, ip, moadian]):
            self.show_error("All fields are required!")
            return

        # if not self.validate_ip(ip):
        #     self.show_error("Invalid IP address format!")
        #     return
        try :
            if self.editing_index != -1:
                # Update existing entry
                self.data[self.editing_index] = {
                    "name": name,
                    "ip": ip,
                    "moadian": moadian,
                    "is_dorsan": is_dorsan
                }
                self.cancel_edit()
            else:
                # Add new entry
                self.data.append({
                    "name": name,
                    "ip": ip,
                    "moadian": moadian,
                    "is_dorsan": is_dorsan
                })
        except AttributeError:
            self.data.append({
                "name": name,
                "ip": ip,
                "moadian": moadian,
                "is_dorsan": is_dorsan
            })

        self.save_to_file()
        self.clear_entries()
        self.refresh_display()


    def delete_company(self):
        selected_idx = self.radio_var.get()
        if selected_idx == -1:
            self.show_error("No company selected!")
            return

        try:
            query = self.search_entry.get()
            conditions = self.parse_search_query(query)
            filtered_indices = [
                i for i, company in enumerate(self.data)
                if self.matches_conditions(company, conditions)
            ]

            if selected_idx < len(filtered_indices):
                del self.data[filtered_indices[selected_idx]]
                self.radio_var.set(-1)
                self.save_to_file()
                self.refresh_display()
        except IndexError:
            self.show_error("Invalid selection!")


    def search_companies(self, event=None):
        self.refresh_display()


    def parse_search_query(self, query):
        conditions = []
        for part in query.split(','):
            part = part.strip()
            if ':' in part:
                field, value = part.split(':', 1)
                field = field.strip().lower()
                value = value.strip()
                conditions.append((field, value))
            else:
                conditions.append(('global', part.strip()))
        return conditions


    def matches_conditions(self, company, conditions):
        for field, value in conditions:
            if field == 'global':
                search_values = [
                    company['name'].lower(),
                    company['ip'],
                    company['moadian'],
                    str(company['is_dorsan'])
                ]
                if not any(value.lower() in val.lower() for val in search_values):
                    return False
            elif field == 'name':
                if value.lower() not in company['name'].lower():
                    return False
            elif field == 'ip':
                if not re.match(value.replace('*', '.*'), company['ip']):
                    return False
            elif field == 'moadian':
                if value not in company['moadian']:
                    return False
            elif field == 'is_dorsan':
                if str(company.get('is_dorsan', 0)) != value:
                    return False
        return True


    def refresh_display(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.rows = []

        query = self.search_entry.get()
        conditions = self.parse_search_query(query)
        filtered_data = [c for c in self.data if self.matches_conditions(c, conditions)]

        for idx, company in enumerate(filtered_data):
            entry_frame = customtkinter.CTkFrame(self.scrollable_frame)
            entry_frame.pack(fill="x", pady=2)

            for col, (weight, width) in enumerate(zip(self.column_weights, self.column_widths)):
                entry_frame.grid_columnconfigure(col, weight=weight, uniform="cols")

            self.rows.append(entry_frame)
            entry_frame.bind("<Button-1>", lambda e, idx=idx: self.radio_var.set(idx))

            # Radio button
            customtkinter.CTkRadioButton(
                entry_frame,
                text="",
                variable=self.radio_var,
                value=idx,
                width=self.column_widths[0],
                command=lambda v=idx: (self.radio_var.set(v), self.update_row_highlight())
            ).grid(row=0, column=0, padx=5, sticky="w")

            # Company name
            customtkinter.CTkLabel(
                entry_frame,
                text=company['name'],
                width=self.column_widths[1],
                anchor="w",
                font=self.farsi_font,
                state="disabled",
            ).grid(row=0, column=1, padx=5, sticky="w")

            # IP Address (copyable)
            ip_label = customtkinter.CTkLabel(
                entry_frame,
                text=company['ip'],
                width=self.column_widths[2],
                anchor="w",
                cursor="hand2"
            )
            ip_label.grid(row=0, column=2, padx=5, sticky="w")
            ip_label.bind(
                "<Button-1>",
                lambda e, t=company['ip']: self.copy_to_clipboard(e, t)  # Pass event + text
            )

            # Phone Number (copyable)
            moadian = customtkinter.CTkLabel(
                entry_frame,
                text=company['moadian'],
                width=self.column_widths[3],
                anchor="w",
                cursor="hand2"
            )
            moadian.grid(row=0, column=3, padx=5, sticky="w")
            moadian.bind(
                "<Button-1>",
                lambda e, t=company['moadian']: self.copy_to_clipboard(e, t)  # Pass event + text
            )

            status = "✅" if company.get('is_dorsan', 0) else "❌"
            customtkinter.CTkLabel(
                entry_frame,
                text=status,
                width=self.column_widths[4],
                anchor="center"
            ).grid(row=0, column=4, padx=5)

            # Call button
            Contacts = customtkinter.CTkButton(
                entry_frame,
                text="Contacts",
                width=self.column_widths[5],
                fg_color="#5cb85c",
                hover_color="#626F47",
                command=partial(self.show_contacts, company['name'])
            )
            Contacts.grid(row=0, column=5, padx=5, sticky="w")

            #Remote button
            remote_btn = customtkinter.CTkButton(
                entry_frame,
                text="Remote",
                width=self.column_widths[5],
                fg_color="#C5172E",
                hover_color="#85193C",
                command=partial(self. connect_remote, company['ip'])
            )
            remote_btn.grid(row=0, column=6, padx=5, sticky="w")

        self.update_row_highlight()

    
    def show_contacts(self,company_name):
        # Hide current window
        self.withdraw()
        
        # Create CompanyApp instance with parameters
        CompanyApp(self, company_name, self.user).mainloop()


    def validate_ip(self, ip):
        pattern = r"^\s*((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\s*\.\s*){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\s*$"
        return re.match(pattern, ip) is not None


    def connect_remote(self , address):
        if '.' in address:
            subprocess.Popen(['mstsc', f'/v:{address}'])
        else:
            try:
                is_running = any(p.name() == self.process_name_anydesk
                                 for p in psutil.process_iter(['pid', 'name']))

                if not is_running:
                    subprocess.Popen([self.executable_path_anydesk])
                    time.sleep(5)
                    self.bring_to_front("Anydesk")
                else:
                    if not self.bring_to_front("Anydesk"):
                        return "could not find Anydesk phone"
                #Bring anydesk window to focus
                time.sleep(1)
                try:
                    win = gw.getWindowsWithTitle(self.window_title_anydesk)[0]
                    if win.isMinimized:
                        win.restore()
                    win.activate()
                    time.sleep(0.5)
                except IndexError:
                    self.show_error("anydesk window not found")
                    return

                # Send keystrokes
                pyautogui.hotkey('space')
                pyautogui.hotkey('backspace')
                pyautogui.write(f'{address}')
                pyautogui.press('enter')

            except Exception as e:
                print(str(e))


    def clear_entries(self):
        self.name_entry.delete(0, tkinter.END)
        self.ip_entry.delete(0, tkinter.END)
        self.moadian_entry.delete(0, tkinter.END)
        self.is_dorsan_var.set(0)
        try:
            if self.editing_index != -1:
                self.cancel_edit()
        except AttributeError:
            pass


    def show_error(self, message):
        """Display styled error dialog and log the error"""
        try:
            # Log the error
            logging.error(f"UI Error: {message}")
            
            # Create error dialog
            error_dialog = customtkinter.CTkToplevel(self)
            error_dialog.title("Error")
            error_dialog.geometry("400x150")
            error_dialog.resizable(False, False)
            
            # Center the dialog
            self._center_window(error_dialog)
            
            # Set icon (if available)
            try:
                error_dialog.iconbitmap("error_icon.ico")  # Add your icon file
            except Exception as e:
                logging.warning(f"Error icon not found: {str(e)}")

            # Configure grid layout
            error_dialog.grid_columnconfigure(0, weight=1)
            error_dialog.grid_rowconfigure(0, weight=1)

            # Error content
            content_frame = customtkinter.CTkFrame(error_dialog)
            content_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

            # Error message with icon
            customtkinter.CTkLabel(content_frame, 
                        text=" ⚠️ ",  # You can use emoji or custom image
                        font=("Arial", 24)).pack(side="left", padx=10)
            customtkinter.CTkLabel(content_frame, 
                        text=message,
                        font=("Arial", 14),
                        wraplength=300).pack(side="left", expand=True, fill="both")

            # OK button
            button_frame = customtkinter.CTkFrame(error_dialog, fg_color="transparent")
            button_frame.grid(row=1, column=0, pady=10)
            customtkinter.CTkButton(button_frame,
                         text="OK",
                         command=error_dialog.destroy,
                         width=100,
                         fg_color="#ff4444",  # Red color for error button
                         hover_color="#cc0000").pack()

            # Make dialog modal
            error_dialog.grab_set()
            error_dialog.attributes('-topmost', True)
            error_dialog.protocol("WM_DELETE_WINDOW", error_dialog.destroy)

        except Exception as e:
            logging.critical(f"Error displaying error dialog: {str(e)}")


    def _center_window(self, window):
        """Center the window relative to parent"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')


    def load_from_file(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    self.data = json.load(file)
            except Exception as e:
                self.show_error(f"Error loading data: {str(e)}")


    def save_to_file(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            self.show_error(f"Error saving data: {str(e)}")


    def enable_edit_mode(self):
        selected_idx = self.radio_var.get()
        if selected_idx == -1:
            self.show_error("Please select a company to edit!")
            return

        try:
            query = self.search_entry.get()
            conditions = self.parse_search_query(query)
            filtered_indices = [
                i for i, company in enumerate(self.data)
                if self.matches_conditions(company, conditions)
            ]

            if selected_idx < len(filtered_indices):
                self.editing_index = filtered_indices[selected_idx]
                company = self.data[self.editing_index]

                # Fill fields with existing data
                self.name_entry.delete(0, tkinter.END)
                self.name_entry.insert(0, company['name'])
                self.ip_entry.delete(0, tkinter.END)
                self.ip_entry.insert(0, company['ip'])
                self.moadian.delete(0, tkinter.END)
                self.moadian.insert(0, company['phone'])
                self.is_dorsan_var.set(company.get('is_dorsan', 0))

                # Change add button to update
                self.add_button.configure(text="Update Company")
        except IndexError:
            self.show_error("Invalid selection for editing!")


    def cancel_edit(self):
        self.editing_index = -1
        self.clear_entries()
        self.add_button.configure(text="Add Company")

    @staticmethod
    def bring_to_front(window_title_phone):
        """Bring window to front using window title"""

        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd) and window_title_phone.lower() in win32gui.GetWindowText(hwnd).lower():
                extra.append(hwnd)

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)

        if hwnds:
            hwnd = hwnds[0]
            # Restore if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # Bring to front
            win32gui.SetForegroundWindow(hwnd)
            return True
        return False

    def copy_to_clipboard(self, event, text):
        # Get root window from the clicked widget
        root = event.widget.winfo_toplevel()

        # Update clipboard
        root.clipboard_clear()
        root.clipboard_append(text)

        # Optional visual feedback (you could flash the label)
        print(f"Copied to clipboard: {text}")

    def open_config_file(self):
        if os.name == 'nt':  # Windows
            os.startfile(self.config_path)
        else:  # Mac/Linux
            subprocess.run(["xdg-open", self.config_path])

    def open_report(self):
        self.withdraw()

        # Create CompanyApp instance with parameters
        WorkReportApp(self).mainloop()

    def open_reminder(self):
        self.withdraw()
        ReliableReminderApp(self).mainloop()

    def open_todo(self):
        current_theme = customtkinter.get_appearance_mode()

        self.withdraw()
        root_todo = customtkinter.CTk()
        app_todo = ToDoUI(root_todo, master=self, original_theme=current_theme)
        root_todo.mainloop()

if __name__ == "__main__":
    app = CompanyList()
    # app.iconbitmap("icon.ico")
    app.mainloop()