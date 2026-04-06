import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import customtkinter as ctk
from database import get_connection, hash_password
from datetime import datetime, timedelta
import os

# COLORS
DARK_BLUE = "#1966C7"
MID_BLUE = "#1E70DB"
WHITE = "#FFFFFF"
TEXT_GRAY = "#333"
BLACK = "#000000"
FORM_WIDTH = 450
FORM_HEIGHT = 680


class LoginFrame(ctk.CTkFrame):
    ROCKET_PATH = "Rocket.png"

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.show_pw = tk.BooleanVar(value=False)
        self.email_entry = None
        self.password_entry = None
        self.login_btn = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        self.rocket_icon = self._load_real_or_placeholder(size=(350, 350))
        self._build_left_panel()
        self._build_right_panel()

    def _load_real_or_placeholder(self, size):
        if os.path.exists(self.ROCKET_PATH):
            try:
                img = Image.open(self.ROCKET_PATH)
                img = img.resize(size, Image.LANCZOS)
                return ctk.CTkImage(light_image=img, size=size)
            except Exception:
                pass
        img = Image.new("RGB", size, DARK_BLUE)
        draw = ImageDraw.Draw(img)
        draw.ellipse((30, 30, 170, 170), fill=MID_BLUE, outline=WHITE, width=4)
        return ctk.CTkImage(light_image=img, size=size)

    def _build_left_panel(self):
        left_frame = ctk.CTkFrame(self, fg_color=DARK_BLUE, corner_radius=0)
        left_frame.grid(row=0, column=0, sticky="nsew")
        content = ctk.CTkFrame(left_frame, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, image=self.rocket_icon, text="").pack(pady=(0, 15))

    def _build_right_panel(self):
        right_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0)
        right_frame.grid(row=0, column=1, sticky="nsew")

        content = ctk.CTkFrame(right_frame, fg_color=WHITE, width=FORM_WIDTH, height=FORM_HEIGHT)
        content.place(relx=0.5, rely=0.5, anchor="center")
        content.pack_propagate(False)

        inner_box = ctk.CTkFrame(content, fg_color=WHITE)
        inner_box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(inner_box, text="Sign In", font=("Arial", 28, "bold"), text_color=TEXT_GRAY).pack(pady=(0, 30))

        # Start with empty placeholders
        self.create_entry_style(inner_box, "E-mail Address", "Enter your email", "email_entry")
        self.create_entry_style(inner_box, "Password", "Enter your password", "password_entry", is_password=True)

        options_frame = ctk.CTkFrame(inner_box, fg_color="transparent", width=350)
        options_frame.pack(pady=(20, 30), padx=25)

        ctk.CTkCheckBox(options_frame, text="Show Password", variable=self.show_pw,
                        command=self.toggle_password_visibility, text_color=TEXT_GRAY,
                        width=100, border_color=TEXT_GRAY, hover_color=MID_BLUE, fg_color=MID_BLUE).pack(side="left",
                                                                                                         padx=(0, 20))

        forgot_btn = ctk.CTkButton(options_frame, text="Forgot Password?", fg_color="transparent",
                                   text_color=MID_BLUE, hover_color="#EEE", width=100,
                                   command=lambda: self.controller.show_frame("ResetPasswordFrame"))
        forgot_btn.pack(side="left")

        btn_frame = ctk.CTkFrame(inner_box, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.login_btn = ctk.CTkButton(btn_frame, text="Sign in", fg_color=MID_BLUE, hover_color=DARK_BLUE, width=120,
                                       command=self.login_user)
        self.login_btn.pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Sign Up", fg_color="transparent", border_width=2, border_color=MID_BLUE,
                      text_color=MID_BLUE, hover_color="#EEE", width=120,
                      command=lambda: self.controller.show_frame("RegisterFrame")).pack(side="left", padx=10)

    def create_entry_style(self, parent, label, placeholder, attribute_name, is_password=False):
        ctk.CTkLabel(parent, text=label, anchor="center", font=("Arial", 14, "bold"), text_color=TEXT_GRAY).pack(
            pady=(10, 0), padx=25, anchor="center")

        entry_kwargs = {
            "placeholder_text": "",  # Start empty
            "width": 350,
            "height": 35,
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
        entry.pack(pady=(0, 2), padx=25, anchor="center")
        tk.Frame(parent, height=2, width=350, bg=MID_BLUE).pack(pady=(0, 10), anchor="center")
        setattr(self, attribute_name, entry)

    def toggle_password_visibility(self):
        show_char = "" if self.show_pw.get() else "*"
        self.password_entry.configure(show=show_char)

    def login_user(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        conn = None
        cursor = None
        try:
            conn, cursor = get_connection()

            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user_data = cursor.fetchone()

            if not user_data:
                messagebox.showerror("Error", "Invalid email or password.")
                return

            stored_hash = user_data[3]
            try:
                login_attempts = user_data[9] if len(user_data) > 9 else 0
                lockout_time = user_data[10] if len(user_data) > 10 else None
            except IndexError:
                login_attempts = 0
                lockout_time = None

            if lockout_time and datetime.now() < lockout_time:
                remaining = lockout_time - datetime.now()
                minutes = int(remaining.total_seconds() // 60)
                messagebox.showerror("Locked Out", f"Account locked. Try again in {minutes} minutes.")
                return

            if hash_password(password) == stored_hash:
                cursor.execute("UPDATE users SET login_attempts = 0, lockout_time = NULL WHERE email = %s",
                               (email,))
                conn.commit()
                self.controller.current_user = user_data
                is_admin = user_data[8] if len(user_data) > 8 else 0
                if is_admin:
                    self.controller.show_frame("AdminDashboardFrame")
                else:
                    self.controller.show_frame("DashboardFrame")
                self.email_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
            else:
                login_attempts += 1
                if login_attempts >= 5:
                    lockout_time = datetime.now() + timedelta(minutes=30)
                    cursor.execute("UPDATE users SET login_attempts = %s, lockout_time = %s WHERE email = %s",
                                   (login_attempts, lockout_time, email))
                    messagebox.showerror("Error", "Too many failed attempts. Account locked for 30 minutes.")
                else:
                    cursor.execute("UPDATE users SET login_attempts = %s WHERE email = %s",
                                   (login_attempts, email))
                    messagebox.showerror("Error", f"Invalid password. Attempt {login_attempts}/5")
                conn.commit()
        except Exception as e:
            messagebox.showerror("System Error", str(e))
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def on_show(self):
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

        def inject_placeholders():
            self.email_entry.configure(placeholder_text="Enter your email")
            self.password_entry.configure(placeholder_text="Enter your password")
            self.login_btn.focus_set()

            # --- FIX: RE-APPLY VISIBILITY AFTER UPDATE ---
            self.toggle_password_visibility()

        self.after(200, inject_placeholders)

        self.controller.bind_all('<Return>', lambda event: self.login_user())