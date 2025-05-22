import customtkinter as ctk
import json
from datetime import datetime
import tkinter.messagebox as messagebox

class ToDoItem:
    def __init__(self, description, due_date=None, priority="Medium", tags=None, completed=False):
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.tags = tags if tags else []
        self.completed = completed

    def to_dict(self):
        return {
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "tags": self.tags,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            description=data["description"],
            due_date=data.get("due_date"),
            priority=data.get("priority", "Medium"),
            tags=data.get("tags", []),
            completed=data.get("completed", False)
        )

class ToDoList:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]

    def mark_completed(self, index):
        if 0 <= index < len(self.items):
            self.items[index].completed = True

    def to_json(self):
        return json.dumps([item.to_dict() for item in self.items], indent=4)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        todo_list = cls()
        for item_data in data:
            todo_list.add_item(ToDoItem.from_dict(item_data))
        return todo_list

class ToDoUI:
    def __init__(self, root , master = None , original_theme=None):
        self.root = root
        self.root.title("🌟 Enhanced To-Do List")
        self.root.geometry("900x700")
        self.original_theme = original_theme
        self.master = master
        self.todo_list = ToDoList()
        self.current_theme = "light"
        self.setup_ui()
        self.load_data()

    def go_back(self):
        ctk.set_appearance_mode(self.original_theme)
        # Close the ToDo window
        self.root.destroy()
        # Show parent window
        self.master.deiconify()
    
    def setup_ui(self):
        ctk.set_appearance_mode("light")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        sidebar_title = ctk.CTkLabel(self.sidebar, text="📋 Menu", font=("Arial", 20, "bold"))
        sidebar_title.pack(pady=20)

        self.all_tasks_btn = ctk.CTkButton(self.sidebar, text="📜 All Tasks", command=self.show_all_tasks, corner_radius=8)
        self.all_tasks_btn.pack(pady=10, padx=20, fill="x")

        self.today_btn = ctk.CTkButton(self.sidebar, text="📅 Today’s Tasks", command=self.show_today_tasks, corner_radius=8)
        self.today_btn.pack(pady=10, padx=20, fill="x")

        self.completed_btn = ctk.CTkButton(self.sidebar, text="✅ Done", command=self.show_completed_tasks, corner_radius=8)
        self.completed_btn.pack(pady=10, padx=20, fill="x")

        self.calendar_btn = ctk.CTkButton(self.sidebar, text="🗓️ Calendar", command=self.show_calendar_view, corner_radius=8)
        self.calendar_btn.pack(pady=10, padx=20, fill="x")

        self.theme_btn = ctk.CTkButton(self.sidebar, text="🌙 Theme Switch", command=self.switch_theme, corner_radius=8)
        self.theme_btn.pack(pady=10, padx=20, fill="x")

        # Main content area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Header with Search
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.pack(fill="x", pady=10)

        self.header = ctk.CTkLabel(self.header_frame, text="✨ My To-Do List", font=("Arial", 28, "bold"))
        self.header.pack(side="left", padx=10)

        self.search_entry = ctk.CTkEntry(self.header_frame, placeholder_text="🔍 Search tasks...", width=300)
        self.search_entry.pack(side="right", padx=10)
        self.search_entry.bind("<KeyRelease>", self.search_tasks)

        # Task display area with scrollbar
        self.task_container = ctk.CTkScrollableFrame(self.main_frame)
        self.task_container.pack(fill="both", expand=True)

        # Floating Add Task button
        self.add_task_btn = ctk.CTkButton(self.main_frame, text="➕ Add a Task", command=self.open_add_task_window, 
                                         corner_radius=20, width=150, height=40)
        self.add_task_btn.pack(pady=15)

        self.add_task_btn_back = ctk.CTkButton(
            self.main_frame,
            text="← Back to List",
            command=self.go_back,
            fg_color="#393E46",
            hover_color="#444444"
        )
        self.add_task_btn_back.pack(pady=25)

        # Bind close event to save data
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_all_tasks(self):
        self.display_tasks(self.todo_list.items)

    def show_today_tasks(self):
        today = datetime.now().strftime("%Y-%m-%d")
        today_tasks = [item for item in self.todo_list.items if item.due_date == today]
        self.display_tasks(today_tasks)

    def show_completed_tasks(self):
        completed_tasks = [item for item in self.todo_list.items if item.completed]
        self.display_tasks(completed_tasks)

    def show_calendar_view(self):
        # Placeholder for calendar view
        messagebox.showinfo("Calendar View", "Calendar view coming soon!")

    def search_tasks(self, event):
        query = self.search_entry.get().lower()
        filtered_tasks = [item for item in self.todo_list.items if query in item.description.lower() or any(query in tag.lower() for tag in item.tags)]
        self.display_tasks(filtered_tasks)

    def display_tasks(self, tasks):
        for widget in self.task_container.winfo_children():
            widget.destroy()

        for idx, task in enumerate(tasks):
            border_color = self.get_priority_color(task.priority)
            task_card = ctk.CTkFrame(self.task_container, corner_radius=10, border_width=2, border_color=border_color)
            task_card.pack(fill="x", pady=5, padx=5)

            desc_color = "gray" if task.completed else "black"
            description_label = ctk.CTkLabel(task_card, text=f"📝 {task.description}", font=("Arial", 16), text_color=desc_color)
            description_label.pack(side="left", padx=10, pady=5)

            due_label = ctk.CTkLabel(task_card, text=f"⏰ Due: {task.due_date or 'N/A'}", font=("Arial", 12))
            due_label.pack(side="left", padx=10)

            priority_label = ctk.CTkLabel(task_card, text=f"⚡ {task.priority}", font=("Arial", 12))
            priority_label.pack(side="left", padx=10)

            tags_label = ctk.CTkLabel(task_card, text=f"🏷️ {', '.join(task.tags) if task.tags else 'No tags'}", font=("Arial", 12))
            tags_label.pack(side="left", padx=10)

            status_label = ctk.CTkLabel(task_card, text="✅" if task.completed else "⭕", font=("Arial", 16))
            status_label.pack(side="left", padx=10)

            complete_btn = ctk.CTkButton(task_card, text="✅ Mark Done", command=lambda i=idx: self.mark_completed(i), 
                                        width=80, corner_radius=5)
            complete_btn.pack(side="right", padx=5)

            remove_btn = ctk.CTkButton(task_card, text="🗑️ Remove", command=lambda i=idx: self.remove_item(i), 
                                      width=80, corner_radius=5)
            remove_btn.pack(side="right", padx=5)

    def get_priority_color(self, priority):
        if priority == "Low":
            return "green"
        elif priority == "Medium":
            return "yellow"
        elif priority == "High":
            return "red"
        return "gray"

    def open_add_task_window(self):
        add_window = ctk.CTkToplevel(self.root)
        add_window.title("✨ Add a New Task")
        add_window.geometry("500x500")
        add_window.transient(self.root)
        add_window.grab_set()

        # Title
        title_label = ctk.CTkLabel(add_window, text="✨ Add a New Task", font=("Arial", 24, "bold"))
        title_label.pack(pady=20)

        # Description
        ctk.CTkLabel(add_window, text="📝 Task Description:").pack(pady=5)
        desc_entry = ctk.CTkEntry(add_window, width=400, placeholder_text="What do you need to do?")
        desc_entry.pack(pady=5)

        # Error label
        error_label = ctk.CTkLabel(add_window, text="", text_color="red")
        error_label.pack(pady=5)

        # Due Date
        ctk.CTkLabel(add_window, text="⏰ Due Date:").pack(pady=5)
        due_entry = ctk.CTkEntry(add_window, width=400, placeholder_text="YYYY-MM-DD (defaults to today if empty)")
        due_entry.pack(pady=5)

        # Priority
        ctk.CTkLabel(add_window, text="⚡ Priority:").pack(pady=5)
        priority_var = ctk.StringVar(value="Medium")
        priority_menu = ctk.CTkOptionMenu(add_window, values=["Low", "Medium", "High"], variable=priority_var)
        priority_menu.pack(pady=5)

        # Tags
        ctk.CTkLabel(add_window, text="🏷️ Tags (comma-separated):").pack(pady=5)
        tags_entry = ctk.CTkEntry(add_window, width=400, placeholder_text="e.g., work, personal, urgent")
        tags_entry.pack(pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(add_window)
        button_frame.pack(pady=20)

        save_btn = ctk.CTkButton(button_frame, text="💾 Save Task", command=lambda: self.save_task(
            desc_entry.get(), due_entry.get(), priority_var.get(), tags_entry.get(), add_window, error_label))
        save_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(button_frame, text="❌ Cancel", command=add_window.destroy)
        cancel_btn.pack(side="left", padx=10)

    def save_task(self, description, due_date, priority, tags, window, error_label):
        if not description:
            error_label.configure(text="🚫 Please enter a task description!")
        else:
            error_label.configure(text="")
            if not due_date:
                due_date = datetime.now().strftime("%Y-%m-%d")
            tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            new_task = ToDoItem(description, due_date, priority, tags_list)
            self.todo_list.add_item(new_task)
            self.show_all_tasks()
            window.destroy()

    def remove_item(self, index):
        self.todo_list.remove_item(index)
        self.show_all_tasks()

    def mark_completed(self, index):
        self.todo_list.mark_completed(index)
        self.show_all_tasks()

    def switch_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        ctk.set_appearance_mode(self.current_theme)

    def load_data(self):
        try:
            with open("todo_data.json", "r") as f:
                self.todo_list = ToDoList.from_json(f.read())
                self.show_all_tasks()
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def on_closing(self):
        with open("todo_data.json", "w") as f:
            f.write(self.todo_list.to_json())
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = ToDoUI(root)
    root.mainloop()