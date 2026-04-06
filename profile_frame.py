import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from database import get_connection, hash_password
from PIL import Image, ImageTk
import mysql.connector
import os
from sidebar_base import BaseSidebarFrame


class ProfileFrame(BaseSidebarFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.show_pw = tk.BooleanVar()
        self.edit_mode = False
        self.entries = {}

        # --- SAFEGUARDS (Add these lines to stop the crash) ---
        self.is_admin = 0
        self.user_id = None
        self.current_name = ""
        self.current_email = ""
        self.image_path = None
        # ------------------------------------------------------

        # --- Sidebar ---
        self.admin_btn = self.add_sidebar_button("ADMIN MODE", self.open_admin_dashboard)
        self.dash_btn = self.add_sidebar_button("DASHBOARD", self.back_to_dashboard)
        self.add_sidebar_button("INTERVIEW SHEET", self.open_interview_sheet)
        self.add_sidebar_button("PROFILE", None)
        self.add_sidebar_button("LOG OUT", self.logout, side="bottom")

        # Hide Admin Button Initially
        self.hide_sidebar_button("ADMIN MODE")

        # --- Content ---
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.main_frame.pack(side="left", fill="both", expand=True)

    def load_user_data(self):
        user = self.controller.current_user
        if not user: return
        self.user_id = user[0]
        self.current_name = user[1]
        self.current_email = user[2]
        self.current_contact = user[4] if len(user) > 4 else ""
        self.current_lc = user[5] if len(user) > 5 else ""
        self.current_role = user[6] if len(user) > 6 else ""
        self.image_path = user[7] if len(user) > 7 else None
        self.is_admin = user[8] if len(user) > 8 else 0

    def on_show(self):
        self.edit_mode = False
        self.load_user_data()
        self.set_button_state("PROFILE")

        # --- SECURITY FIX: Strict Check ---
        if self.is_admin == 1:
            self.show_sidebar_button("ADMIN MODE", before_text="DASHBOARD")
            self.admin_btn.configure(state="normal")
        else:
            self.hide_sidebar_button("ADMIN MODE")

        self.build_profile_form()

    def open_interview_sheet(self):
        self.controller.show_frame("AdminInterviewerModeFrame")
        dashboard_instance = self.controller.frames.get("AdminInterviewerModeFrame")
        if dashboard_instance and hasattr(dashboard_instance, 'open_interview'):
            dashboard_instance.open_interview()

    def open_admin_dashboard(self):
        self.controller.show_frame("AdminDashboardFrame")

    def back_to_dashboard(self):
        self.controller.unbind_all('<Return>')
        target = "AdminInterviewerModeFrame" if hasattr(self, 'is_admin') and self.is_admin else "DashboardFrame"
        self.controller.show_frame(target)

    # --- MISSING METHODS ADDED HERE ---

    def enable_edit_mode(self):
        self.edit_mode = True
        self.build_profile_form()

    def cancel_edit(self):
        self.edit_mode = False
        self.load_user_data()  # Revert data
        self.build_profile_form()

    def upload_new_photo(self):
        fp = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if fp:
            self.image_path = fp
            self.build_profile_form()

    def save_profile_changes(self):
        conn, cursor = get_connection()
        try:
            sql = "UPDATE users SET full_name=%s, email=%s, contact_no=%s, lc=%s, role=%s, image_path=%s WHERE id=%s"
            vals = (self.entries['full_name'].get(), self.entries['email'].get(), self.entries['contact_no'].get(),
                    self.entries['lc'].get(), self.entries['role'].get(), self.image_path, self.user_id)
            cursor.execute(sql, vals)
            conn.commit()

            # Update local user data
            cursor.execute("SELECT * FROM users WHERE id=%s", (self.user_id,))
            self.controller.current_user = cursor.fetchone()

            messagebox.showinfo("Success", "Updated!")
            self.edit_mode = False
            self.load_user_data()
            self.build_profile_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()

    # ----------------------------------

    def build_profile_form(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        if not self.controller.current_user: return

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=50, pady=20)

        # Header
        header = ctk.CTkFrame(scroll, fg_color="white")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="PROFILE", font=("Helvetica", 24, "bold"), text_color="black").pack(side="left")

        if self.edit_mode:
            ctk.CTkButton(header, text="Save Changes", fg_color="#28a745", command=self.save_profile_changes).pack(
                side="right", padx=10)
            ctk.CTkButton(header, text="Cancel", fg_color="#dc3545", command=self.cancel_edit).pack(side="right")
        else:
            ctk.CTkButton(header, text="Edit Profile", fg_color="#1966C7", command=self.enable_edit_mode).pack(
                side="right", padx=10)

        self.display_profile_image(scroll)
        if self.edit_mode:
            ctk.CTkButton(scroll, text="Change Photo", fg_color="#f0f0f0", text_color="black",
                          command=self.upload_new_photo).pack(pady=5)

        # Fields
        info_frame = ctk.CTkFrame(scroll, fg_color="white")
        info_frame.pack(anchor="center", pady=(10, 20))
        fields = [("Full Name", self.current_name, "full_name"), ("Email", self.current_email, "email"),
                  ("Contact No", self.current_contact, "contact_no"), ("LC", self.current_lc, "lc"),
                  ("Role", self.current_role, "role")]

        self.entries = {}
        for i, (lbl, val, key) in enumerate(fields):
            ctk.CTkLabel(info_frame, text=lbl + ":", font=("Arial", 14, "bold"), text_color="black", width=150,
                         anchor="e").grid(row=i, column=0, padx=10, pady=8)
            if self.edit_mode:
                e = ctk.CTkEntry(info_frame, font=("Arial", 14), width=250)
                e.insert(0, val if val else "")
                e.grid(row=i, column=1, padx=10, pady=8)
                self.entries[key] = e
            else:
                ctk.CTkLabel(info_frame, text=val if val else "N/A", font=("Arial", 14), text_color="black").grid(row=i,
                                                                                                                  column=1,
                                                                                                                  sticky="w",
                                                                                                                  padx=10,
                                                                                                                  pady=8)

        if not self.edit_mode:
            ctk.CTkLabel(scroll, text="--- Change Password ---", font=("Helvetica", 16), text_color="black").pack(
                pady=(30, 10))
            self.old_pw_entry = self.make_entry(scroll, "Current Password", True)
            self.new_pw_entry = self.make_entry(scroll, "New Password", True)
            self.confirm_pw_entry = self.make_entry(scroll, "Confirm New Password", True)
            ctk.CTkCheckBox(scroll, text="Show Passwords", variable=self.show_pw, command=self.toggle_pw,
                            text_color="black").pack(pady=(0, 15))
            ctk.CTkButton(scroll, text="Update Password", fg_color="#dc3545", command=self.change_password).pack(pady=5)

    def display_profile_image(self, parent):
        lbl = ctk.CTkLabel(parent, text="")
        lbl.pack(pady=(0, 10))
        try:
            if self.image_path and os.path.exists(self.image_path):
                img = ctk.CTkImage(light_image=Image.open(self.image_path), size=(120, 120))
                lbl.configure(image=img)
            else:
                lbl.configure(text="No Image", width=120, height=120, fg_color="#eee")
        except:
            lbl.configure(text="Error")

    def make_entry(self, parent, ph, pwd=False):
        e = ctk.CTkEntry(parent, placeholder_text=ph, width=250, justify="center");
        e.pack(pady=5)
        if pwd: e.configure(show="*" if not self.show_pw.get() else "")
        return e

    def toggle_pw(self):
        char = "" if self.show_pw.get() else "*"
        for e in [self.old_pw_entry, self.new_pw_entry, self.confirm_pw_entry]:
            e.configure(show=char)

    def change_password(self):
        old, new, conf = self.old_pw_entry.get(), self.new_pw_entry.get(), self.confirm_pw_entry.get()
        if not all([old, new, conf]): return messagebox.showerror("Error", "Fill all fields")
        if new != conf: return messagebox.showerror("Error", "Passwords mismatch")

        conn, cursor = get_connection()
        try:
            cursor.execute("SELECT password FROM users WHERE id=%s", (self.user_id,))
            if hash_password(old) != cursor.fetchone()[0]: return messagebox.showerror("Error",
                                                                                       "Wrong current password")
            cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hash_password(new), self.user_id))
            conn.commit();
            messagebox.showinfo("Success", "Updated!");
            self.logout()
        finally:
            cursor.close(); conn.close()