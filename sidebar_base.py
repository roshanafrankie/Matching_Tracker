import customtkinter as ctk
from tkinter import messagebox


class BaseSidebarFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller

        # --- Shared Sidebar Container ---
        # Fixed width of 200px
        self.sidebar = ctk.CTkFrame(self, fg_color="#1966C7", width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", anchor="w")

        # Prevent the sidebar from shrinking/expanding based on buttons
        self.sidebar.pack_propagate(False)

        self.sidebar_buttons = {}

    def add_sidebar_button(self, text, command, side="top"):
        """Creates a modern styled button that fits the sidebar."""
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            font=('Arial', 12, 'bold'),
            fg_color="transparent",  # Transparent background by default
            text_color="white",  # White text
            hover_color="#1253a6",  # Darker blue on hover
            corner_radius=0,  # Square edges
            height=45,  # Slightly shorter for cleaner look
            width=190,  # Fits inside the 200px sidebar
            anchor="w",  # Align text to the left
            command=command
        )

        # Pack with 0 horizontal padding so it fills the width
        if side == "bottom":
            btn.pack(pady=2, padx=0, side="bottom")
        else:
            btn.pack(pady=2, padx=0)

        self.sidebar_buttons[text] = btn
        return btn

    def set_button_state(self, active_button_name):
        """Highlights the active button."""
        for name, button in self.sidebar_buttons.items():
            if name == active_button_name:
                button.configure(fg_color="#1E70DB", state="disabled", text_color="white")
            else:
                button.configure(fg_color="transparent", state="normal", text_color="white")

    def hide_sidebar_button(self, text):
        """Safely hides a specific button."""
        if text in self.sidebar_buttons:
            self.sidebar_buttons[text].pack_forget()

    def show_sidebar_button(self, text, before_text=None):
        """Safely shows a button."""
        if text in self.sidebar_buttons:
            btn = self.sidebar_buttons[text]
            if before_text and before_text in self.sidebar_buttons:
                btn.pack(pady=2, padx=0, before=self.sidebar_buttons[before_text])
            else:
                btn.pack(pady=2, padx=0)

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
        if confirm:
            self.controller.current_user = None
            self.controller.show_frame("LoginFrame")