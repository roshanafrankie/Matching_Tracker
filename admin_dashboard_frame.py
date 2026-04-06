import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from PIL import Image, ImageTk
import os
from sidebar_base import BaseSidebarFrame


class AdminDashboardFrame(BaseSidebarFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # --- Sidebar ---
        self.add_sidebar_button("ADMIN DASHBOARD", self.update_dashboard)
        self.add_sidebar_button("INTERVIEWER MODE", self.switch_to_interviewer_mode)
        self.add_sidebar_button("LOG OUT", self.logout, side="bottom")

        # --- Content ---
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.bold_font = ('Arial', 20, 'bold')
        self.normal_font = ctk.CTkFont(family="Arial", size=12)

    def update_dashboard(self):
        self.set_button_state("ADMIN DASHBOARD")
        for w in self.main_frame.winfo_children(): w.destroy()

        # 1. Header
        ctk.CTkLabel(self.main_frame, text="ADMIN DASHBOARD", font=self.bold_font, text_color="black").pack(anchor="nw",
                                                                                                            padx=20,
                                                                                                            pady=(
                                                                                                            20, 5))

        # 2. Stats Card
        total = self.get_total_system_interviews()
        card = ctk.CTkFrame(self.main_frame, fg_color="#1E70DB", height=120, corner_radius=10)
        card.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(card, text="🎉 System Overview", font=("Arial", 20, "bold"), text_color="white").pack(pady=(15, 0))
        ctk.CTkLabel(card, text=f"Total interviews conducted: {total}", font=("Arial", 18, "bold"),
                     text_color="white").pack(pady=(5, 15))

        # 3. Actions / Filters
        filter_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
        filter_frame.pack(fill="x", padx=20, pady=(10, 5))

        # Search Entry
        self.search_entry = ctk.CTkEntry(filter_frame, width=250, placeholder_text="Enter EP Name")
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.apply_filters())
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.apply_filters())

        # Project Dropdown
        ctk.CTkLabel(filter_frame, text="Project:", text_color="black", font=self.normal_font).pack(side="left",
                                                                                                    padx=(10, 5))
        self.project_filter_var = tk.StringVar(value="All Projects")
        projects = ["All Projects", "Aquatica", "Green Leaders", "Global Classroom", "On The Map", "Rooted"]
        self.project_filter_combo = ctk.CTkComboBox(filter_frame, variable=self.project_filter_var, values=projects,
                                                    state="readonly", width=150, command=lambda e: self.apply_filters())
        self.project_filter_combo.pack(side="left")

        # Buttons
        ctk.CTkButton(filter_frame, text="Apply", fg_color="#0d6efd", width=80, command=self.apply_filters).pack(
            side="left", padx=10)
        ctk.CTkButton(filter_frame, text="Reset", fg_color="gray", width=60, command=self.reset_filters).pack(
            side="left")

        # Delete Button (Red)
        ctk.CTkButton(filter_frame, text="Delete Selected", fg_color="#dc3545", hover_color="#a71d2a", width=120,
                      command=self.delete_selected).pack(side="right")

        # 4. Table (Treeview)
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))

        cols = ("ID", "EP Name", "Project", "Timeline", "Interviewer", "Date Entered")
        self.tree = ttk.Treeview(self.main_frame, columns=cols, show="headings", height=12)

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")

        self.tree.column("ID", width=50)
        self.tree.column("EP Name", width=200, anchor="w")

        self.tree.bind("<Double-1>", self.view_summary)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        self.populate_activity()

    def get_total_system_interviews(self):
        conn, cursor = get_connection()
        try:
            cursor.execute("SELECT COUNT(*) FROM interviews")
            return cursor.fetchone()[0]
        except:
            return 0
        finally:
            cursor.close();
            conn.close()

    def reset_filters(self):
        self.search_entry.delete(0,"end")
        self.project_filter_var.set("All Projects")
        self.apply_filters()

    def apply_filters(self):
        s = self.search_entry.get().strip()
        p = self.project_filter_var.get()
        if p == "All Projects": p = ""
        self.populate_activity(s, p)

    def populate_activity(self, search="", project_filter=""):
        conn, cursor = get_connection()
        try:
            # JOIN query to fetch the User's Name instead of just the ID
            # We select users.full_name as the second item
            q = """
                SELECT interviews.id, users.full_name, interviews.summary, interviews.timestamp 
                FROM interviews 
                LEFT JOIN users ON interviews.user_id = users.id
            """

            p_params = []
            conditions = []

            # note: specify 'interviews.summary' to avoid ambiguity in SQL
            if search:
                conditions.append("interviews.summary LIKE %s")
                p_params.append(f"%EP Name: {search}%")

            if project_filter:
                conditions.append("interviews.summary LIKE %s")
                p_params.append(f"%Project: {project_filter}%")

            if conditions:
                q += " WHERE " + " AND ".join(conditions)

            q += " ORDER BY interviews.id DESC"

            cursor.execute(q, tuple(p_params))

            # Clear existing items
            self.tree.delete(*self.tree.get_children())

            for rec in cursor.fetchall():
                # rec[0] = interview id
                # rec[1] = full_name (from users table)
                # rec[2] = summary
                # rec[3] = timestamp

                interview_id = rec[0]
                interviewer_name = rec[1] if rec[1] else "Unknown"  # Handle deleted users
                summary_text = rec[2]
                timestamp = rec[3]

                ep = self.extract_field(summary_text, "EP Name")
                pr = self.extract_field(summary_text, "Project")
                tm = self.extract_field(summary_text, "Timeline")

                # Insert the name (interviewer_name) instead of the ID
                self.tree.insert("", tk.END, values=(interview_id, ep, pr, tm, interviewer_name, timestamp))

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_selected(self):
        sel = self.tree.focus()
        if not sel: return messagebox.showerror("Error", "Select an interview to delete")
        val = self.tree.item(sel, 'values')

        if messagebox.askyesno("Confirm Delete",
                               f"Are you sure you want to delete the record for {val[1]} (ID: {val[0]})?"):
            conn, cursor = get_connection()
            try:
                # Remove associated image if exists
                cursor.execute("SELECT summary FROM interviews WHERE id=%s", (val[0],))
                res = cursor.fetchone()
                if res:
                    img_path = self.extract_field(res[0], "Image Path")
                    if img_path and os.path.exists(img_path):
                        os.remove(img_path)

                cursor.execute("DELETE FROM interviews WHERE id=%s", (val[0],))
                conn.commit()
                messagebox.showinfo("Success", "Record deleted.")
                self.update_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                cursor.close();
                conn.close()

    def view_summary(self, event):
        sel = self.tree.focus()
        if not sel: return
        val = self.tree.item(sel, 'values')
        record_id = val[0]

        # 1. Clear Main Frame
        for w in self.main_frame.winfo_children(): w.destroy()

        # 2. Header with Back Button
        header = ctk.CTkFrame(self.main_frame, fg_color="white")
        header.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(header, text="← Back to Dashboard", width=120, fg_color="gray",
                      command=self.update_dashboard).pack(side="left")
        ctk.CTkLabel(header, text=f"Interview Summary (ID: {record_id})", font=("Arial", 20, "bold"),
                     text_color="black").pack(side="left", padx=20)

        # 3. Content Container (Scrollable)
        content = ctk.CTkScrollableFrame(self.main_frame, fg_color="white")
        content.pack(fill="both", expand=True, padx=20, pady=10)

        # 4. Fetch Summary Data
        conn, cursor = get_connection()
        summary_text = ""
        try:
            cursor.execute("SELECT summary FROM interviews WHERE id=%s", (record_id,))
            res = cursor.fetchone()
            if res: summary_text = res[0]
        finally:
            cursor.close();
            conn.close()

        # 5. Parse Text & Image
        image_path = None
        clean_lines = []

        for line in summary_text.split("\n"):
            if line.startswith("Image Path:"):
                image_path = line.split(":", 1)[1].strip()
                continue
            if line.startswith("CV Path:"):
                continue
            clean_lines.append(line)

        clean_text = "\n".join(clean_lines)

        # 6. Display Image
        if image_path and os.path.exists(image_path):
            try:
                pil_img = Image.open(image_path)
                h_percent = (300 / float(pil_img.size[1]))
                w_size = int((float(pil_img.size[0]) * float(h_percent)))
                if w_size > 500:
                    w_percent = (500 / float(pil_img.size[0]))
                    h_size = int((float(pil_img.size[1]) * float(w_percent)))
                    pil_img = pil_img.resize((500, h_size), Image.Resampling.LANCZOS)
                else:
                    pil_img = pil_img.resize((w_size, 300), Image.Resampling.LANCZOS)

                ctk_img = ctk.CTkImage(light_image=pil_img, size=pil_img.size)
                ctk.CTkLabel(content, text="", image=ctk_img).pack(anchor="w", pady=(10, 20))
            except Exception as e:
                ctk.CTkLabel(content, text=f"[Error loading image: {e}]", text_color="red").pack(anchor="w")

        # 7. Display Text
        text_box = ctk.CTkTextbox(content, font=("Arial", 14), height=400, border_width=2, border_color="#B0B0B0",
                                  fg_color="#F9F9F9", text_color="black")
        text_box.pack(fill="both", expand=True)
        text_box.insert("1.0", clean_text)
        text_box.configure(state="disabled")

    def switch_to_interviewer_mode(self):
        self.controller.show_frame("AdminInterviewerModeFrame")

    @staticmethod
    def extract_field(text, field):
        for line in text.split("\n"):
            if line.startswith(f"{field}:"): return line.split(":", 1)[1].strip()
        return ""