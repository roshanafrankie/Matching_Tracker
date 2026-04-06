import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import os
from database import get_connection, hash_password

# COLORS
DARK_BLUE = "#1966C7"
MID_BLUE = "#1E70DB"
WHITE = "#FFFFFF"
TEXT_GRAY = "#333"
BLACK = "#000000"
FORM_WIDTH = 450
FORM_HEIGHT = 680


class ResetPasswordFrame(ctk.CTkFrame):
    ROCKET_PATH = "Rocket.png"

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.conn, self.cursor = get_connection()
        self.show_pw = tk.BooleanVar(value=False)
        self.reset_btn = None

        # Layout configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        self.rocket_icon = self._load_image(size=(350, 350))
        self._build_left_panel()
        self._build_right_panel()

    def _load_image(self, size):
        if os.path.exists(self.ROCKET_PATH):
            try:
                img = Image.open(self.ROCKET_PATH)
                img = img.resize(size, Image.LANCZOS)
                return ctk.CTkImage(light_image=img, size=size)
            except:
                pass
        img = Image.new("RGB", size, DARK_BLUE)
        draw = ImageDraw.Draw(img)
        draw.ellipse((30, 30, 170, 170), fill=MID_BLUE, outline=WHITE, width=4)
        return ctk.CTkImage(light_image=img, size=size)

    def _build_left_panel(self):
        left = ctk.CTkFrame(self, fg_color=DARK_BLUE, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        content = ctk.CTkFrame(left, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, image=self.rocket_icon, text="").pack(pady=(0, 15))

    def _build_right_panel(self):
        right = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        wrapper = ctk.CTkFrame(right, fg_color=WHITE, width=FORM_WIDTH, height=FORM_HEIGHT)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(wrapper, text="Reset Password", font=("Arial", 24, "bold"), text_color=TEXT_GRAY).pack(
            pady=(20, 20))

        # Inputs
        self.create_entry(wrapper, "Registered Email", "Enter your email", "email_entry")
        self.create_entry(wrapper, "New Password", "Enter new password", "new_pw_entry", is_password=True)
        self.create_entry(wrapper, "Confirm Password", "Confirm new password", "conf_pw_entry", is_password=True)

        ctk.CTkCheckBox(wrapper, text="Show Passwords", variable=self.show_pw,
                        command=self.toggle_password_visibility, text_color=TEXT_GRAY,
                        hover_color=MID_BLUE, fg_color=MID_BLUE).pack(pady=(10, 20), anchor="w", padx=25)

        # Buttons
        self.reset_btn = ctk.CTkButton(wrapper, text="Reset Password", fg_color=MID_BLUE, hover_color=DARK_BLUE,
                                       width=350, height=40,
                                       command=self.reset_password)
        self.reset_btn.pack(pady=(0, 10))

        ctk.CTkButton(wrapper, text="Back to Login", fg_color="transparent", text_color=MID_BLUE, hover_color="#EEE",
                      border_width=2, border_color=MID_BLUE,
                      width=350, height=40, command=lambda: self.controller.show_frame("LoginFrame")).pack()

    def create_entry(self, parent, label, placeholder, attr_name, is_password=False):
        ctk.CTkLabel(parent, text=label, anchor="center", font=("Arial", 14, "bold"), text_color=TEXT_GRAY).pack(
            pady=(10, 0), padx=25)

        entry_kwargs = {
            # --- FIX: Start with EMPTY placeholder ---
            "placeholder_text": "",
            "width": 350,
            "height": 40,
            "fg_color": WHITE,
            "text_color": TEXT_GRAY,
            "placeholder_text_color": "#555555",
            "border_width": 2,
            "border_color": BLACK,
            "corner_radius": 5,
            "justify": "center"
        }

        if is_password:
            entry_kwargs["show"] = "*"

        entry = ctk.CTkEntry(parent, **entry_kwargs)
        entry.pack(pady=(0, 2), padx=25)
        tk.Frame(parent, height=2, width=350, bg=MID_BLUE).pack(pady=(0, 10))
        setattr(self, attr_name, entry)

    def toggle_password_visibility(self):
        show_char = "" if self.show_pw.get() else "*"
        self.new_pw_entry.configure(show=show_char)
        self.conf_pw_entry.configure(show=show_char)

    def reset_password(self):
        email = self.email_entry.get().strip()
        new_pw = self.new_pw_entry.get().strip()
        conf_pw = self.conf_pw_entry.get().strip()

        if not all([email, new_pw, conf_pw]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        if new_pw != conf_pw:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if len(new_pw) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        self.conn, self.cursor = get_connection()
        try:
            self.cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            user = self.cursor.fetchone()
            if not user:
                messagebox.showerror("Error", "This email is not registered.")
                return

            new_hash = hash_password(new_pw)
            self.cursor.execute("UPDATE users SET password=%s, login_attempts=0, lockout_time=NULL WHERE email=%s",
                                (new_hash, email))
            self.conn.commit()

            messagebox.showinfo("Success", "Password reset successful!")
            self.email_entry.delete(0, tk.END)
            self.new_pw_entry.delete(0, tk.END)
            self.conf_pw_entry.delete(0, tk.END)
            self.controller.show_frame("LoginFrame")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_show(self):
        self.email_entry.delete(0, tk.END)
        self.new_pw_entry.delete(0, tk.END)
        self.conf_pw_entry.delete(0, tk.END)

        # --- FIX: FOCUS + REFRESH + VISIBILITY ENFORCEMENT ---
        self.reset_btn.focus_set()

        def refresh_placeholders():
            self.email_entry.configure(placeholder_text="Enter your email")
            self.new_pw_entry.configure(placeholder_text="Enter new password")
            self.conf_pw_entry.configure(placeholder_text="Confirm new password")

            # --- FIX: RE-APPLY VISIBILITY AFTER UPDATE ---
            self.toggle_password_visibility()

        self.after(100, refresh_placeholders)

        self.controller.bind_all('<Return>', lambda event: self.reset_password())