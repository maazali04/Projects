from src.ui_components import (
    Sidebar,
    DashboardView,
    StudentsView,
    ClassesView,
    FeeRecordsView,
    AttendanceView,
    ExaminationView,
    SettingsView,
    ThemeManager,
    AssetManager,
)
from src.database import DatabaseManager
import customtkinter as ctk


class CollegeManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()

        self.title("College Management System")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        self.state("zoomed")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color="#F2F5F5")

        self.theme = ThemeManager()
        self.assets = AssetManager()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_content = ctk.CTkFrame(
            self, fg_color=self.theme.colors["bg_main"], corner_radius=0
        )
        self.main_content.grid(row=0, column=1, sticky="nsew")

        self.sidebar = Sidebar(self, self.theme, self.assets, self.handle_view_change)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.sidebar.handle_click("Dashboard")

    def handle_view_change(self, view_name):
        """Standardized clearing and rendering logic"""
        self.clear_main_content()
        self.sidebar.set_active_tab(view_name)

        render_methods = {
            "Dashboard": self.render_dashboard,
            "Students": self.render_students_view,
            "Classes": self.render_classes_view,
            "Fee Records": self.render_fee_records_view,
            "Examination": self.render_examination_view,
            "Attendance": self.render_attendance_view,
            "Settings": self.render_settings_view,
        }

        if view_name in render_methods:
            render_methods[view_name]()

    def render_dashboard(self):
        self.clear_main_content()
        recent_logs = self.db.get_recent_activities(limit=5)
        print(f"DEBUG: Activities found in DB: {recent_logs}")
        print(f"DEBUG: Type of data: {type(recent_logs)}")
        stats = self.db.get_dashboard_stats()

        dashboard = DashboardView(
            self.main_content, self, stats_data=stats, activity_data=recent_logs
        )
        dashboard.pack(fill="both", expand=True)

    def render_students_view(self):
        self.clear_main_content()

        students = self.db.get_all_students()

        student_view = StudentsView(self.main_content, self, data_list=students)
        student_view.pack(fill="both", expand=True)

    def render_classes_view(self):
        self.clear_main_content()

        real_data = self.db.get_all_classes()

        class_view = ClassesView(self.main_content, self, data_dict=real_data)
        class_view.pack(fill="both", expand=True)

    def render_fee_records_view(self):
        self.clear_main_content()
        real_fee_data = self.db.get_fee_records()

        fee_view = FeeRecordsView(
            self.main_content, controller=self, data_dict=real_fee_data
        )
        fee_view.pack(fill="both", expand=True)

    def render_attendance_view(self):
        self.clear_main_content()

        AttendanceView(self.main_content, self).pack(fill="both", expand=True)

    def render_examination_view(self):
        self.clear_main_content()
        real_exam_data = self.db.get_examination_data()

        exam_view = ExaminationView(self.main_content, self, data_dict=real_exam_data)
        exam_view.pack(fill="both", expand=True)

    def render_settings_view(self):
        self.clear_main_content()
        SettingsView(self.main_content, self).pack(fill="both", expand=True)

    def clear_main_content(self):
        """Helper to clear the stage"""
        for widget in self.main_content.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = CollegeManagementApp()
    app.mainloop()
