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
import time
from functools import partial
from configs import *
import logging

class SelectableCTkLabel(customtkinter.CTkTextbox):
    def __init__(self, master, text="", **kwargs):
        super().__init__(
            master,
            border_width=0,
            fg_color="transparent",
            wrap="word",
            insertwidth=0,  # Hide text cursor
            **kwargs
        )
        self.insert("1.0", text)
        self._setup_bindings()
        self.configure(state="normal")  # Allow text selection

    def _setup_bindings(self):
        # Block regular keyboard input
        self.bind("<Key>", self._block_input)

        # Add Ctrl+C copy functionality
        self._textbox.bind("<Control-c>", self._copy_selection)

        # For macOS users (Command+C instead of Control+C)
        # self._textbox.bind("<Command-c>", self._copy_selection)

    def _block_input(self, event):
        """Allow only Ctrl+C to pass through"""
        if not (event.state & 0x4 and event.keysym.lower() == 'c'):
            return "break"

    def _copy_selection(self, event=None):
        """Copy selected text to clipboard"""
        if self._textbox.tag_ranges("sel"):
            # Get selected text from underlying Tkinter widget
            start = self._textbox.index("sel.first")
            end = self._textbox.index("sel.last")
            selected_text = self._textbox.get(start, end)

            # Update clipboard
            self.master.clipboard_clear()
            self.master.clipboard_append(selected_text)
        return "break"


class CompanyApp(customtkinter.CTk):

    def __init__(self ,master ,company_name , user):
        super().__init__()
        self.master = master
        self.file_path = "contacts.json"
        self.data = []
        self.config_path = os.path.join(os.path.expanduser("~"), "company_manager_config.json")

        

        self.user = user
        self.company_name = company_name

        logging.basicConfig(
            filename='app_errors.log',
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        if not os.path.exists(self.config_path):
            self.create_default_config()
            
        self.load_config()
        self.editing_index = -1

        # Configure window
        self.title("Contacts")
        self.geometry("1200x800")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        # 3CX configuration
        # self.process_name_phone = process_name_phone
        # self.window_title_phone = window_title_phone
        # self.executable_path_phone = executable_path_phone

        self.process_name_phone = self.config["phone"]["process_name"]
        self.window_title_phone = self.config["phone"]["window_title"]
        self.executable_path_phone = self.config["phone"]["executable_path"]

        # self.process_name_anydesk = process_name_anydesk
        # self.window_title_anydesk = window_title_anydesk
        # self.executable_path_anydesk = executable_path_anydesk

        
        self.process_name_anydesk = self.config["anydesk"]["process_name"]
        self.window_title_anydesk = self.config["anydesk"]["window_title"]
        self.executable_path_anydesk = self.config["anydesk"]["executable_path"]


        # Font configuration
        self.farsi_font = customtkinter.CTkFont(family="Tahoma", size=14)

        # Column configuration (updated for Call button)
        self.column_weights = [1, 6, 4, 4, 2, 2]
        self.column_widths = [50, 300, 150, 150, 100 ,100]

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
        #Back to Person list
        back_btn = customtkinter.CTkButton(
            self,
            text="← Back to List",
            command=self.go_back,
            fg_color="transparent",
            hover_color="#444444"
        )
        back_btn.pack(anchor="nw", padx=10, pady=10)

        # Search Section
        search_frame = customtkinter.CTkFrame(self.main_frame)
        search_frame.pack(fill="x", padx=10, pady=10)

        self.search_entry = customtkinter.CTkEntry(
            search_frame,
            placeholder_text="Search..",
            width=800
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.search_person)

        # Input Section
        input_frame = customtkinter.CTkFrame(self.main_frame)
        input_frame.pack(fill="x", padx=10, pady=10)

        # Person Name
        self.name_entry = customtkinter.CTkEntry(
            input_frame,
            placeholder_text="Person Name",
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

        # Phone Number
        self.phone_entry = customtkinter.CTkEntry(
            input_frame,
            placeholder_text="Phone Number",
            width=150
        )
        self.phone_entry.grid(row=0, column=2, padx=5, pady=5)

        # Buttons
        button_frame = customtkinter.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.add_button = customtkinter.CTkButton(
            button_frame,
            text="Add Person ➕",
            command=self.add_person,
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            text_color='black',
            width=120
        )
        self.add_button.grid(row=0, column=0, padx=5)

        self.edit_button = customtkinter.CTkButton(
            button_frame,
            text="Edit Selected 🔄",
            command=self.enable_edit_mode,
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            text_color='black',
            width=120,
            fg_color="#f0ad4e"
        )
        self.edit_button.grid(row=0, column=1, padx=5)

        self.delete_button = customtkinter.CTkButton(
            button_frame,
            text="Delete Selected 🗑️",
            command=self.delete_person,
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            text_color='black',
            fg_color="#d9534f",
            width=120
        )
        self.delete_button.grid(row=0, column=2, padx=5)

        self.config_button = customtkinter.CTkButton(
            button_frame,
            text="Edit Config ✏️",
            command=self.open_config_file,
            font=("Segoe UI Emoji", 14),
            hover_color="#A5D6A7",
            text_color='black',
            width=120,
            fg_color="#5bc0de"
        )
        self.config_button.grid(row=0, column=3, padx=5)

        # Table Section
        list_container = customtkinter.CTkFrame(self.main_frame)
        list_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        self.header_frame = customtkinter.CTkFrame(list_container)
        self.header_frame.pack(fill="x", pady=(0, 5))

        for col, weight in enumerate(self.column_weights):
            self.header_frame.grid_columnconfigure(col, weight=weight, uniform="cols")

        columns = ["Select", "Person Name", "Remote", "Phone", "Call" ,"Remote"]
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


    def go_back(self):
        # Destroy current app window
        self.destroy()
        # Show the parent CompanyList window
        self.master.deiconify()


    def add_person(self):
        name = self.name_entry.get().strip()
        ip = self.ip_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not all([name, ip, phone]):
            self.show_error("All fields are required!")
            return

        # Create new person dictionary
        new_person = {
            "name": name,
            "ip": ip,
            "phone": phone,
        }

        # Check for duplicates
        if any(p == new_person for p in self.data):
            self.show_error("This person already exists!")
            return

        try:
            if self.editing_index != -1:
                # Update existing entry
                self.data[self.editing_index] = new_person
                self.cancel_edit()
            else:
                # Add new entry (no duplicate)
                self.data.append(new_person)
        except AttributeError:
            self.data.append(new_person)

        self.save_to_file()
        self.clear_entries()
        self.refresh_display()


    def delete_person(self):
        selected_idx = self.radio_var.get()
        if selected_idx == -1:
            self.show_error("No person selected!")
            return

        try:
            query = self.search_entry.get()
            conditions = self.parse_search_query(query)
            filtered_indices = [
                i for i, person in enumerate(self.data)
                if self.matches_conditions(person, conditions)
            ]

            if selected_idx < len(filtered_indices):
                del self.data[filtered_indices[selected_idx]]
                self.radio_var.set(-1)
                self.save_to_file()
                self.refresh_display()
        except IndexError:
            self.show_error("Invalid selection!")


    def search_person(self, event=None):
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


    def matches_conditions(self, person, conditions):
        for field, value in conditions:
            if field == 'global':
                search_values = [
                    person['name'].lower(),
                    person['ip'],
                    person['phone']
                ]
                if not any(value.lower() in val.lower() for val in search_values):
                    return False
            elif field == 'name':
                if value.lower() not in person['name'].lower():
                    return False
            elif field == 'ip':
                if not re.match(value.replace('*', '.*'), person['ip']):
                    return False
            elif field == 'phone':
                if value not in person['phone']:
                    return False
        return True


    def refresh_display(self):

        self.rows.clear()

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame._parent_canvas.yview_moveto(0.0)
        self.radio_var.set(-1)

        query = self.search_entry.get()
        conditions = self.parse_search_query(query)
        filtered_data = [c for c in self.data if self.matches_conditions(c, conditions)]

        for idx, person in enumerate(filtered_data):
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

            # person name
            customtkinter.CTkLabel(
                entry_frame,
                text=person['name'],
                width=self.column_widths[1],
                anchor="w",
                font=self.farsi_font,
                state="disabled",
            ).grid(row=0, column=1, padx=5, sticky="w")

            # IP Address (copyable)
            ip_label = customtkinter.CTkLabel(
                entry_frame,
                text=person['ip'],
                width=self.column_widths[2],
                anchor="w",
                cursor="hand2"
            )
            ip_label.grid(row=0, column=2, padx=5, sticky="w")
            ip_label.bind(
                "<Button-1>",
                lambda e, t=person['ip']: self.copy_to_clipboard(e, t)  # Pass event + text
            )

            # Phone Number (copyable)
            phone_label = customtkinter.CTkLabel(
                entry_frame,
                text=person['phone'],
                width=self.column_widths[3],
                anchor="w",
                cursor="hand2"
            )
            phone_label.grid(row=0, column=3, padx=5, sticky="w")
            phone_label.bind(
                "<Button-1>",
                lambda e, t=person['phone']: self.copy_to_clipboard(e, t)  # Pass event + text
            )

            # Call button
            call_btn = customtkinter.CTkButton(
                entry_frame,
                text="Call",
                width=self.column_widths[5],
                fg_color="#5cb85c",
                hover_color="#626F47",
                command=partial(self.dial_number, person['phone'])
            )
            call_btn.grid(row=0, column=5, padx=5, sticky="w")

            #Remote button
            remote_btn = customtkinter.CTkButton(
                entry_frame,
                text="Remote",
                width=self.column_widths[5],
                fg_color="#C5172E",
                hover_color="#85193C",
                command=partial(self. connect_remote, person['ip'])
            )
            remote_btn.grid(row=0, column=6, padx=5, sticky="w")

        self.update_row_highlight()


    def validate_ip(self, ip):
        pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return re.match(pattern, ip) is not None


    def dial_number(self, phone_number):
        try:
            # Check if 3CX is running
            is_running = any(p.name() == self.process_name_phone
                             for p in psutil.process_iter(['pid', 'name']))

            if not is_running:
                subprocess.Popen([self.executable_path_phone])
                time.sleep(5)
                self.bring_to_front("3CXPhone")
            else:
                if not self.bring_to_front("3CXPhone"):
                    return "could not find 3CX phone"

            # Bring 3CX window to focus
            time.sleep(1)

            try:
                win = gw.getWindowsWithTitle(self.window_title_phone)[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.5)
            except IndexError:
                self.show_error("3CX window not found")
                return

            # Send keystrokes
            pyautogui.hotkey('shift', 'insert')
            pyautogui.write(f'9{phone_number}')
            pyautogui.press('enter')

            # self.clear_entries()
            # self.refresh_display()


        except Exception as e:
            self.show_error(f"Dialing failed: {str(e)}")


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
        self.phone_entry.delete(0, tkinter.END)
        try:
            if self.editing_index != -1:
                self.cancel_edit()
        except AttributeError:
            pass


    def show_error(self, message):
        error_dialog = customtkinter.CTkToplevel(self)
        error_dialog.title("Error")
        error_dialog.geometry("300x100")
        customtkinter.CTkLabel(error_dialog, text=message).pack(pady=20)
        customtkinter.CTkButton(error_dialog, text="OK", command=error_dialog.destroy).pack()


    def load_from_file(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    for company in data:
                        if x:=company.get(self.company_name , None):
                            self.data = x
            except Exception as e:
                self.show_error(f"Error loading data: {str(e)}")


    def save_to_file(self):
        try:
            # Load all existing companies from the file
            all_companies = []
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as file:
                    all_companies = json.load(file)
            
            # Check if the current company exists in the data
            company_exists = False
            for company in all_companies:
                if self.company_name in company:
                    # Update the contacts for the current company
                    company[self.company_name] = self.data
                    company_exists = True
                    break
            
            # If the company doesn't exist, add it to the list
            if not company_exists:
                all_companies.append({self.company_name: self.data})
            
            # Save the updated data back to the file
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(all_companies, file, indent=4, ensure_ascii=False)
        except Exception as e:
            self.show_error(f"Error saving data: {str(e)}")


    def enable_edit_mode(self):
        selected_idx = self.radio_var.get()
        if selected_idx == -1:
            self.show_error("Please select a person to edit!")
            return

        try:
            query = self.search_entry.get()
            conditions = self.parse_search_query(query)
            filtered_indices = [
                i for i, person in enumerate(self.data)
                if self.matches_conditions(person, conditions)
            ]

            if selected_idx < len(filtered_indices):
                self.editing_index = filtered_indices[selected_idx]
                person = self.data[self.editing_index]

                # Fill fields with existing data
                self.name_entry.delete(0, tkinter.END)
                self.name_entry.insert(0, person['name'])
                self.ip_entry.delete(0, tkinter.END)
                self.ip_entry.insert(0, person['ip'])
                self.phone_entry.delete(0, tkinter.END)
                self.phone_entry.insert(0, person['phone'])

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

if __name__ == "__main__":
    app = CompanyApp()
    # app.iconbitmap("icon.ico")
    app.mainloop()