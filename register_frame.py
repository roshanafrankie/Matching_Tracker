import tkinter as tk
from tkinter import messagebox, filedialog
from database import get_connection, hash_password
import mysql.connector
import os
import re
import phonenumbers
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk

# COLORS
DARK_BLUE = "#1966C7"
MID_BLUE = "#1E70DB"
WHITE = "#FFFFFF"
TEXT_GRAY = "#333"
BLACK = "#000000"
FORM_WIDTH = 450
FORM_HEIGHT = 680


class RegisterFrame(ctk.CTkFrame):
    ROCKET_PATH = "Rocket.png"

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.image_path = None
        self.conn, self.cursor = get_connection()
        self.show_pw = tk.BooleanVar(value=False)
        self.signup_btn = None  # Reference

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
        left = ctk.CTkFrame(self, fg_color=DARK_BLUE, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        content = ctk.CTkFrame(left, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, image=self.rocket_icon, text="").pack(pady=(0, 15))

    def _build_right_panel(self):
        right = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        wrapper = ctk.CTkFrame(right, fg_color=WHITE, width=FORM_WIDTH, height=750)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
        wrapper.pack_propagate(False)

        ctk.CTkLabel(wrapper, text="SIGN UP", font=("Arial", 24, "bold"), text_color=TEXT_GRAY).pack(
            pady=(15, 10))

        self.create_entry_style(wrapper, "Name", "Enter full name", "name_entry")
        self.create_entry_style(wrapper, "E-mail", "Enter email", "email_entry")
        self.create_entry_style(wrapper, "Contact", "+CountryCode Number", "contact_entry")
        self.create_entry_style(wrapper, "LC", "Local Committee", "lc_entry")
        self.create_entry_style(wrapper, "Role", "Your Role", "role_entry")
        self.create_entry_style(wrapper, "Password", "Enter password", "password_entry", is_password=True)
        self.create_entry_style(wrapper, "Confirm", "Confirm password", "confirm_entry", is_password=True)

        ctk.CTkCheckBox(wrapper, text="Show Passwords", variable=self.show_pw, command=self.toggle_password_visibility,
                        text_color=TEXT_GRAY, border_color=TEXT_GRAY, hover_color=MID_BLUE, fg_color=MID_BLUE).pack(
            pady=(5, 5), anchor="center", padx=25)

        img_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        img_frame.pack(pady=5)
        ctk.CTkButton(img_frame, text="Upload Image", command=self.upload_image, fg_color=MID_BLUE).pack(side="left")
        self.img_label = ctk.CTkLabel(img_frame, text="No image selected", text_color=TEXT_GRAY)
        self.img_label.pack(side="left", padx=10)

        btn_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        btn_frame.pack(pady=(15, 10))

        self.signup_btn = ctk.CTkButton(btn_frame, text="Sign Up", fg_color=MID_BLUE, width=120, height=30,
                                        command=self.register_user)
        self.signup_btn.pack(side="left", padx=15)

        ctk.CTkButton(btn_frame, text="Back", fg_color="transparent", border_width=2, border_color=MID_BLUE,
                      text_color=MID_BLUE, width=120, height=30,
                      command=lambda: self.controller.show_frame("LoginFrame")).pack(side="left")

    def create_entry_style(self, parent, label, placeholder, attribute_name, is_password=False):
        ctk.CTkLabel(parent, text=label, anchor="center", font=("Arial", 14, "bold"), text_color=TEXT_GRAY).pack(
            pady=(5, 2), padx=25
        )

        show_char = "*" if is_password else ""

        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=350, height=35,
                             show=show_char,
                             placeholder_text_color="#555555",
                             fg_color=WHITE,
                             text_color=TEXT_GRAY,
                             border_width=2, border_color=BLACK,
                             corner_radius=5,
                             justify="center")

        entry.pack(pady=(0, 2), padx=25)
        tk.Frame(parent, height=2, width=350, bg=MID_BLUE).pack(pady=(0, 5))
        setattr(self, attribute_name, entry)

    def toggle_password_visibility(self):
        show_char = "" if self.show_pw.get() else "*"
        self.password_entry.configure(show=show_char)
        self.confirm_entry.configure(show=show_char)

    def upload_image(self):
        fp = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if fp:
            self.image_path = fp
            self.img_label.configure(text=os.path.basename(fp), text_color="green")

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        self.lc_entry.delete(0, tk.END)
        self.role_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_entry.delete(0, tk.END)
        self.image_path = None
        self.img_label.configure(text="No image selected", text_color=TEXT_GRAY)

    def is_valid_email(self, email):
        return re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

    def is_valid_contact(self, c):
        if not c.startswith("+"): return False, "Contact must start with +"
        try:
            num = phonenumbers.parse(c, None)
            if not phonenumbers.is_valid_number(num): return False, "Invalid number"
            return True, ""
        except:
            return False, "Bad number format"

    def is_strong_password(self, pw):
        if len(pw) < 8: return False, "Minimum 8 characters"
        if not re.search(r"[A-Z]", pw): return False, "Need uppercase letter"
        if not re.search(r"[0-9]", pw): return False, "Need a digit"
        if not re.search(r"[^A-Za-z0-9]", pw): return False, "Need special symbol"
        return True, ""

    def register_user(self):
        self.conn, self.cursor = get_connection()
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        contact = self.contact_entry.get().strip()
        lc = self.lc_entry.get().strip()
        role = self.role_entry.get().strip()
        pw = self.password_entry.get().strip()
        conf = self.confirm_entry.get().strip()

        if not all([name, email, contact, lc, role, pw, conf]):
            messagebox.showerror("Error", "Fill all fields")
            return
        if pw != conf:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Invalid email")
            return
        ok, msg = self.is_valid_contact(contact)
        if not ok:
            messagebox.showerror("Error", msg)
            return
        strong, msg = self.is_strong_password(pw)
        if not strong:
            messagebox.showerror("Error", msg)
            return

        hashed = hash_password(pw)
        try:
            sql = """INSERT INTO users (full_name,email,password,contact_no,lc,role,image_path)
                     VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            vals = (name, email, hashed, contact, lc, role, self.image_path)
            self.cursor.execute(sql, vals)
            self.conn.commit()
            messagebox.showinfo("Success", "Registration complete!")
            self.clear_form()
            self.controller.show_frame("LoginFrame")
        except mysql.connector.Error as e:
            if e.errno == 1062:
                messagebox.showerror("Error", "Email already registered")
            else:
                messagebox.showerror("Error", str(e))

    def on_show(self):
        self.clear_form()

        # --- FIX: FOCUS + REFRESH ---
        self.signup_btn.focus_set()

        def refresh_placeholders():
            self.name_entry.configure(placeholder_text="Enter full name")
            self.email_entry.configure(placeholder_text="Enter email")
            self.contact_entry.configure(placeholder_text="+CountryCode Number")
            self.lc_entry.configure(placeholder_text="Local Committee")
            self.role_entry.configure(placeholder_text="Your Role")
            self.password_entry.configure(placeholder_text="Enter password")
            self.confirm_entry.configure(placeholder_text="Confirm password")

        self.after(100, refresh_placeholders)

        self.controller.unbind_all('<Return>')