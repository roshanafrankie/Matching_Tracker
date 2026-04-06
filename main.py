import customtkinter as ctk
import tkinter as tk
import os
from ctypes import windll, byref, sizeof, c_int  # REQUIRED FOR THE FIX

# --- Imports ---
from login_frame import LoginFrame
from register_frame import RegisterFrame
from reset_password_frame import ResetPasswordFrame

from dashboard_frame import DashboardFrame
from profile_frame import ProfileFrame
from admin_dashboard_frame import AdminDashboardFrame
from admin_interviewer_mode_frame import AdminInterviewerModeFrame

# --- GLOBAL SETTINGS ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#FFFFFF")  # Force white using Hex Code

        self.title("Interview Tracker")
        self.geometry("1100x800")
        self.resizable(True, True)
        self.current_user = None

        # --- THE "BLACK FLASH" FIX (Windows Only) ---
        # This tells Windows DWM (Desktop Window Manager) to force Light Mode
        # for this window's title bar and background.
        try:
            # Get the window handle (HWND)
            self.update()
            hwnd = windll.user32.GetParent(self.winfo_id())

            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20 (or 35 on newer Win11)
            # We set it to '0' (False) to force Light Mode
            value = c_int(0)
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, byref(value), sizeof(value))
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(value), sizeof(value))
        except Exception as e:
            print(f"Could not apply Windows DWM fix: {e}")
        # ---------------------------------------------

        # --- Custom Logo Logic ---
        try:
            if os.path.exists("Rocket.ico"):
                self.iconbitmap("Rocket.ico")
            elif os.path.exists("Rocket.png"):
                icon_img = tk.PhotoImage(file="Rocket.png")
                self.iconphoto(False, icon_img)
        except Exception as e:
            print(f"Could not load custom logo: {e}")

        container = tk.Frame(self, bg="white")
        container.pack(fill="both", expand=True)

        self.frames = {}

        frame_classes = (
            LoginFrame,
            RegisterFrame,
            ResetPasswordFrame,
            DashboardFrame,
            ProfileFrame,
            AdminDashboardFrame,
            AdminInterviewerModeFrame
        )

        for F in frame_classes:
            try:
                frame = F(parent=container, controller=self)
                self.frames[F.__name__] = frame
                frame.place(relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error loading {F.__name__}: {e}")

        self.show_frame("LoginFrame")

    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)
        if frame:
            frame.lift()
            if hasattr(frame, "on_show"):
                frame.on_show()
            elif hasattr(frame, "update_dashboard"):
                frame.update_dashboard()
        else:
            print(f"Error: Frame '{frame_name}' not found.")


if __name__ == "__main__":
    app = App()
    app.mainloop()