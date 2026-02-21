from datetime import datetime
import customtkinter as ctk
from PIL import Image
import os
from tkinter import font
import pandas as pd
from tkinter import filedialog, messagebox
import sys

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ThemeManager:
    def __init__(self):

        self.colors = {
            "bg_sidebar": "#FFFFFF",
            "bg_main": "#F2F5F5",
            "bg_card": "#FFFFFF",
            "bg_hover": "#F3F4F6",
            "text_primary": "#111827",
            "text_secondary": "#4B5563",
            "text_muted": "#9CA3AF",
            "text_accent": "#2563EB",
            "accent": "#2563EB",
            "border": "#DBD1D1",
            "danger": "#E11D48",
            "success": "#10B981",
            "icon_bg": "#F3F4F6",
        }
        self.font_family = self._detect_font()

        self.fonts = {
            "display_large": ctk.CTkFont(
                family=self.font_family, size=32, weight="bold"
            ),
            "h1": ctk.CTkFont(family=self.font_family, size=24, weight="bold"),
            "h2": ctk.CTkFont(family=self.font_family, size=20, weight="bold"),
            "h3": ctk.CTkFont(family=self.font_family, size=16, weight="bold"),
            "title": ctk.CTkFont(family=self.font_family, size=22),
            "subtitle": ctk.CTkFont(family=self.font_family, size=14, weight="normal"),
            "table": ctk.CTkFont(family=self.font_family, size=13),
            "body_large": ctk.CTkFont(family=self.font_family, size=15),
            "body_main": ctk.CTkFont(family=self.font_family, size=14),
            "body_strong": ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
            "body_strong_large": ctk.CTkFont(
                family=self.font_family, size=15, weight="bold"
            ),
            "body_small": ctk.CTkFont(family=self.font_family, size=12),
            "label_caps": ctk.CTkFont(family=self.font_family, size=12, weight="bold"),
            "button_text": ctk.CTkFont(family=self.font_family, size=13, weight="bold"),
            "caption": ctk.CTkFont(family=self.font_family, size=11, weight="normal"),
        }

    def _detect_font(self):
        """Detects best available font"""
        available = font.families()
        for f in ["Inter", "Inter Regular", "Segoe UI", "Helvetica", "Arial"]:
            if f in available:
                return f
        return "sans-serif"


class AssetManager:
    """Handles all image loading, recoloring, and caching."""

    @staticmethod
    def recolor_icon(image_path, color="#1f538d"):
        """
        Takes a monochromatic icon (PNG) and changes its color while
        preserving transparency.
        """
        try:
            img = Image.open(image_path).convert("RGBA")
            alpha = img.getchannel("A")
            new_img = Image.new("RGBA", img.size, color)
            new_img.putalpha(alpha)
            return ctk.CTkImage(light_image=new_img, dark_image=new_img, size=img.size)
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None

    @staticmethod
    def get_sidebar_icon(name, theme_manager):
        """Helper to get a standard sidebar icon with the correct theme color."""
        path = resource_path(f"assets/icons/{name}.png")
        return AssetManager.recolor_icon(path, theme_manager.colors["accent"])


class ComponentFactory:
    @staticmethod
    def create_header_bar(parent, theme, title, subtitle):
        """
        Generates a professional header bar.
        Note: We remove widget.destroy() from here to keep this a 'pure' factory.
        The Page class should handle its own clearing logic.
        """
        header_bar = ctk.CTkFrame(
            parent,
            height=80,
            corner_radius=0,
            fg_color=theme.colors["bg_card"],
        )
        header_bar.pack(fill="x", side="top")
        header_bar.pack_propagate(False)

        bottom_border = ctk.CTkFrame(
            header_bar, height=2, fg_color=theme.colors["border"], corner_radius=0
        )
        bottom_border.pack(side="bottom", fill="x")

        header_content = ctk.CTkFrame(header_bar, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=(31, 32))

        text_group = ctk.CTkFrame(header_content, fg_color="transparent")
        text_group.pack(side="left", fill="y", pady=13)

        welcome_label = ctk.CTkLabel(
            text_group,
            text=title,
            font=theme.fonts["title"],
            text_color=theme.colors["text_primary"],
        )
        welcome_label.pack(anchor="w", pady=(0, 2))

        sub_text = ctk.CTkLabel(
            text_group,
            text=subtitle,
            font=theme.fonts["body_main"],
            text_color=theme.colors["text_secondary"],
        )
        sub_text.pack(anchor="w")

        return header_bar

    @staticmethod
    def create_separator(
        parent, theme, px_height=1, horizontal_margin=24, vertical_margin=0
    ):
        """Creates a subtle horizontal divider line"""
        line = ctk.CTkFrame(
            parent, height=px_height, fg_color=theme.colors["border"], corner_radius=0
        )
        line.pack_propagate(False)
        line.pack(fill="x", padx=horizontal_margin, pady=vertical_margin)
        return line

    @staticmethod
    def create_stat_card(parent, theme, asset_manager, stat_data):
        """
        Full implementation of a professional dashboard stat card.
        stat_data keys: "title", "value", "icon", "trend", "is_up"
        """

        card = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            height=140,
            corner_radius=12,
            border_width=2,
            border_color=theme.colors["border"],
        )
        card.pack_propagate(False)

        def on_hover(e):
            card.configure(border_color=theme.colors["accent"])

        def on_leave(e):
            card.configure(border_color=theme.colors["border"])

        ComponentFactory.bind_hover_recursively(card, on_hover, on_leave)

        left_side = ctk.CTkFrame(card, fg_color="transparent")
        left_side.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        img_path = resource_path(f"assets/icons/{stat_data['icon']}")
        icon_img = asset_manager.recolor_icon(img_path, theme.colors["text_secondary"])

        icon_label = ctk.CTkLabel(left_side, text="", image=icon_img)
        icon_label.pack(anchor="w")

        title_label = ctk.CTkLabel(
            left_side,
            text=stat_data["title"],
            font=theme.fonts["body_small"],
            text_color=theme.colors["text_secondary"],
        )
        title_label.pack(anchor="w", pady=(10, 0))

        value_label = ctk.CTkLabel(
            left_side,
            text=stat_data["value"],
            font=theme.fonts["h1"],
            text_color=theme.colors["text_primary"],
        )
        value_label.pack(anchor="w")

        trend_color = "#10B981" if stat_data["is_up"] else "#EF4444"
        trend_bg = "#ECFDF5" if stat_data["is_up"] else "#FEF2F2"

        badge = ctk.CTkFrame(
            card,
            fg_color=trend_bg,
            corner_radius=15,
            height=28,
        )
        badge.pack(side="right", anchor="n", padx=15, pady=20)

        trend_label = ctk.CTkLabel(
            badge,
            text=stat_data["trend"],
            font=theme.fonts["body_strong"],
            text_color=trend_color,
            padx=10,
        )
        trend_label.pack()

        return card

    @staticmethod
    def create_activity_item(parent, theme, asset_manager, data):
        """Creates a single row for the Recent Activity section"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", padx=24, pady=20)

        img_path = resource_path(f"assets/icons/{data['icon']}")
        icon_img = asset_manager.recolor_icon(img_path, theme.colors["text_secondary"])

        icon_circle = ctk.CTkLabel(
            item_frame,
            text="",
            image=icon_img,
            width=40,
            height=40,
            fg_color="#E0F2FE",
            corner_radius=20,
        )
        icon_circle.pack(side="left")

        text_container = ctk.CTkFrame(item_frame, fg_color="transparent")
        text_container.pack(side="left", padx=15)

        ctk.CTkLabel(
            text_container,
            text=data["title"],
            font=theme.fonts["body_strong"],
            text_color=theme.colors["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_container,
            text=data["sub"],
            font=theme.fonts["body_small"],
            text_color=theme.colors["text_secondary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            item_frame,
            text=data["time"],
            font=theme.fonts["body_small"],
            text_color=theme.colors["text_secondary"],
        ).pack(side="right", anchor="n", pady=5)

        return item_frame

    @staticmethod
    def create_action_card(
        parent, theme, asset_manager, title, subtitle, icon, bg_color, command=None
    ):
        """Creates a clickable action card for the Quick Actions section"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            height=80,
            corner_radius=12,
            border_width=1,
            border_color=theme.colors["border"],
            cursor="hand2",
        )
        card.pack(fill="x", pady=(0, 10))
        card.pack_propagate(False)

        img_path = resource_path(f"assets/icons/{icon}")
        icon_img = asset_manager.recolor_icon(img_path, theme.colors["text_secondary"])

        icon_circle = ctk.CTkLabel(
            card,
            text="",
            image=icon_img,
            width=40,
            height=40,
            fg_color=bg_color,
            corner_radius=20,
        )
        icon_circle.pack(side="left", padx=(20, 15), pady=15)

        text_stack = ctk.CTkFrame(card, fg_color="transparent")
        text_stack.pack(side="left", fill="y", pady=15)

        ctk.CTkLabel(
            text_stack,
            text=title,
            font=theme.fonts["body_strong"],
            text_color=theme.colors["text_primary"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_stack,
            text=subtitle,
            font=theme.fonts["body_small"],
            text_color=theme.colors["text_secondary"],
        ).pack(anchor="w")

        def on_e(e):
            card.configure(fg_color="#F8FAFC", border_color=theme.colors["accent"])

        def on_l(e):
            card.configure(fg_color="#FFFFFF", border_color=theme.colors["border"])

        def trigger_command(event):
            if command:
                command()

        ComponentFactory.bind_hover_recursively(card, on_e, on_l)

        card.bind("<Button-1>", trigger_command)
        for child in card.winfo_children():
            child.bind("<Button-1>", trigger_command)
            child.configure(cursor="hand2")
        return card

    @staticmethod
    def bind_hover_recursively(widget, enter_func, leave_func, root_card=None):
        """
        Improved recursive hover that prevents flickering and 'stuck' colors.
        root_card: The main container (the Card) we want to track.
        """
        if root_card is None:
            root_card = widget

        def on_enter(event):
            enter_func(event)

        def on_leave(event):
            root_card.after(10, lambda: check_if_really_left(event))

        def check_if_really_left(event):
            x, y = root_card.winfo_pointerxy()
            target = root_card.winfo_containing(x, y)

            is_inside = False
            if target == root_card:
                is_inside = True
            else:
                parent = target
                while parent:
                    if parent == root_card:
                        is_inside = True
                        break
                    parent = parent.master if hasattr(parent, "master") else None

            if not is_inside:
                leave_func(event)

        widget.bind("<Enter>", on_enter, add="+")
        widget.bind("<Leave>", on_leave, add="+")

        for child in widget.winfo_children():
            ComponentFactory.bind_hover_recursively(
                child, enter_func, leave_func, root_card
            )

    @staticmethod
    def create_data_table(
        parent,
        theme,
        headers,
        rows,
        is_attendance=False,
        action_command=None,
        command_text=None,
    ):
        current_theme = theme

        table_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="#FFFFFF",
            border_width=0,
            border_color=theme.colors["border"],
            corner_radius=15,
        )
        table_frame.pack(fill="both", expand=True, padx=0.6, pady=(0, 0))

        for i in range(len(headers)):
            table_frame.grid_columnconfigure(i, weight=2 if i == 1 else 1)

        header_bg = "#F8FAFC"
        for col, text in enumerate(headers):
            h_frame = ctk.CTkFrame(
                table_frame, fg_color=header_bg, corner_radius=0, height=45
            )
            h_frame.grid(row=0, column=col, sticky="nsew")

            ctk.CTkLabel(
                h_frame,
                text=text,
                font=("Inter", 13, "bold"),
                text_color=theme.colors["text_secondary"],
            ).pack(side="left", padx=15, pady=10)
        if not rows:
            empty_cell = ctk.CTkFrame(table_frame, fg_color="transparent", height=100)
            empty_cell.grid(row=1, column=0, columnspan=len(headers), sticky="nsew")

            ctk.CTkLabel(
                empty_cell,
                text="No records found in database",
                font=("Inter", 13, "italic"),
                text_color=theme.colors["text_secondary"],
            ).pack(expand=True, pady=20)
        else:
            for row_idx, data in enumerate(rows):
                current_grid_row = (row_idx * 2) + 1
                row_cells = []

                row_values = []
                for h in headers:
                    if h == "Exam Name":
                        row_values.append(data.get("exam_name", "---"))

                    elif h == "Class":
                        row_values.append(data.get("class_name", "---"))

                    elif h == "Date":
                        row_values.append(data.get("exam_date", "---"))

                    elif h == "Room Number":
                        row_values.append(data.get("room_no", "TBD"))

                    elif h in ["Class Name", "Student Name", "Subject Name"]:
                        row_values.append(data.get("name", "---"))
                    elif h == "Father Name":
                        row_values.append(data.get("father_name", "---"))
                    elif h in ["ID", "Invoice ID", "Subject Code"]:
                        row_values.append(data.get("id", "---"))
                    elif h == "Capacity":
                        row_values.append(data.get("capacity", "0/0"))
                    elif h == "Room/Hall":
                        row_values.append(data.get("room", "---"))
                    elif h == "Shift":
                        row_values.append(data.get("shift", "---"))
                    elif h == "Status":
                        row_values.append(data.get("status", "Pending"))
                    elif h == "Actions":
                        row_values.append("Actions")
                    else:
                        row_values.append(data.get("class_name", "---"))

                for col_idx, val in enumerate(row_values):
                    cell = ctk.CTkFrame(table_frame, fg_color="transparent", height=50)
                    cell.grid(row=current_grid_row, column=col_idx, sticky="nsew")
                    row_cells.append(cell)

                    if headers[col_idx] == "Capacity":
                        container = ctk.CTkFrame(cell, fg_color="transparent")
                        container.pack(side="left", padx=15, pady=8)

                        ctk.CTkLabel(container, text=val, font=("Inter", 11)).pack(
                            anchor="w"
                        )

                        try:
                            if val and "/" in str(val):
                                clean_val = str(val).replace(" ", "")
                                curr, total = map(int, clean_val.split("/"))
                                prog = curr / total if total > 0 else 0
                                color = "#EF4444" if prog > 0.9 else "#10B981"

                                pb = ctk.CTkProgressBar(
                                    container,
                                    height=6,
                                    corner_radius=10,
                                    progress_color=color,
                                    width=200,
                                    fg_color="#E2E8F0",
                                )
                                pb.set(prog)
                                pb.pack(fill="x", pady=(2, 0))
                            else:
                                ctk.CTkLabel(container, text="N/A").pack()
                        except Exception as e:
                            print(f"Error rendering progress bar: {e}")

                    elif headers[col_idx] == "Status":
                        if is_attendance:
                            status_menu = ctk.CTkOptionMenu(
                                cell,
                                values=["Present", "Absent", "Leave"],
                                width=100,
                                height=28,
                                corner_radius=6,
                                fg_color="#F8FAFC",
                                text_color="#1F2937",
                                button_color="#F1F5F9",
                                button_hover_color="#E2E8F0",
                                font=("Inter", 11),
                            )
                            status_menu.set(val)
                            status_menu.pack(side="left", pady=10, padx=15)
                        else:
                            status_color = (
                                "#10B981"
                                if val == "Paid"
                                else "#EF4444"
                                if val == "Pending"
                                else "#334155"
                            )
                            ctk.CTkLabel(
                                cell,
                                text=str(val),
                                font=("Inter", 12, "bold"),
                                text_color=status_color,
                            ).pack(side="left", padx=15, pady=12)
                    elif val == "Actions":
                        is_delete = command_text == "Delete"

                        btn_text = "Delete" if is_delete else "→"
                        btn_fg = "#FEE2E2" if is_delete else "transparent"
                        btn_text_col = (
                            "#DC2626" if is_delete else current_theme.colors["accent"]
                        )
                        btn_hover = "#FCA5A5" if is_delete else "#F1F5F9"
                        btn_font = (
                            ("Inter", 10, "bold")
                            if is_delete
                            else ("Inter", 18, "bold")
                        )

                        action_btn = ctk.CTkButton(
                            cell,
                            text=btn_text,
                            width=40,
                            height=30,
                            corner_radius=8,
                            fg_color=btn_fg,
                            text_color=btn_text_col,
                            font=btn_font,
                            hover_color=btn_hover,
                            anchor="center",
                            command=lambda r=data: (
                                action_command(r)
                                if action_command
                                else print(f"Clicked {r}")
                            ),
                        )
                        action_btn.pack(side="left", padx=15, pady=10)

                        action_btn.configure(cursor="hand2")

                    else:
                        ctk.CTkLabel(
                            cell,
                            text=str(val),
                            font=("Inter", 13),
                            text_color="#334155",
                        ).pack(side="left", padx=15, pady=12)

                sep = ctk.CTkFrame(
                    table_frame, height=2, fg_color=theme.colors["border"]
                )
                sep.grid(
                    row=current_grid_row + 1,
                    column=0,
                    columnspan=len(headers),
                    sticky="ew",
                    padx=15,
                )

                def make_hover(cells):
                    def on_e(e):
                        for c in cells:
                            c.configure(fg_color="#F1F5F9")

                    def on_l(e):
                        for c in cells:
                            c.configure(fg_color="transparent")

                    return on_e, on_l

                on_enter, on_leave = make_hover(row_cells)
                for cell in row_cells:
                    ComponentFactory.bind_hover_recursively(cell, on_enter, on_leave)

        return table_frame

    @staticmethod
    def create_search_bar(parent, theme, placeholder):
        """Ultra-clean search bar using only the Entry widget to avoid nesting bugs"""
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=40,
            corner_radius=10,
            border_width=1,
            fg_color="#F8FAFC",
            border_color=theme.colors["border"],
            text_color=theme.colors["text_primary"],
            placeholder_text_color=theme.colors["text_secondary"],
            font=theme.fonts["body_small"],
        )

        def on_e(e):
            entry.configure(border_color=theme.colors["accent"])

        def on_l(e):
            entry.configure(border_color=theme.colors["border"])

        entry.bind("<Enter>", on_e)
        entry.bind("<Leave>", on_l)

        return entry

    @staticmethod
    def create_table_row(parent, theme, data, is_header=False):
        """Creates a single row in the data table"""
        row_frame = ctk.CTkFrame(
            parent,
            fg_color="#F8FAFC" if is_header else "transparent",
            height=50,
            corner_radius=0,
        )
        row_frame.pack(fill="x")

        col_configs = [
            (data[0], 0.1),
            (data[1], 0.3),
            (data[2], 0.25),
            (data[3], 0.15),
            (data[4], 0.2),
        ]

        for text, weight in col_configs:
            cell = ctk.CTkFrame(row_frame, fg_color="transparent")
            cell.pack(side="left", fill="both", expand=True)

            if text == "Actions" and not is_header:
                btn = ctk.CTkButton(
                    cell, text="Edit", width=60, height=26, corner_radius=6
                )
                btn.pack(pady=12)
            else:
                lbl = ctk.CTkLabel(
                    cell,
                    text=text,
                    font=(
                        theme.fonts["body_strong"]
                        if is_header
                        else theme.fonts["body_small"]
                    ),
                    text_color=theme.colors["text_primary"],
                )
                lbl.pack(side="left", padx=20, pady=12)

        if not is_header:

            def on_e(e):
                row_frame.configure(fg_color="#F1F5F9")

            def on_l(e):
                row_frame.configure(fg_color="transparent")

            ComponentFactory.bind_hover_recursively(row_frame, on_e, on_l)

        return row_frame


class ProfileDetailModal(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.title("Add New Student")
        self.geometry("700x600")
        self.minsize(700, 600)
        self.controller = controller
        self.db = controller.db

        self.attributes("-topmost", True)

        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure((0, 1), weight=1)

        header = ctk.CTkLabel(
            self, text="Student Registration", font=("Inter", 22, "bold")
        )
        header.grid(row=0, column=0, columnspan=2, pady=(30, 20))

        self.entries = {}

        fields = [
            ("Full Name", "name", 1, 0),
            ("Roll Number", "roll_no", 1, 1),
            ("Class Name", "class_name", 2, 0),
            ("Father's Name", "father_name", 2, 1),
            ("Joining Date", "joining_date", 3, 0),
        ]

        for label_text, key, r, c in fields:
            container = ctk.CTkFrame(self, fg_color="transparent")
            container.grid(row=r, column=c, padx=20, pady=10, sticky="ew")

            ctk.CTkLabel(container, text=label_text, font=("Inter", 12, "bold")).pack(
                anchor="w"
            )
            entry = ctk.CTkEntry(
                container, height=40, placeholder_text=f"Enter {label_text.lower()}"
            )
            entry.pack(fill="x", pady=(5, 0))
            self.entries[key] = entry

        gender_container = ctk.CTkFrame(self, fg_color="transparent")
        gender_container.grid(
            row=4, column=0, columnspan=2, padx=20, pady=10, sticky="ew"
        )

        ctk.CTkLabel(gender_container, text="Gender", font=("Inter", 12, "bold")).pack(
            anchor="w"
        )
        self.gender_var = ctk.StringVar(value="Male")
        self.gender_menu = ctk.CTkOptionMenu(
            gender_container,
            values=["Male", "Female", "Other"],
            variable=self.gender_var,
            height=40,
        )
        self.gender_menu.pack(fill="x", pady=(5, 0))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=40, padx=20, sticky="ew")

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            height=45,
            fg_color="#64748B",
            command=self.destroy,
        )
        self.cancel_btn.pack(side="left", padx=10, expand=True, fill="x")

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Student",
            height=45,
            fg_color="#10B981",
            hover_color="#059669",
            command=self.save_data,
        )
        self.save_btn.pack(side="left", padx=10, expand=True, fill="x")

    def save_data(self):
        name = self.entries["name"].get().strip()
        roll = self.entries["roll_no"].get().strip()
        cls = self.entries["class_name"].get().strip()
        f_name = self.entries["father_name"].get().strip()
        gender = self.gender_var.get()

        if not name or not roll or not cls:
            messagebox.showwarning(
                "Input Required",
                "Please fill in all required fields (Name, Roll No, and Class).",
            )
            return

        if not self.controller.db.class_exists(cls):
            messagebox.showerror(
                "Invalid Class",
                f"The class '{cls}' does not exist.\n\nPlease create the class in the 'Classes' tab first.",
                parent=self,
            )
            return

        success, message = self.controller.db.add_student(
            name, f_name, cls, roll, gender
        )

        if success:
            messagebox.showinfo(
                "Success",
                f"Student {name} has been registered successfully!",
                parent=self,
            )
            self.controller.handle_view_change("Students")
            self.destroy()
            self.controller.db.log_event(
                "Student", f"Added new student '{name}' to class '{cls}'"
            )
        else:
            messagebox.showerror(
                "Database Error", f"Failed to save student: {message}", parent=self
            )


class CollectFeePopup(ctk.CTkToplevel):
    def __init__(self, parent, theme, db_manager, refresh_callback):
        super().__init__(parent)
        self.title("Collect Student Fee")
        self.geometry("400x450")
        self.lift()
        self.attributes("-topmost", True)
        self.after(10, self.focus_force)
        self.db = db_manager
        self.refresh_callback = refresh_callback
        self.theme = theme

        label = ctk.CTkLabel(self, text="Collect Payment", font=theme.fonts["h2"])
        label.pack(pady=20)

        self.invoice_entry = ctk.CTkEntry(
            self,
            placeholder_text="Enter Invoice ID (e.g. INV-101)",
            width=300,
            height=40,
        )
        self.invoice_entry.pack(pady=10)

        self.amount_entry = ctk.CTkEntry(
            self, placeholder_text="Enter Amount Paid", width=300, height=40
        )
        self.amount_entry.pack(pady=10)

        submit_btn = ctk.CTkButton(
            self,
            text="Confirm Payment",
            fg_color=theme.colors["accent"],
            command=self.submit_payment,
            width=200,
            height=45,
        )
        submit_btn.pack(pady=30)

    def submit_payment(self):
        inv_id = self.invoice_entry.get()
        amount = self.amount_entry.get()

        if inv_id and amount:
            success = self.db.collect_student_fee(inv_id, amount)
            if success:
                print(f"Payment received for {inv_id}")
                self.db.log_event("Fee", f"Paid PKR {amount} for Invoice {inv_id}")
                self.refresh_callback()
                self.destroy()
            else:
                print("Invoice not found.")


class ScheduleExamPopup(ctk.CTkToplevel):
    def __init__(self, parent, theme, db_manager, refresh_callback):
        super().__init__(parent)
        self.title("Schedule New Examination")
        self.geometry("500x650")
        self.attributes("-topmost", True)
        self.db = db_manager
        self.theme = theme
        self.refresh_callback = refresh_callback

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(
            self.main_container, text="Exam Details", font=theme.fonts["h2"]
        ).pack(pady=(0, 20))

        self.name_entry = self.create_input("Exam Name", "e.g. Final Semester 2026")

        classes = self.db.get_all_class_names()
        self.class_dropdown = self.create_dropdown("Select Class", classes)

        self.date_entry = self.create_input("Date", "YYYY-MM-DD")
        self.room_entry = self.create_input("Room Number", "e.g. Room 101")

        save_btn = ctk.CTkButton(
            self.main_container,
            text="Schedule Exam",
            command=self.save_exam,
            fg_color=theme.colors["accent"],
            height=45,
        )
        save_btn.pack(fill="x", pady=30)

    def create_input(self, label, placeholder):
        ctk.CTkLabel(
            self.main_container, text=label, font=self.theme.fonts["body_strong"]
        ).pack(anchor="w")
        entry = ctk.CTkEntry(
            self.main_container, placeholder_text=placeholder, height=40
        )
        entry.pack(fill="x", pady=(5, 15))
        return entry

    def create_dropdown(self, label, values):
        ctk.CTkLabel(
            self.main_container, text=label, font=self.theme.fonts["body_strong"]
        ).pack(anchor="w")
        combo = ctk.CTkComboBox(self.main_container, values=values, height=40)
        combo.pack(fill="x", pady=(5, 15))
        return combo

    def save_exam(self):
        """Extracts data from UI, saves to DB, and refreshes the main view."""
        exam_name = self.name_entry.get().strip()
        selected_class = self.class_dropdown.get()
        exam_date = self.date_entry.get().strip()
        room_number = self.room_entry.get().strip()

        if not all([exam_name, exam_date, room_number]):
            print("Error: All fields are required!")
            return

        exam_data = {
            "exam_name": exam_name,
            "class_name": selected_class,
            "exam_date": exam_date,
            "room_no": room_number,
        }

        success = self.db.add_new_exam(exam_data)

        if success:
            print(f"Success: {exam_name} scheduled.")
            if self.refresh_callback:
                self.refresh_callback()

            self.destroy()
        else:
            print("Database Error: Could not save exam.")


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, theme, asset_manager, on_menu_click):
        super().__init__(
            parent, width=260, corner_radius=0, fg_color=theme.colors["bg_sidebar"]
        )
        self.theme = theme
        self.assets = asset_manager
        self.on_menu_click = on_menu_click
        self.menu_buttons = {}
        self.current_active = None
        self.buttons = {}

        self.grid_propagate(False)

        right_border = ctk.CTkFrame(
            self, width=2, fg_color=theme.colors["border"], corner_radius=0
        )
        right_border.pack(side="right", fill="y")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=16, pady=24)

        self._setup_logo()
        self._setup_menu()

    def set_active_tab(self, view_name):
        """Standardizes the visual state when navigation happens externally"""
        if view_name in self.menu_buttons:
            self._update_visual_state(view_name)

    def _update_visual_state(self, name):
        """Internal helper to handle the 'Active' look (Icons, Colors, Fonts)"""
        if self.current_active and self.current_active in self.menu_buttons:
            old_data = self.menu_buttons[self.current_active]
            old_btn = old_data["widget"]
            old_path = old_data["icon_path"]

            old_btn.configure(
                fg_color="transparent",
                text_color=self.theme.colors["text_secondary"],
                font=self.theme.fonts["body_strong"],
                image=self.assets.recolor_icon(
                    old_path, self.theme.colors["text_secondary"]
                ),
            )

        if name in self.menu_buttons:
            new_data = self.menu_buttons[name]
            new_btn = new_data["widget"]
            new_path = new_data["icon_path"]

            new_btn.configure(
                fg_color=self.theme.colors["bg_hover"],
                text_color=self.theme.colors["accent"],
                font=self.theme.fonts["body_strong_large"],
                image=self.assets.recolor_icon(new_path, self.theme.colors["accent"]),
            )
            self.current_active = name

    def _setup_logo(self):
        try:
            image_path = resource_path("assets/icons/uom_logo.png")
            original_uom_logo = Image.open(image_path)
            orig_width, orig_height = original_uom_logo.size
            desired_width = 40
            aspect_ratio = orig_height / orig_width
            calculated_height = int(desired_width * aspect_ratio)

            uom_logo = ctk.CTkImage(
                light_image=original_uom_logo,
                dark_image=original_uom_logo,
                size=(desired_width, calculated_height),
            )
            logo_label = ctk.CTkLabel(
                self.content,
                text=" UOM",
                image=uom_logo,
                compound="left",
                font=self.theme.fonts["h1"],
                text_color=self.theme.colors["text_primary"],
            )
            logo_label.pack(pady=(0, 32), anchor="w")
        except Exception as e:
            print(f"Logo error: {e}")

    def _setup_menu(self):
        items = [
            ("Dashboard", "dashboard.png"),
            ("Students", "students.png"),
            ("Classes", "classes.png"),
            ("Fee Records", "fee_records.png"),
            ("Examination", "examination.png"),
            ("Attendance", "attendance.png"),
            ("Settings", "settings.png"),
        ]

        for name, icon_name in items:
            path = resource_path(f"assets/icons/{icon_name}")
            btn = ctk.CTkButton(
                self.content,
                text=f"  {name}",
                image=self.assets.recolor_icon(
                    path, self.theme.colors["text_secondary"]
                ),
                compound="left",
                anchor="w",
                height=50,
                corner_radius=8,
                fg_color="transparent",
                text_color=self.theme.colors["text_secondary"],
                hover_color=self.theme.colors["bg_hover"],
                font=self.theme.fonts["body_strong"],
                command=lambda n=name: self.handle_click(n),
            )
            btn.pack(fill="x", pady=2)
            self.menu_buttons[name] = {"widget": btn, "icon_path": path}

    def handle_click(self, name):
        """Triggered by manual button clicks"""
        self._update_visual_state(name)

        self.on_menu_click(name)


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller, stats_data=None, activity_data=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = controller.theme
        self.assets = controller.assets
        self.controller = controller

        self.stats = stats_data or [
            {
                "title": "Active Students",
                "value": "0",
                "icon": "students.png",
                "trend": "0%",
                "is_up": True,
            },
            {
                "title": "Total Faculty",
                "value": "0",
                "icon": "settings.png",
                "trend": "0%",
                "is_up": True,
            },
            {
                "title": "Attendance",
                "value": "0%",
                "icon": "attendance.png",
                "trend": "0%",
                "is_up": False,
            },
            {
                "title": "Revenue",
                "value": "$0",
                "icon": "fee_records.png",
                "trend": "0%",
                "is_up": True,
            },
        ]

        self.activities = activity_data or []

        ComponentFactory.create_header_bar(
            self,
            self.theme,
            "Dashboard",
            "Welcome back! Here's a summary of your college.",
        )

        self.render_stats_grid()

        self.render_lower_sections()

    def render_stats_grid(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=32, pady=(40, 24))
        container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for i, data in enumerate(self.stats):
            card = ComponentFactory.create_stat_card(
                container, self.theme, self.assets, data
            )
            card.grid(row=0, column=i, sticky="nsew", padx=10)

    def render_lower_sections(self):
        lower_container = ctk.CTkFrame(self, fg_color="transparent")
        lower_container.pack(fill="both", expand=True, padx=32, pady=(20, 32))
        lower_container.grid_columnconfigure(0, weight=3)
        lower_container.grid_columnconfigure(1, weight=2)

        activity_group = ctk.CTkFrame(lower_container, fg_color="transparent")
        activity_group.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        ctk.CTkLabel(
            activity_group,
            text="Recent Activity",
            font=self.theme.fonts["h3"],
            text_color=self.theme.colors["text_primary"],
        ).pack(anchor="w", pady=(0, 15))

        activity_card = ctk.CTkFrame(
            activity_group,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color=self.theme.colors["border"],
        )
        activity_card.pack(fill="both", expand=True)

        if not self.activities:
            ctk.CTkLabel(
                activity_card,
                text="No recent activity to display.",
                font=self.theme.fonts["body_small"],
                text_color="#94a3b8",
            ).pack(pady=50)
        else:
            for i, item in enumerate(self.activities):
                ComponentFactory.create_activity_item(
                    activity_card, self.theme, self.assets, item
                )
                if i < len(self.activities) - 1:
                    ComponentFactory.create_separator(
                        activity_card, self.theme, px_height=2
                    )

        actions_group = ctk.CTkFrame(lower_container, fg_color="transparent")
        actions_group.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            actions_group,
            text="Quick Actions",
            font=self.theme.fonts["h3"],
            text_color=self.theme.colors["text_primary"],
        ).pack(anchor="w", pady=(0, 15))

        quick_actions = [
            ("New Student", "Register for 2026", "students.png", "#F0F9FF", "Students"),
            (
                "Fee Payment",
                "Generate Invoice",
                "fee_records.png",
                "#F0FDF4",
                "Fee Records",
            ),
            (
                "Exam Portal",
                "Update Marks",
                "examination.png",
                "#FFFBEB",
                "Examination",
            ),
        ]

        for title, sub, icon, bg, target in quick_actions:
            ComponentFactory.create_action_card(
                actions_group,
                self.theme,
                self.assets,
                title,
                sub,
                icon,
                bg,
                command=lambda t=target: self.controller.handle_view_change(t),
            )


class StudentsView(ctk.CTkFrame):
    def __init__(self, parent, controller, data_list=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = controller.theme
        self.assets = controller.assets
        self.controller = controller
        self.db = controller.db

        self.all_students = data_list or []
        self.current_filter = "Active"

        ComponentFactory.create_header_bar(
            self,
            self.theme,
            "Student Manager",
            "Register new students and manage existing records.",
        )
        self.setup_nav_bar()

        self.main_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color=self.theme.colors["border"],
        )
        self.main_card.pack(fill="both", expand=True, padx=32, pady=(0, 32))
        self.main_card.bind("<Button-1>", lambda e: self.main_card.focus())

        self.render_view()

    def open_student_actions(self, student_data):
        """Triggered when the arrow is clicked"""
        action_popup = ctk.CTkToplevel(self)
        action_popup.title(f"Manage: {student_data.get('name')}")
        action_popup.geometry("400x500")
        action_popup.attributes("-topmost", True)

        ctk.CTkLabel(
            action_popup, text="Student Actions", font=("Inter", 18, "bold")
        ).pack(pady=20)

        info_text = f"Name: {student_data.get('name')}\nID: {student_data.get('roll_no')}\nCurrent Status: {student_data.get('status')}"
        ctk.CTkLabel(action_popup, text=info_text, justify="left").pack(pady=10)

        ctk.CTkLabel(
            action_popup, text="Update Status:", font=("Inter", 12, "bold")
        ).pack(pady=(20, 5))

        status_var = ctk.StringVar(value=student_data.get("status"))
        status_dropdown = ctk.CTkOptionMenu(
            action_popup,
            values=["Active", "Dropouts", "Graduated"],
            variable=status_var,
        )
        status_dropdown.pack(pady=10)

        def save_changes():
            new_status = status_var.get()

            student_id = student_data.get("enrollment_id") or student_data.get("id")

            success = self.controller.db.update_student_status(student_id, new_status)

            if success:
                student_data["status"] = new_status

                self.render_view()
                action_popup.destroy()
            else:
                print("Failed to update status in Database. Check column names.")

        ctk.CTkButton(
            action_popup, text="Save Changes", fg_color="#10B981", command=save_changes
        ).pack(pady=20)

    def open_student_profile_editor(self, student_data):
        """Opens a dialog to EDIT student details specifically for the Profile Tab"""
        edit_window = ctk.CTkToplevel(self)
        edit_window.title(f"Edit Profile: {student_data.get('name')}")
        edit_window.geometry("450x550")
        edit_window.attributes("-topmost", True)

        ctk.CTkLabel(
            edit_window, text="Update Student Information", font=("Inter", 18, "bold")
        ).pack(pady=20)

        fields = [
            ("Name", "name"),
            ("Roll No", "roll_no"),
            ("Class", "class_name"),
            ("Shift", "shift"),
            ("Region", "region"),
        ]

        entries = {}
        for label_text, key in fields:
            frame = ctk.CTkFrame(edit_window, fg_color="transparent")
            frame.pack(fill="x", padx=40, pady=8)

            ctk.CTkLabel(frame, text=label_text, width=100, anchor="w").pack(
                side="left"
            )
            entry = ctk.CTkEntry(frame)
            entry.insert(0, str(student_data.get(key, "")))
            entry.pack(side="right", expand=True, fill="x")
            entries[key] = entry

        def save_changes():
            updated_data = {
                "name": entries["name"].get(),
                "roll_no": entries["roll_no"].get(),
                "class_name": entries["class_name"].get(),
                "shift": entries["shift"].get(),
                "region": entries["region"].get(),
                "id": student_data.get("id"),
            }

            success = self.controller.db.update_student_profile(updated_data)

            if success:
                edit_window.destroy()
                for s in self.all_students:
                    if s.get("id") == updated_data["id"]:
                        s.update(updated_data)
                        break
                self.render_view()
                self.db.log_event(
                    "Student", f"Profile updated for student ID {updated_data['id']}"
                )

        ctk.CTkButton(
            edit_window, text="Save Changes", fg_color="#10B981", command=save_changes
        ).pack(pady=30)

    def handle_filter_change(self, value):
        self.current_filter = value.strip()
        self.render_view()

    def render_view(self):
        """Clears and re-renders the content based on the current filter"""
        for widget in self.main_card.winfo_children():
            widget.destroy()

        if self.current_filter == "Profile":
            action = self.open_student_profile_editor
            self.show_student_table(self.all_students, action)

        else:
            action = self.open_student_actions
            filtered_data = [
                s
                for s in self.all_students
                if str(s.get("status")).strip().capitalize()
                == self.current_filter.strip().capitalize()
            ]
            self.show_student_table(filtered_data, action)

    def update_table_only(self, filtered_data, action_command=None):
        for widget in self.table_container.winfo_children():
            widget.destroy()

        ComponentFactory.create_data_table(
            self.table_container,
            self.theme,
            headers=["Student Name", "Father Name", "Class", "Status", "Actions"],
            rows=filtered_data,
            action_command=action_command,
        )

    def process_search(self, event=None):
        """Filters students in real-time as you type"""
        query = self.search_entry.get().lower().strip()

        if self.current_filter == "Profile":
            base_data = self.all_students
        else:
            base_data = [
                s
                for s in self.all_students
                if str(s.get("status")).strip().capitalize() == self.current_filter
            ]

        if query:
            filtered_results = [
                s
                for s in base_data
                if query in str(s.get("name")).lower()
                or query in str(s.get("id")).lower()
            ]
        else:
            filtered_results = base_data

        self.update_table_only(filtered_results)

    def handle_export(self):
        """Exports the currently filtered list to an Excel file"""
        if self.current_filter == "Profile":
            export_data = self.all_students
            filename_suggestion = "All_Students_Report.xlsx"
        else:
            export_data = [
                s
                for s in self.all_students
                if str(s.get("status")).strip().capitalize() == self.current_filter
            ]
            filename_suggestion = f"{self.current_filter}_Students_Report.xlsx"

        if not export_data:
            messagebox.showwarning("Export", "No data available to export in this tab.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=filename_suggestion,
        )

        if file_path:
            try:
                df = pd.DataFrame(export_data)
                df.to_excel(file_path, index=False)
                messagebox.showinfo(
                    "Success", f"Data exported successfully to {file_path}"
                )
                self.db.log_event("Export", f"Exported data to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")

    def create_view_toolbar(self, parent, data_count):
        """Standardized toolbar with dynamic badge count"""
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=20)

        badge_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        badge_frame.pack(side="left")

        ctk.CTkLabel(
            badge_frame,
            text=f"{self.current_filter} Students",
            font=self.theme.fonts["body_strong"],
        ).pack(side="left")

        count_bubble = ctk.CTkLabel(
            badge_frame,
            text=str(data_count),
            width=40,
            height=24,
            corner_radius=12,
            fg_color="#E0F2FE",
            text_color="#0369A1",
            font=self.theme.fonts["body_strong"],
        )
        count_bubble.pack(side="left", padx=10)

        self.search_entry = ComponentFactory.create_search_bar(
            toolbar, self.theme, "Search by name or ID..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=20)
        self.search_entry.bind("<KeyRelease>", self.process_search)

        if self.current_filter == "Profile":
            add_btn = ctk.CTkButton(
                toolbar,
                text="+ Add Student",
                command=lambda: ProfileDetailModal(self, self.controller),
                width=140,
                height=40,
                corner_radius=10,
                fg_color=self.theme.colors["accent"],
                text_color="#FFFFFF",
                font=self.theme.fonts["body_strong"],
                cursor="hand2",
            )
            add_btn.pack(side="right")

    def show_student_table(self, data, action_command):
        for widget in self.main_card.winfo_children():
            widget.destroy()
        self.create_view_toolbar(self.main_card, len(data))
        self.table_container = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True)
        self.update_table_only(data, action_command)

    def open_detailed_profile(self, student_data):
        """This opens a popup modal with all student details"""
        ProfileDetailModal(self, self.controller, student_data)

    def setup_nav_bar(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=32, pady=(20, 20))

        self.status_var = ctk.StringVar(value="Active")
        status_filter = ctk.CTkSegmentedButton(
            container,
            values=["Active", "Dropouts", "Graduated", "Profile"],
            command=self.handle_filter_change,
            variable=self.status_var,
            height=45,
            width=450,
            corner_radius=20,
            fg_color="#FFFFFF",
            unselected_color="#FFFFFF",
            unselected_hover_color="#F1F5F9",
            selected_hover_color=self.theme.colors["bg_hover"],
            selected_color=self.theme.colors["bg_hover"],
            text_color=self.theme.colors["text_primary"],
            font=self.theme.fonts["body_strong"],
        )
        status_filter.pack(side="left")
        export_btn = ctk.CTkButton(
            container,
            text="Export Data",
            width=120,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=self.theme.colors["border"],
            fg_color="#FFFFFF",
            text_color=self.theme.colors["text_primary"],
            hover_color="#F8FAFC",
            font=self.theme.fonts["body_strong"],
            command=self.handle_export,
        )
        export_btn.pack(side="right")


class ClassesView(ctk.CTkFrame):
    def __init__(self, parent, controller, data_dict=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = controller.theme
        self.assets = controller.assets
        self.controller = controller
        self.db = controller.db

        self.classes_data = data_dict or []

        ComponentFactory.create_header_bar(
            self,
            self.theme,
            "Class Management",
            "Organize class schedules, room assignments, and student capacity.",
        )

        self.main_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color=self.theme.colors["border"],
        )
        self.main_card.pack(fill="both", expand=True, padx=32, pady=(30, 32))
        self.main_card.bind("<Button-1>", lambda e: self.main_card.focus())

        self.render_classes_content()

    def render_view(self):
        """Clears and re-renders the Classes content"""

        for widget in self.main_card.winfo_children():
            widget.destroy()

        self.search_entry = None
        self.table_container = None
        self.count_bubble = None

        self.render_classes_content()

    def open_add_class_dialog(self):
        """Opens a top-level window to add a new class"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Class")
        dialog.geometry("400x600")
        dialog.minsize(400, 600)
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Class Details", font=("Inter", 18, "bold")).pack(
            pady=20
        )

        fields = [
            ("Class Name (e.g., BS-CS)", "name"),
            ("Total Capacity (Seats)", "capacity"),
            ("Room Number", "room"),
            ("Shift (Morning/Evening)", "shift"),
        ]

        entries = {}
        for label_text, key in fields:
            frame = ctk.CTkFrame(dialog, fg_color="transparent")
            frame.pack(fill="x", padx=30, pady=5)

            ctk.CTkLabel(frame, text=label_text, anchor="w").pack(fill="x")
            entry = ctk.CTkEntry(frame)
            entry.pack(fill="x", pady=(0, 5))
            entries[key] = entry

        def save_new_class():
            new_class_data = {
                key: entry.get().strip() for key, entry in entries.items()
            }

            import uuid

            generated_id = f"CLS-{uuid.uuid4().hex[:4].upper()}"
            new_class_data["id"] = generated_id

            raw_capacity = entries["capacity"].get().strip()
            new_class_data["capacity"] = raw_capacity

            success = self.controller.db.add_class(new_class_data)

            if success:
                dialog.destroy()

                self.classes_data = self.controller.db.get_all_classes()
                self.render_view()
                messagebox.showinfo(
                    "Success", f"Class Created!\nCapacity: {new_class_data['capacity']}"
                )
                self.db.log_event(
                    "Class", f"Created new class with ID {new_class_data['id']}"
                )

        save_btn = ctk.CTkButton(
            dialog,
            text="Create Class",
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            width=200,
            corner_radius=8,
            command=save_new_class,
        )

        save_btn.pack(pady=(40, 20))

    def refresh_class_data(view_instance):
        """Re-syncs the UI with the actual Database content"""
        view_instance.all_classes = view_instance.controller.db.get_all_classes()

        view_instance.render_view()

    def view_class_students(self, class_data):
        """Swaps the class list for a student list within the same view."""
        students = self.controller.db.get_students_by_class(class_data["name"])

        self.count_bubble.configure(text=str(len(students)))
        self.search_entry.delete(0, "end")
        self.search_entry.configure(
            placeholder_text=f"Search students in {class_data['name']}..."
        )

        for widget in self.table_container.winfo_children():
            widget.destroy()

        back_btn = ctk.CTkButton(
            self.table_container,
            text="← Back to All Classes",
            width=150,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            text_color=self.theme.colors["accent"],
            hover_color="#F1F5F9",
            command=self.render_classes_content,
        )
        back_btn.pack(anchor="w", padx=20, pady=(10, 0))

        headers = ["Student Name", "Father Name", "Class", "Status"]
        ComponentFactory.create_data_table(
            self.table_container, self.theme, headers=headers, rows=students
        )

    def render_classes_content(self):
        if (
            not hasattr(self, "search_entry")
            or self.search_entry is None
            or not self.search_entry.winfo_exists()
        ):
            for widget in self.main_card.winfo_children():
                widget.destroy()

            toolbar = ctk.CTkFrame(self.main_card, fg_color="transparent")
            toolbar.pack(fill="x", padx=20, pady=20)

            badge_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
            badge_frame.pack(side="left")
            ctk.CTkLabel(
                badge_frame, text="Total Classes", font=self.theme.fonts["body_strong"]
            ).pack(side="left")

            self.count_bubble = ctk.CTkLabel(
                badge_frame,
                text=str(len(self.classes_data)),
                width=45,
                height=24,
                corner_radius=12,
                fg_color="#E0F2FE",
                text_color="#0369A1",
                font=self.theme.fonts["body_small"],
            )
            self.count_bubble.pack(side="left", padx=10)

            self.search_entry = ComponentFactory.create_search_bar(
                toolbar, self.theme, "Search classes..."
            )
            self.search_entry.pack(side="left", fill="x", expand=True, padx=20)
            self.search_entry.bind("<KeyRelease>", self.filter_classes)

            ctk.CTkButton(
                toolbar,
                text="+ Create Class",
                width=140,
                height=40,
                corner_radius=10,
                fg_color=self.theme.colors["accent"],
                text_color="#FFFFFF",
                font=self.theme.fonts["body_strong"],
                command=self.open_add_class_dialog,
            ).pack(side="right")

            self.table_container = ctk.CTkFrame(self.main_card, fg_color="transparent")
            self.table_container.pack(fill="both", expand=True)

        for widget in self.table_container.winfo_children():
            widget.destroy()

        self.count_bubble.configure(text=str(len(self.classes_data)))

        headers = ["Class Name", "Capacity", "Room/Hall", "Shift", "Actions"]

        ComponentFactory.create_data_table(
            self.table_container,
            self.theme,
            headers=headers,
            rows=self.classes_data,
            action_command=self.handle_class_action,
        )

    def confirm_delete(self, class_data, dialog_to_close):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {class_data['name']}?\nThis cannot be undone.",
        )
        if confirm:
            success = self.controller.db.delete_class(class_data["id"])
            if success:
                dialog_to_close.destroy()
                self.classes_data = self.controller.db.get_all_classes()
                self.render_classes_content()
                messagebox.showinfo("Deleted", "Class removed successfully.")
                self.db.log_event("Class", f"Deleted class with ID {class_data['id']}")

    def handle_class_action(self, class_data):
        action_dialog = ctk.CTkToplevel(self)
        action_dialog.title(f"Manage {class_data['name']}")
        action_dialog.geometry("300x400")
        action_dialog.grab_set()

        ctk.CTkLabel(
            action_dialog,
            text=f"Class: {class_data['id']}",
            font=self.theme.fonts["body_strong"],
        ).pack(pady=20)

        ctk.CTkButton(
            action_dialog,
            text="View Enrolled Students",
            fg_color=self.theme.colors["accent"],
            command=lambda: [
                action_dialog.destroy(),
                self.view_class_students(class_data),
            ],
        ).pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(
            action_dialog,
            text="Edit Class Details",
            fg_color="#F59E0B",
            command=lambda: self.open_edit_dialog(class_data, action_dialog),
        ).pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(
            action_dialog,
            text="Remove Class",
            fg_color="#EF4444",
            command=lambda: self.confirm_delete(class_data, action_dialog),
        ).pack(pady=10, padx=20, fill="x")

    def filter_classes(self, event=None):
        query = self.search_entry.get().lower()
        full_list = self.controller.db.get_all_classes()

        if not query:
            self.classes_data = full_list
        else:
            self.classes_data = [
                c
                for c in full_list
                if query in str(c.get("name", "")).lower()
                or query in str(c.get("id", "")).lower()
            ]

        self.render_classes_content()

    def open_edit_dialog(self, class_data, action_dialog):
        action_dialog.destroy()
        edit_dialog = ctk.CTkToplevel(self)
        edit_dialog.title(f"Edit Class {class_data['id']}")
        edit_dialog.geometry("400x550")
        print(f"Editing class: {class_data}")


class FeeRecordsView(ctk.CTkFrame):
    def __init__(self, parent, controller, data_dict=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = controller.theme
        self.assets = controller.assets
        self.controller = controller
        self.db = controller.db

        self.data_dict = data_dict

        ComponentFactory.create_header_bar(
            self,
            self.theme,
            "Fee Management",
            "Track student payments, pending balances, and financial history.",
        )

        ComponentFactory.create_separator(
            self, self.theme, horizontal_margin=32, vertical_margin=(0, 20)
        )

        self.main_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color=self.theme.colors["border"],
        )
        self.main_card.pack(fill="both", expand=True, padx=32, pady=(0, 32))

        self.render_fee_content()

    def refresh_data(self):
        """
        The Bridge: Fetches fresh data from the DB and
        tells the UI to redraw itself.
        """
        new_data = self.controller.db.get_fee_records()
        self.data_dict = new_data
        self.render_fee_content()

    def render_fee_content(self):
        if hasattr(self, "main_card"):
            for widget in self.main_card.winfo_children():
                widget.destroy()
        else:
            self.main_card = ctk.CTkFrame(
                self, fg_color=self.theme.colors["bg_card"], corner_radius=15
            )
            self.main_card.pack(fill="both", expand=True, padx=30, pady=30)

        if self.data_dict and len(self.data_dict) > 0:
            fee_data = self.data_dict
            pending_count = len(
                [item for item in fee_data if item.get("status") == "Pending"]
            )
            badge_color = "#FEE2E2" if pending_count > 0 else "#DCFCE7"
            badge_text_color = "#991B1B" if pending_count > 0 else "#166534"
        else:
            fee_data = [
                {
                    "id": "---",
                    "name": "No transactions found",
                    "course": "---",
                    "status": "---",
                }
            ]
            pending_count = 0
            badge_color = "#F1F5F9"
            badge_text_color = "#475569"

        toolbar = ctk.CTkFrame(self.main_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(20, 7))

        badge_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        badge_frame.pack(side="left")
        ctk.CTkLabel(
            badge_frame, text="Pending Dues", font=self.theme.fonts["body_strong"]
        ).pack(side="left")

        count_bubble = ctk.CTkLabel(
            badge_frame,
            text=str(pending_count),
            width=40,
            height=24,
            corner_radius=12,
            fg_color=badge_color,
            text_color=badge_text_color,
            font=self.theme.fonts["body_small"],
        )
        count_bubble.pack(side="left", padx=10)

        self.search_entry = ComponentFactory.create_search_bar(
            toolbar, self.theme, "Search by student name or Invoice ID..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=20)

        collect_btn = ctk.CTkButton(
            toolbar,
            text="+ Collect Fee",
            width=140,
            height=40,
            corner_radius=10,
            fg_color=self.theme.colors["accent"],
            text_color="#FFFFFF",
            font=self.theme.fonts["body_strong"],
            command=lambda: [
                print("Button Clicked!"),
                CollectFeePopup(
                    self, self.theme, self.controller.db, self.refresh_data
                ),
            ],
        )
        collect_btn.pack(side="right")

        headers = ["Invoice ID", "Student Name", "Month", "Status"]

        self.fee_table = ComponentFactory.create_data_table(
            self.main_card, self.theme, headers=headers, rows=fee_data
        )


class ExaminationView(ctk.CTkFrame):
    def __init__(self, parent, controller, data_dict=None):
        super().__init__(parent, fg_color="transparent")

        self.controller = controller
        self.theme = controller.theme
        self.assets = controller.assets
        self.data = data_dict
        self.db = controller.db
        ComponentFactory.create_header_bar(
            self,
            self.theme,
            "Examination Portal",
            "Academic Session: 2025-2026 | Term: Final Exams",
        )
        ComponentFactory.create_separator(
            self, self.theme, horizontal_margin=32, vertical_margin=(0, 20)
        )

        self.main_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color=self.theme.colors["border"],
        )
        self.main_card.pack(fill="both", expand=True, padx=32, pady=(0, 32))
        self.render_examination_view()

    def refresh_data(self):
        self.data = self.controller.db.get_examination_data()
        self.render_examination_view()

    def render_examination_view(self, input_data=None):
        """The Master Render Method - The only place that draws UI"""
        for widget in self.main_card.winfo_children():
            widget.destroy()
        display_data = (
            input_data if input_data is not None else (self.data if self.data else [])
        )
        self.render_exam_toolbar_logic(display_data)

        headers = ["Exam Name", "Class", "Date", "Room Number", "Actions"]
        self.exam_table = ComponentFactory.create_data_table(
            self.main_card,
            self.theme,
            headers=headers,
            rows=display_data,
            action_command=self.handle_delete_exam,
            command_text="Delete",
        )

    def handle_delete_exam(self, exam_data):
        exam_name = exam_data.get("exam_name", "this exam")
        confirm = messagebox.askyesno(
            title="Confirm Deletion",
            message=f"Are you sure you want to delete '{exam_name}'?\nThis cannot be undone.",
        )

        if confirm:
            success = self.controller.db.delete_exam(exam_data["id"])

            if success:
                self.refresh_data()

    def open_schedule_exam(self):
        """
        Instantiates the ScheduleExamPopup.
        We pass 'self.refresh_data' so the popup can tell this view to
        update once the exam is saved.
        """
        ScheduleExamPopup(
            parent=self,
            theme=self.theme,
            db_manager=self.controller.db,
            refresh_callback=self.refresh_data,
        )

    def render_exam_toolbar_logic(self, exam_data):
        if len(exam_data) > 0:
            badge_count = str(len(exam_data))
            badge_color = "#DCFCE7"
            text_color = "#166534"
        else:
            badge_count = "0"
            badge_color = "#FEE2E2"
            text_color = "#991B1B"

        toolbar = ctk.CTkFrame(self.main_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(20, 7))

        badge_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        badge_frame.pack(side="left")
        ctk.CTkLabel(
            badge_frame, text="Scheduled Exams", font=self.theme.fonts["body_strong"]
        ).pack(side="left")

        ctk.CTkLabel(
            badge_frame,
            text=badge_count,
            width=40,
            height=24,
            corner_radius=12,
            fg_color=badge_color,
            text_color=text_color,
            font=self.theme.fonts["body_small"],
        ).pack(side="left", padx=10)

        self.search_entry = ComponentFactory.create_search_bar(
            toolbar, self.theme, "Search subjects or dates..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=20)

        ctk.CTkButton(
            toolbar,
            text="+ Schedule Exam",
            width=140,
            height=40,
            corner_radius=10,
            fg_color=self.theme.colors["accent"],
            text_color="#FFFFFF",
            font=self.theme.fonts["body_strong"],
            command=self.open_schedule_exam,
        ).pack(side="right")


class AttendanceView(ctk.CTkFrame):
    def __init__(self, parent, controller, data_dict=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = controller.theme
        self.data_dict = data_dict
        self.controller = controller
        self.db = controller.db
        self.available_classes = [c["name"] for c in self.db.get_all_classes()]

        ComponentFactory.create_header_bar(
            self,
            self.theme,
            "Attendance Registry",
            "Daily student roll call and attendance tracking.",
        )

        ComponentFactory.create_separator(
            self, self.theme, horizontal_margin=32, vertical_margin=(0, 20)
        )

        self.main_container = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color=self.theme.colors["border"],
        )
        self.main_container.pack(fill="both", expand=True, padx=32, pady=(0, 32))

        self.render_attendance_content()

    def save_attendance(self):
        if not hasattr(self, "current_students_list") or not self.current_students_list:
            return

        selected_class = self.class_dropdown.get()
        current_date = datetime.now().strftime("%Y-%m-%d")
        attendance_records = []

        for student in self.current_students_list:
            s_id = student.get("enrollment_id")

            if not s_id:
                print(f"Debug: Student dict keys are {list(student.keys())}")
                continue

            attendance_records.append(
                {
                    "student_id": s_id,
                    "date": current_date,
                    "status": "Present",
                    "class_name": selected_class,
                }
            )

        success = self.db.save_attendance_batch(attendance_records)
        if success:
            self.show_message(
                "Success",
                f"Attendance for {selected_class} has been saved successfully.",
            )
        else:
            self.show_message(
                "Database Error", "Failed to save attendance. Check logs.", "#e74c3c"
            )

    def load_class_attendance(self, selected_class):
        """Refreshes ONLY the table area"""

        for widget in self.data_area.winfo_children():
            widget.destroy()
        if selected_class == "Select Class":
            self.show_empty_state()
            return
        students = self.db.get_students_by_class(selected_class)
        self.current_students_list = students

        self.status_vars = {}

        if not students:
            self.show_empty_state()
            return

        attendance_rows = []
        for s in students:
            attendance_rows.append(
                {
                    "id": s.get("enrollment_id", "N/A"),
                    "name": s.get("name", "Unknown"),
                    "avg": "---",
                    "status": "Present",
                }
            )
        headers = ["ID", "Student Name", "Monthly Avg", "Status", "Actions"]
        self.attendance_table = ComponentFactory.create_data_table(
            self.data_area,
            self.theme,
            headers=headers,
            rows=attendance_rows,
            is_attendance=True,
            action_command=self.show_student_details,
        )

    def show_message(self, title, message, color="#2ecc71"):
        """Creates a professional popup notification"""
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("300x150")
        popup.attributes("-topmost", True)

        popup.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            popup, text=message, font=self.theme.fonts["body_strong"], wraplength=250
        ).grid(row=0, column=0, pady=20)

        ctk.CTkButton(
            popup, text="OK", width=100, fg_color=color, command=popup.destroy
        ).grid(row=1, column=0, pady=10)

    def show_student_details(self, student_data):
        """Triggered when the action arrow is clicked"""

        s_id = student_data.get("id") or student_data.get("enrollment_id")
        s_name = student_data.get("name", "Student")

        if not s_id:
            self.show_message("Error", "Could not identify student ID.", "#e74c3c")
            return

        history = self.db.get_student_attendance_history(s_id)

        if not history:
            msg = f"No attendance records found for {s_name}."
        else:
            lines = [f"{record['date']}: {record['status']}" for record in history[:5]]
            history_str = "\n".join(lines)
            msg = f"Recent History for {s_name}:\n\n{history_str}"

        self.show_message("Attendance Stats", msg, self.theme.colors["accent"])

    def show_empty_state(self):
        """Displays placeholder inside the data_area"""
        self.empty_container = ctk.CTkFrame(self.data_area, fg_color="transparent")
        self.empty_container.pack(expand=True, fill="both", pady=100)
        ctk.CTkLabel(self.empty_container, text="📂", font=("Inter", 50)).pack()

        ctk.CTkLabel(
            self.empty_container,
            text="No students found in this class",
            font=self.theme.fonts["h3"],
            text_color=self.theme.colors["text_primary"],
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            self.empty_container,
            text="Please select a different class from the dropdown\nor add new students to this registry.",
            font=self.theme.fonts["body_small"],
            text_color=self.theme.colors["text_secondary"],
        ).pack()

    def render_attendance_content(self):
        self.toolbar = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=20, pady=20)

        self.class_dropdown = ctk.CTkOptionMenu(
            self.toolbar,
            values=(
                ["Select Class"] + self.available_classes
                if self.available_classes
                else ["No Classes Found"]
            ),
            width=200,
            height=38,
            corner_radius=8,
            command=self.load_class_attendance,
        )
        self.class_dropdown.set("Select Class")
        self.class_dropdown.pack(side="left")

        save_btn = ctk.CTkButton(
            self.toolbar,
            text="Save Attendance",
            command=self.save_attendance,
            width=140,
            height=40,
            corner_radius=10,
            fg_color=self.theme.colors["accent"],
            text_color="#FFFFFF",
            font=self.theme.fonts["body_strong"],
        )
        save_btn.pack(side="right", padx=10)

        self.data_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.data_area.pack(fill="both", expand=True)

        self.show_empty_state()


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.theme = controller.theme
        self.db = controller.db
        self.controller = controller
        self.entries = {}

        ComponentFactory.create_header_bar(
            self,
            self.theme,
            "System Configuration",
            "Manage global institution parameters and academic standards.",
        )
        ComponentFactory.create_separator(
            self, self.theme, horizontal_margin=32, vertical_margin=(0, 20)
        )

        self.main_container = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color=self.theme.colors["border"],
        )
        self.main_container.pack(fill="both", expand=True, padx=32, pady=(0, 32))

        self.render_settings_content()
        self.load_settings_from_db()

    def render_settings_content(self):
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_container, fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=(20, 80))

        self.add_section_header(
            "Organization Identity",
            "Basic information regarding your academic institution.",
        )

        self.create_setting_row(
            "inst_name", "Legal Institution Name", "The official name used in reports."
        )
        self.create_setting_row(
            "admin_email",
            "Administrative Email",
            "Primary contact for system notifications.",
        )

        self.create_setting_row(
            "academic_session",
            "Active Academic Session",
            "The current operational year (e.g., 2025-2026).",
        )
        self.create_setting_row(
            "attendance_threshold",
            "Attendance Threshold (%)",
            "Minimum percentage required for exam eligibility.",
        )

        footer = ctk.CTkFrame(
            self.main_container, fg_color="#F8FAFC", height=70, corner_radius=0
        )
        footer.place(relx=0, rely=1, relwidth=1, anchor="sw")

        save_btn = ctk.CTkButton(
            footer,
            text="Apply Changes",
            width=180,
            height=40,
            corner_radius=8,
            fg_color=self.theme.colors["accent"],
            font=("Inter", 13, "bold"),
            command=self.save_settings,
        )
        save_btn.pack(side="right", padx=30, pady=15)

    def create_setting_row(self, key, label, help_text):
        row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row.pack(fill="x", pady=12)

        label_side = ctk.CTkFrame(row, fg_color="transparent")
        label_side.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            label_side, text=label, font=("Inter", 14, "bold"), text_color="#1E293B"
        ).pack(anchor="w")
        ctk.CTkLabel(
            label_side, text=help_text, font=("Inter", 11), text_color="#94A3B8"
        ).pack(anchor="w")
        entry = ctk.CTkEntry(
            row,
            width=320,
            height=38,
            corner_radius=6,
            fg_color="#FFFFFF",
            border_color="#E2E8F0",
            font=("Inter", 13),
        )
        entry.pack(side="right", padx=(20, 0))
        self.entries[key] = entry

    def add_section_header(self, title, description):
        header_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_container.pack(fill="x", pady=(25, 15))
        ctk.CTkLabel(
            header_container,
            text=title.upper(),
            font=("Inter", 12, "bold"),
            text_color=self.theme.colors["accent"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_container, text=description, font=("Inter", 12), text_color="#64748B"
        ).pack(anchor="w")
        ctk.CTkFrame(self.scroll_frame, height=1, fg_color="#F1F5F9").pack(
            fill="x", pady=(0, 15)
        )

    def load_settings_from_db(self):
        """Fetches settings from the database and populates the entries"""
        settings_data = self.db.get_all_settings()
        for key, value in settings_data.items():
            if key in self.entries:
                self.entries[key].insert(0, value)

    def save_settings(self):
        settings_to_save = {key: entry.get() for key, entry in self.entries.items()}
        if self.db.update_settings(settings_to_save):
            self.show_message("Success", "System configuration updated successfully.")
        else:
            self.show_message("Error", "Failed to save settings.", "#e74c3c")

    def show_message(self, title, message, color="#2ecc71"):
        """Creates a professional popup notification"""
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("300x150")
        popup.attributes("-topmost", True)
        popup.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            popup, text=message, font=self.theme.fonts["body_strong"], wraplength=250
        ).grid(row=0, column=0, pady=20)
        ctk.CTkButton(
            popup, text="OK", width=100, fg_color=color, command=popup.destroy
        ).grid(row=1, column=0, pady=10)
