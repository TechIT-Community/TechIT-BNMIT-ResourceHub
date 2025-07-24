import customtkinter as ctk
import os
from tkinter import filedialog

# Base class for the application
class LicensePlateApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure the main window
        self.title("ALPERS - License Plate Recognition")

        # Set window dimensions to 70-80% of the screen size and center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.75)
        window_height = int(screen_height * 0.75)
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Disable resizing
        self.resizable(False, False)

        # Set gradient background
        self.configure(bg_gradient=("#4e54c8", "#8f94fb"))

        # Initialize UI components
        self.initialize_ui()

    def initialize_ui(self):
        """Initialize the UI components."""
        # Title label
        self.title_label = ctk.CTkLabel(
            self,
            text="ALPERS",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="white"
        )
        self.title_label.place(relx=0.5, rely=0.1, anchor="center")

        # Button to capture from image
        self.image_button = ctk.CTkButton(
            self,
            text="Capture from Image",
            command=self.open_image_capture_window,
            font=ctk.CTkFont(size=20),
            width=260,
            height=100
        )
        self.image_button.place(relx=0.3, rely=0.6, anchor="center")

        # Button to capture from video
        self.video_button = ctk.CTkButton(
            self,
            text="Capture from Video",
            command=self.run_video_capture,
            font=ctk.CTkFont(size=20),
            width=260,
            height=100
        )
        self.video_button.place(relx=0.7, rely=0.6, anchor="center")

    def open_image_capture_window(self):
        """Open a new window to select an image path and process it."""
        toplevel = ctk.CTkToplevel(self)
        toplevel.after(500, toplevel.focus(), 1)
        toplevel.title("Select Image for Recognition")
        toplevel.geometry("400x200")

        def process_image():
            image_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image Files", "*.jpg;*.png")])
            if image_path:
                os.system(f"python Main/misc.py \"{image_path}\"")

        label = ctk.CTkLabel(
            toplevel,
            text="Select an image for license plate recognition:",
            font=ctk.CTkFont(size=16)
        )
        label.pack(pady=20)

        browse_button = ctk.CTkButton(
            toplevel,
            text="Browse Image",
            command=process_image,
            font=ctk.CTkFont(size=14)
        )
        browse_button.pack(pady=10)

    def run_video_capture(self):
        """Run the video capture functionality."""
        os.system("python Main/main2.py")

# Main execution
if __name__ == "__main__":
    app = LicensePlateApp()
    app.mainloop()