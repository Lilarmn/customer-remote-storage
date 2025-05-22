import customtkinter as ctk
import tkinter

class YourApp:
    def __init__(self):
        # ... [your existing setup code] ...

        # Table Body
        self.scrollable_frame = ctk.CTkScrollableFrame(list_container)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Configure columns (ensure weights match your needs)
        self.column_weights = [1, 1, 1]  # Example column configuration
        for col, weight in enumerate(self.column_weights):
            self.scrollable_frame.grid_columnconfigure(col, weight=weight, uniform="cols")

        # Radio button variable and row tracking
        self.radio_var = tkinter.IntVar(value=-1)
        self.rows = []  # Stores references to row frames

        # Generate example rows (replace with your data)
        self.create_sample_rows()

        # Trace radio variable changes to update highlights
        self.radio_var.trace_add("write", self.update_row_highlight)

    def create_sample_rows(self):
        # Sample data - replace with your actual data
        sample_data = [["Row 1", "Data 1"], ["Row 2", "Data 2"], ["Row 3", "Data 3"]]

        for idx, row_data in enumerate(sample_data):
            # Create a frame for the entire row
            row_frame = ctk.CTkFrame(self.scrollable_frame)
            row_frame.grid(row=idx, column=0, columnspan=len(self.column_weights), sticky="nsew")

            # Store reference to the row frame
            self.rows.append(row_frame)

            # Add radio button
            radio = ctk.CTkRadioButton(
                row_frame,
                text="",
                variable=self.radio_var,
                value=idx
            )
            radio.grid(row=0, column=0, padx=5)

            # Add data labels (customize based on your columns)
            for col, text in enumerate(row_data, start=1):
                label = ctk.CTkLabel(row_frame, text=text)
                label.grid(row=0, column=col, padx=5, pady=5)

            # Make entire row clickable
            row_frame.bind("<Button-1>", lambda e, idx=idx: self.radio_var.set(idx))

    def update_row_highlight(self, *args):
        selected_idx = self.radio_var.get()
        for idx, row_frame in enumerate(self.rows):
            if idx == selected_idx:
                row_frame.configure(fg_color=("gray75", "gray25"))  # Highlight color
            else:
                row_frame.configure(fg_color="transparent")  # Default color