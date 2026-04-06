import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from sidebar_base import BaseSidebarFrame


class DashboardFrame(BaseSidebarFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # --- FONTS ---
        self.header_font = ctk.CTkFont(family="Arial", size=24, weight="bold")
        self.sub_font = ctk.CTkFont(family="Arial", size=14, weight="bold")
        self.card_font = ctk.CTkFont(family="Arial", size=20, weight="bold")
        self.normal_font = ctk.CTkFont(family="Arial", size=12)

        # --- Sidebar Buttons ---
        self.add_sidebar_button("DASHBOARD", self.update_dashboard)
        self.add_sidebar_button("INTERVIEW SHEET", self.open_interview)
        self.add_sidebar_button("PROFILE", self.open_profile_settings)
        self.add_sidebar_button("LOG OUT", self.logout, side="bottom")

        # --- Main Content Area ---
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.main_frame.pack(side="left", fill="both", expand=True)

    # --- Navigation ---
    def update_dashboard(self):
        self.set_button_state("DASHBOARD")
        self.clear_main()
        self.build_dashboard_ui()

    def open_interview(self):
        self.set_button_state("INTERVIEW SHEET")
        from interview_form import InterviewForm
        self.clear_main()
        user_id = self.controller.current_user[0] if self.controller.current_user else None
        InterviewForm(self.main_frame, user_id)

    def open_profile_settings(self):
        self.set_button_state("PROFILE")
        self.clear_main()
        self.controller.show_frame("ProfileFrame")

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def build_dashboard_ui(self):
        user = self.controller.current_user
        name = user[1] if user else "Guest"

        # Welcome
        ctk.CTkLabel(self.main_frame, text="DASHBOARD", font=self.header_font, text_color="black").pack(anchor="nw",
                                                                                                        padx=20,
                                                                                                        pady=(20, 5))
        ctk.CTkLabel(self.main_frame, text=f"Welcome, {name}!", font=self.normal_font, text_color="gray").pack(
            anchor="nw", padx=20, pady=(0, 20))

        # Stats Card
        total_interviews = self.get_total_interviews()
        card_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E70DB", height=120, corner_radius=10)
        card_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(card_frame, text="🎉 Congratulations!", font=self.card_font, text_color="white").pack(pady=(15, 0))
        ctk.CTkLabel(card_frame, text=f"You have conducted {total_interviews} interviews", font=self.sub_font,
                     text_color="white").pack(pady=(5, 15))

        # --- Filters Section ---
        filter_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
        filter_frame.pack(fill="x", padx=20, pady=(10, 5))

        # 1. Search Entry
        self.search_entry = ctk.CTkEntry(filter_frame, width=250, placeholder_text="Enter EP Name")
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.apply_filters())
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind('<Return>', lambda event: self.apply_filters())

        # 2. Project Dropdown
        ctk.CTkLabel(filter_frame, text="Project:", text_color="black", font=self.normal_font).pack(side="left",
                                                                                                    padx=(10, 5))
        self.project_filter_var = tk.StringVar(value="All Projects")
        projects = ["All Projects", "Aquatica", "Green Leaders", "Global Classroom", "On The Map", "Rooted"]
        self.project_filter_combo = ctk.CTkComboBox(filter_frame, variable=self.project_filter_var, values=projects,
                                                    state="readonly", width=150, command=lambda e: self.apply_filters())
        self.project_filter_combo.pack(side="left")

        # 3. Apply Button
        ctk.CTkButton(filter_frame, text="Apply", fg_color="#0d6efd", width=80, command=self.apply_filters).pack(
            side="left", padx=10)

        # 4. Reset Button
        ctk.CTkButton(filter_frame, text="Reset", fg_color="gray", width=60, command=self.reset_filters).pack(
            side="left")

        # Treeview
        ctk.CTkLabel(self.main_frame, text="Recent Interviews (Double-click to Edit)", font=self.sub_font,
                     text_color="black").pack(anchor="nw", padx=20, pady=(10, 5))

        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))

        columns = ("ID", "EP Name", "Project", "Timeline", "Date Entered")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.column("ID", width=40)

        self.tree.bind("<Double-1>", self.edit_selected_interview)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        self.populate_recent_activity()

        ctk.CTkButton(self.main_frame, text="View All Interviews", fg_color="#0d6efd", width=200,
                      command=self.view_all_interviews).pack(padx=20, pady=(0, 20))

    # --- Logic Helpers ---
    def get_total_interviews(self):
        if self.controller.current_user is None: return 0
        conn, cursor = get_connection()
        try:
            cursor.execute("SELECT COUNT(*) FROM interviews WHERE user_id = %s", (self.controller.current_user[0],))
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
        self.populate_recent_activity(s, p)

    def populate_recent_activity(self, search_term="", project_filter=""):
        if not self.controller.current_user: return
        conn, cursor = get_connection()
        try:
            q = "SELECT id, summary, timestamp FROM interviews WHERE user_id = %s"
            params = [self.controller.current_user[0]]

            if search_term:
                q += " AND summary LIKE %s"
                params.append(f"%EP Name: {search_term}%")

            if project_filter:
                q += " AND summary LIKE %s"
                params.append(f"%Project: {project_filter}%")

            q += " ORDER BY id DESC LIMIT 5"
            cursor.execute(q, tuple(params))
            records = cursor.fetchall()

            self.tree.delete(*self.tree.get_children())
            for rec in records:
                summary = rec[1]
                ep = self.extract_field(summary, "EP Name")
                proj = self.extract_field(summary, "Project")
                time = self.extract_field(summary, "Timeline").replace("→", " to ").strip()
                self.tree.insert("", tk.END, values=(rec[0], ep, proj, time, rec[2]))
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close();
            conn.close()

    @staticmethod
    def extract_field(summary_text, field_name):
        for line in summary_text.split("\n"):
            if line.startswith(f"{field_name}:"): return line.split(":", 1)[1].strip()
        return ""

    def edit_selected_interview(self, event):
        sel = self.tree.focus()
        if not sel: return
        rec_id = self.tree.item(sel, 'values')[0]
        self.clear_main()
        from interview_form import InterviewForm
        InterviewForm(self.main_frame, self.controller.current_user[0], record_id=rec_id)

    def view_all_interviews(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="ALL RECORDED INTERVIEWS", font=self.header_font, text_color="black").pack(
            anchor="nw", padx=20, pady=(20, 5))

        cols = ("ID", "EP Name", "Project", "Timeline", "Date Entered")
        tree = ttk.Treeview(self.main_frame, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True, padx=20)

        conn, cursor = get_connection()
        try:
            uid = self.controller.current_user[0]
            cursor.execute("SELECT id, summary, timestamp FROM interviews WHERE user_id=%s ORDER BY id DESC", (uid,))
            for rec in cursor.fetchall():
                ep = self.extract_field(rec[1], "EP Name")
                proj = self.extract_field(rec[1], "Project")
                tm = self.extract_field(rec[1], "Timeline")
                tree.insert("", tk.END, values=(rec[0], ep, proj, tm, rec[2]))
        finally:
            cursor.close();
            conn.close()

        ctk.CTkButton(self.main_frame, text="Back", fg_color="gray", command=self.update_dashboard).pack(pady=10)