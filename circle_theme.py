import customtkinter as ctk
import math

class PieButtonApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Tools App")
        self.geometry("600x400")
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create main container frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create circular button container
        self.create_pie_buttons()
        
    def create_pie_buttons(self):
        # Create canvas for circular buttons
        self.canvas = ctk.CTkCanvas(self.main_frame, width=300, height=300, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Pie button parameters
        center_x, center_y = 150, 150
        radius = 120
        num_buttons = 6
        angle = 360 / num_buttons
        
        # Create pie segments
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD", "#D4A5A5"]
        for i in range(num_buttons):
            start_angle = i * angle
            end_angle = (i + 1) * angle
            
            # Create arc segment
            segment = self.canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle, extent=angle,
                fill=colors[i], outline=""
            )
            
            # Bind click event to segment
            self.canvas.tag_bind(segment, "<Button-1>", 
                                lambda event, idx=i: self.on_pie_button_click(idx))
            
            # Add hover effect
            self.canvas.tag_bind(segment, "<Enter>", 
                               lambda event, seg=segment: self.on_segment_hover(seg))
            self.canvas.tag_bind(segment, "<Leave>", 
                               lambda event, seg=segment: self.on_segment_leave(seg))
            
            # Add text labels
            text_angle = math.radians(start_angle + angle/2)
            text_x = center_x + (radius * 0.6) * math.cos(text_angle)
            text_y = center_y + (radius * 0.6) * math.sin(text_angle)
            
            self.canvas.create_text(text_x, text_y,
                                   text=f"Tool {i+1}",
                                   fill="white",
                                   font=("Arial", 10, "bold"))
            
    def on_segment_hover(self, segment):
        self.canvas.itemconfig(segment, fill=self.lighten_color(self.canvas.itemcget(segment, "fill")))
        
    def on_segment_leave(self, segment):
        original_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD", "#D4A5A5"]
        index = int(self.canvas.gettags(segment)[0].split("_")[1])
        self.canvas.itemconfig(segment, fill=original_colors[index])
        
    def lighten_color(self, color, amount=30):
        # Convert hex to RGB
        rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        # Lighten color
        new_rgb = tuple(min(255, c + amount) for c in rgb)
        # Convert back to hex
        return f'#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}'
        
    def on_pie_button_click(self, button_index):
        print(f"Button {button_index + 1} clicked!")
        # Add your button functions here
        if button_index == 0:
            self.tool1_function()
        elif button_index == 1:
            self.tool2_function()
        # Add more functions for other buttons
        
    def tool1_function(self):
        print("Tool 1 activated!")
        
    def tool2_function(self):
        print("Tool 2 activated!")

if __name__ == "__main__":
    app = PieButtonApp()
    app.mainloop()