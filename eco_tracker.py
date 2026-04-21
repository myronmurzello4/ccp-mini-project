import tkinter as tk
from tkinter import ttk, messagebox, font
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import hashlib
import datetime
import random

# ─────────────────────────────────────────────
#  CONFIG & CONSTANTS
# ─────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

USERS_CSV    = os.path.join(DATA_DIR, "users.csv")
ACTIVITY_CSV = os.path.join(DATA_DIR, "activities.csv")

ACTIVITY_POINTS = {
    "Planting Trees 🌳": 50,
    "Cycling 🚴":        10,
    "Walking 🚶":         5,
    "Recycling ♻️":      20,
    "Saving Electricity 💡": 15,
}

ACTIVITY_ICONS = {
    "Planting Trees 🌳": "🌳",
    "Cycling 🚴":        "🚴",
    "Walking 🚶":         "🚶",
    "Recycling ♻️":      "♻️",
    "Saving Electricity 💡": "💡",
}

# Colour palette – deep forest / bioluminescent accent
C = {
    "bg":       "#0D1F0F",   # near-black forest green
    "panel":    "#132A15",   # card background
    "border":   "#1E4020",   # subtle border
    "accent":   "#4ADE80",   # vivid green (primary CTA)
    "accent2":  "#22C55E",   # secondary green
    "lime":     "#A3E635",   # lime highlight
    "text":     "#E8F5E9",   # off-white
    "muted":    "#6B9E74",   # muted green text
    "red":      "#F87171",   # error / warning
    "gold":     "#FBBF24",   # gold for leaderboard
    "silver":   "#94A3B8",
    "bronze":   "#CD7F32",
    "chart_bg": "#0A1A0C",
}

# ─────────────────────────────────────────────
#  DATA HELPERS
# ─────────────────────────────────────────────
def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> pd.DataFrame:
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV)
    return pd.DataFrame(columns=["username", "email", "password_hash", "joined"])


def save_users(df: pd.DataFrame):
    df.to_csv(USERS_CSV, index=False)


def load_activities() -> pd.DataFrame:
    if os.path.exists(ACTIVITY_CSV):
        df = pd.read_csv(ACTIVITY_CSV, parse_dates=["date"])
        return df
    return pd.DataFrame(columns=["username", "activity", "points", "date", "bonus"])


def save_activities(df: pd.DataFrame):
    df.to_csv(ACTIVITY_CSV, index=False)


def user_total_points(username: str, df_act: pd.DataFrame) -> int:
    sub = df_act[df_act["username"] == username]
    return int(sub["points"].sum()) if not sub.empty else 0


def performance_rating(points: int) -> tuple:
    if points >= 500:
        return "Excellent 🥇", C["gold"]
    elif points >= 250:
        return "Good 👍", C["accent"]
    elif points >= 100:
        return "Average 🙂", C["lime"]
    else:
        return "Poor ⚠️", C["red"]


def consistency_bonus(username: str, activity: str, df_act: pd.DataFrame) -> int:
    """Award +10 bonus if user logged same activity 3+ days in last 7 days."""
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    sub = df_act[
        (df_act["username"] == username) &
        (df_act["activity"] == activity) &
        (df_act["date"].dt.date >= week_ago)
    ]
    return 10 if len(sub) >= 3 else 0


# ─────────────────────────────────────────────
#  TREE CANVAS ANIMATION
# ─────────────────────────────────────────────
def draw_tree(canvas: tk.Canvas, cx: int, cy: int, height: int, level: int = 5):
    """Recursive fractal tree on a Tkinter Canvas."""
    canvas.delete("all")
    canvas.configure(bg=C["bg"])
    _branch(canvas, cx, cy, -90, height, level)


def _branch(canvas, x, y, angle, length, depth):
    import math
    if depth == 0 or length < 4:
        return
    rad = math.radians(angle)
    x2 = x + length * math.cos(rad)
    y2 = y + length * math.sin(rad)
    green = max(0, min(255, 40 + depth * 30))
    color = f"#00{green:02X}20" if depth > 2 else f"#{20+depth*10:02X}{green:02X}{20+depth*5:02X}"
    width = max(1, depth)
    canvas.create_line(x, y, x2, y2, fill=color, width=width, capstyle=tk.ROUND)
    _branch(canvas, x2, y2, angle - 25, length * 0.72, depth - 1)
    _branch(canvas, x2, y2, angle + 25, length * 0.72, depth - 1)


# ─────────────────────────────────────────────
#  STYLED WIDGET HELPERS
# ─────────────────────────────────────────────
def styled_button(parent, text, command, width=20, bg=None, fg=None):
    bg = bg or C["accent"]
    fg = fg or C["bg"]
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=C["accent2"],
        activeforeground=C["bg"],
        font=("Courier New", 11, "bold"),
        relief="flat", bd=0, padx=14, pady=8,
        cursor="hand2", width=width,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=C["accent2"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def card_frame(parent, **kwargs):
    return tk.Frame(parent, bg=C["panel"],
                    highlightbackground=C["border"],
                    highlightthickness=1, **kwargs)


def label(parent, text, size=11, bold=False, color=None, **kwargs):
    color = color or C["text"]
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                    font=("Courier New", size, weight), **kwargs)


def entry_widget(parent, show=""):
    e = tk.Entry(
        parent, bg=C["border"], fg=C["text"],
        insertbackground=C["accent"],
        font=("Courier New", 11),
        relief="flat", bd=0,
        highlightbackground=C["accent"],
        highlightthickness=1,
        show=show,
    )
    return e


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class EcoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌿 Eco Activity Tracker")
        self.geometry("1000x680")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.minsize(900, 620)

        self.current_user: str = None
        self.df_users    = load_users()
        self.df_act      = load_activities()

        self._show_auth_screen()

    # ── SCREEN MANAGEMENT ──────────────────────
    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ═══════════════════════════════════════════
    #  AUTH SCREEN
    # ═══════════════════════════════════════════
    def _show_auth_screen(self):
        self._clear()
        self.geometry("820x560")

        root_frame = tk.Frame(self, bg=C["bg"])
        root_frame.pack(fill="both", expand=True)

        # Left decorative panel
        left = tk.Frame(root_frame, bg=C["panel"], width=320)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🌿", bg=C["panel"], font=("", 60)).pack(pady=(60, 10))
        label(left, "ECO TRACKER", size=18, bold=True, color=C["accent"]).pack()
        label(left, "Track. Earn. Thrive.", size=10, color=C["muted"]).pack(pady=4)

        # Animated tree canvas
        tree_canvas = tk.Canvas(left, width=260, height=200, bg=C["bg"], highlightthickness=0)
        tree_canvas.pack(pady=20)
        self.after(300, lambda: draw_tree(tree_canvas, 130, 195, 70, 6))

        label(left, "Every action matters.", size=9, color=C["muted"]).pack(side="bottom", pady=20)

        # Right auth panel
        right = tk.Frame(root_frame, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        # Tabs
        self._auth_tab = tk.StringVar(value="login")
        tab_row = tk.Frame(right, bg=C["bg"])
        tab_row.pack(fill="x", pady=(0, 24))

        def set_tab(t):
            self._auth_tab.set(t)
            _render_form()

        self._login_tab_btn = tk.Button(
            tab_row, text="LOG IN", command=lambda: set_tab("login"),
            font=("Courier New", 11, "bold"), relief="flat", bd=0,
            padx=18, pady=6, cursor="hand2",
        )
        self._login_tab_btn.pack(side="left")
        self._signup_tab_btn = tk.Button(
            tab_row, text="SIGN UP", command=lambda: set_tab("signup"),
            font=("Courier New", 11, "bold"), relief="flat", bd=0,
            padx=18, pady=6, cursor="hand2",
        )
        self._signup_tab_btn.pack(side="left", padx=8)

        self._form_frame = tk.Frame(right, bg=C["bg"])
        self._form_frame.pack(fill="both", expand=True)
        self._msg_var = tk.StringVar()

        def _render_form():
            for w in self._form_frame.winfo_children():
                w.destroy()
            self._msg_var.set("")

            active = self._auth_tab.get()
            self._login_tab_btn.config(
                bg=C["accent"] if active == "login" else C["panel"],
                fg=C["bg"] if active == "login" else C["muted"],
            )
            self._signup_tab_btn.config(
                bg=C["accent"] if active == "signup" else C["panel"],
                fg=C["bg"] if active == "signup" else C["muted"],
            )

            ff = self._form_frame
            if active == "login":
                label(ff, "Welcome back 🌱", size=15, bold=True).pack(anchor="w", pady=(0, 20))
                label(ff, "Email").pack(anchor="w")
                email_e = entry_widget(ff)
                email_e.pack(fill="x", ipady=7, pady=(2, 12))
                label(ff, "Password").pack(anchor="w")
                pw_e = entry_widget(ff, show="●")
                pw_e.pack(fill="x", ipady=7, pady=(2, 20))
                styled_button(ff, "LOG IN →", lambda: self._login(email_e.get(), pw_e.get()), width=30).pack()
            else:
                label(ff, "Join the movement 🌍", size=15, bold=True).pack(anchor="w", pady=(0, 16))
                label(ff, "Username").pack(anchor="w")
                un_e = entry_widget(ff);  un_e.pack(fill="x", ipady=6, pady=(2, 10))
                label(ff, "Email").pack(anchor="w")
                em_e = entry_widget(ff);  em_e.pack(fill="x", ipady=6, pady=(2, 10))
                label(ff, "Password").pack(anchor="w")
                pw_e = entry_widget(ff, show="●"); pw_e.pack(fill="x", ipady=6, pady=(2, 18))
                styled_button(ff, "CREATE ACCOUNT →",
                              lambda: self._register(un_e.get(), em_e.get(), pw_e.get()), width=30).pack()

            tk.Label(ff, textvariable=self._msg_var, bg=C["bg"], fg=C["red"],
                     font=("Courier New", 10), wraplength=320).pack(pady=(12, 0))

        _render_form()

    def _login(self, email, password):
        if not email or not password:
            self._msg_var.set("Please fill all fields.")
            return
        row = self.df_users[
            (self.df_users["email"] == email) &
            (self.df_users["password_hash"] == hash_pw(password))
        ]
        if row.empty:
            self._msg_var.set("Invalid email or password.")
            return
        self.current_user = row.iloc[0]["username"]
        self._show_dashboard()

    def _register(self, username, email, password):
        if not username or not email or not password:
            self._msg_var.set("All fields are required.")
            return
        if "@" not in email:
            self._msg_var.set("Enter a valid email address.")
            return
        if len(password) < 6:
            self._msg_var.set("Password must be ≥ 6 characters.")
            return
        if not self.df_users[self.df_users["email"] == email].empty:
            self._msg_var.set("Email already registered.")
            return
        new_row = {
            "username": username.strip(),
            "email": email.strip(),
            "password_hash": hash_pw(password),
            "joined": str(datetime.date.today()),
        }
        self.df_users = pd.concat([self.df_users, pd.DataFrame([new_row])], ignore_index=True)
        save_users(self.df_users)
        self._msg_var.set("✅ Account created! Please log in.")
        self._auth_tab.set("login")

    # ═══════════════════════════════════════════
    #  DASHBOARD
    # ═══════════════════════════════════════════
    def _show_dashboard(self):
        self._clear()
        self.geometry("1080x720")

        # Sidebar
        sidebar = tk.Frame(self, bg=C["panel"], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        label(sidebar, "🌿 ECO", size=16, bold=True, color=C["accent"]).pack(pady=(24, 4))
        label(sidebar, "TRACKER", size=10, color=C["muted"]).pack()
        ttk.Separator(sidebar).pack(fill="x", pady=18)

        nav_items = [
            ("🏠  Dashboard",    self._page_home),
            ("📋  Log Activity", self._page_log),
            ("📊  Analytics",    self._page_analytics),
            ("🏆  Leaderboard",  self._page_leaderboard),
            ("⭐  Top Performer",self._page_top_performer),
        ]
        self._nav_btns = []
        for txt, cmd in nav_items:
            b = tk.Button(
                sidebar, text=txt, command=cmd,
                bg=C["panel"], fg=C["text"],
                activebackground=C["border"],
                activeforeground=C["accent"],
                font=("Courier New", 10), relief="flat",
                bd=0, padx=16, pady=10, anchor="w",
                cursor="hand2", width=18,
            )
            b.pack(fill="x")
            self._nav_btns.append(b)

        tk.Frame(sidebar, bg=C["panel"]).pack(fill="both", expand=True)
        styled_button(sidebar, "⏻  Log Out", self._logout, width=16, bg=C["border"], fg=C["muted"]).pack(pady=20)

        # Main content area
        self._main = tk.Frame(self, bg=C["bg"])
        self._main.pack(side="right", fill="both", expand=True)

        self._page_home()

    def _clear_main(self):
        for w in self._main.winfo_children():
            w.destroy()

    def _highlight_nav(self, idx):
        for i, b in enumerate(self._nav_btns):
            b.config(bg=C["accent"] if i == idx else C["panel"],
                     fg=C["bg"] if i == idx else C["text"])

    def _logout(self):
        self.current_user = None
        self.geometry("820x560")
        self._show_auth_screen()

    # ── PAGE: HOME ─────────────────────────────
    def _page_home(self):
        self._clear_main()
        self._highlight_nav(0)
        m = self._main

        # Header
        hdr = tk.Frame(m, bg=C["bg"])
        hdr.pack(fill="x", padx=30, pady=(28, 0))
        label(hdr, f"Welcome back, {self.current_user}! 🌱", size=18, bold=True, color=C["accent"]).pack(anchor="w")
        label(hdr, str(datetime.date.today().strftime("%A, %d %B %Y")), size=10, color=C["muted"]).pack(anchor="w")

        ttk.Separator(m).pack(fill="x", padx=30, pady=18)

        # Stat cards
        row1 = tk.Frame(m, bg=C["bg"])
        row1.pack(fill="x", padx=30)

        total_pts  = user_total_points(self.current_user, self.df_act)
        rating, rc = performance_rating(total_pts)
        user_acts  = self.df_act[self.df_act["username"] == self.current_user]
        n_acts     = len(user_acts)
        streak     = self._calc_streak()

        cards_data = [
            ("⭐ Total Points", str(total_pts), C["accent"]),
            ("🎯 Rating",       rating,         rc),
            ("📅 Activities",   str(n_acts),    C["lime"]),
            ("🔥 Day Streak",   str(streak),    C["gold"]),
        ]
        for title, val, col in cards_data:
            c = card_frame(row1, padx=20, pady=18)
            c.pack(side="left", fill="both", expand=True, padx=6)
            label(c, title, size=9, color=C["muted"]).pack(anchor="w")
            label(c, val,   size=18, bold=True, color=col).pack(anchor="w", pady=(6, 0))

        # Recent activities
        tk.Frame(m, bg=C["bg"]).pack(pady=14)
        label(m, "  Recent Activities", size=12, bold=True, color=C["text"]).pack(anchor="w", padx=30)

        recent = user_acts.tail(8).iloc[::-1] if not user_acts.empty else pd.DataFrame()
        cf = card_frame(m, padx=0, pady=0)
        cf.pack(fill="both", expand=True, padx=30, pady=10)

        cols = ["Date", "Activity", "Points", "Bonus"]
        col_w = [120, 280, 80, 80]
        hrow = tk.Frame(cf, bg=C["border"])
        hrow.pack(fill="x")
        for col_name, w in zip(cols, col_w):
            label(hrow, col_name, size=9, bold=True, color=C["muted"]).pack(side="left", padx=10, pady=8, width=w//7)

        if recent.empty:
            label(cf, "No activities logged yet. Start your journey! 🚀", size=10, color=C["muted"]).pack(pady=30)
        else:
            for _, row in recent.iterrows():
                rrow = tk.Frame(cf, bg=C["panel"])
                rrow.pack(fill="x")
                tk.Frame(cf, bg=C["border"], height=1).pack(fill="x")
                label(rrow, str(row["date"])[:10], size=9, color=C["muted"]).pack(side="left", padx=10, pady=7, width=17)
                label(rrow, str(row["activity"]), size=9, color=C["text"]).pack(side="left", padx=10, width=40)
                label(rrow, f"+{int(row['points'])}", size=9, bold=True, color=C["accent"]).pack(side="left", padx=10, width=11)
                label(rrow, f"+{int(row['bonus'])}" if row["bonus"] else "-", size=9, color=C["lime"]).pack(side="left", padx=10)

    def _calc_streak(self) -> int:
        user_acts = self.df_act[self.df_act["username"] == self.current_user]
        if user_acts.empty:
            return 0
        dates = sorted(set(user_acts["date"].dt.date.tolist()), reverse=True)
        streak = 0
        today = datetime.date.today()
        for i, d in enumerate(dates):
            if d == today - datetime.timedelta(days=i):
                streak += 1
            else:
                break
        return streak

    # ── PAGE: LOG ACTIVITY ─────────────────────
    def _page_log(self):
        self._clear_main()
        self._highlight_nav(1)
        m = self._main

        label(m, "  Log Eco Activity", size=16, bold=True, color=C["accent"]).pack(anchor="w", padx=30, pady=(28, 4))
        label(m, "  Every action earns points and helps the planet.", size=10, color=C["muted"]).pack(anchor="w", padx=30)
        ttk.Separator(m).pack(fill="x", padx=30, pady=18)

        content = tk.Frame(m, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=30)

        # Activity grid
        label(content, "Choose an activity:", size=11, bold=True).pack(anchor="w", pady=(0, 14))
        grid = tk.Frame(content, bg=C["bg"])
        grid.pack(fill="x")

        self._sel_activity = tk.StringVar()
        self._act_buttons  = {}

        acts = list(ACTIVITY_POINTS.keys())
        for i, act in enumerate(acts):
            pts = ACTIVITY_POINTS[act]
            col = i % 3
            row_i = i // 3

            c = card_frame(grid, padx=20, pady=16, cursor="hand2")
            c.grid(row=row_i, column=col, padx=8, pady=8, sticky="ew")
            grid.columnconfigure(col, weight=1)

            label(c, ACTIVITY_ICONS[act], size=22).pack()
            label(c, act.split(" ")[0] + " " + act.split(" ")[1], size=10, bold=True).pack(pady=(4, 2))
            label(c, f"+{pts} pts", size=11, color=C["accent"], bold=True).pack()

            def _select(a=act, card=c):
                self._sel_activity.set(a)
                for aa, cc in self._act_buttons.items():
                    cc.config(highlightbackground=C["border"])
                card.config(highlightbackground=C["accent"])

            c.bind("<Button-1>", lambda e, a=act, card=c: _select(a, card))
            for child in c.winfo_children():
                child.bind("<Button-1>", lambda e, a=act, card=c: _select(a, card))
            self._act_buttons[act] = c

        # Date
        df = tk.Frame(content, bg=C["bg"])
        df.pack(fill="x", pady=(20, 0))
        label(df, "Date:", size=11, bold=True).pack(side="left")
        self._date_var = tk.StringVar(value=str(datetime.date.today()))
        date_e = tk.Entry(df, textvariable=self._date_var, bg=C["border"], fg=C["text"],
                          font=("Courier New", 11), relief="flat",
                          insertbackground=C["accent"],
                          highlightbackground=C["accent"], highlightthickness=1)
        date_e.pack(side="left", padx=12, ipady=6, ipadx=10)

        # Log button
        bf = tk.Frame(content, bg=C["bg"])
        bf.pack(fill="x", pady=18)
        styled_button(bf, "✅  LOG THIS ACTIVITY", self._log_activity, width=28).pack(side="left")

        # Result label
        self._log_msg = tk.StringVar()
        tk.Label(content, textvariable=self._log_msg, bg=C["bg"], fg=C["accent"],
                 font=("Courier New", 11, "bold"), wraplength=500).pack(anchor="w", pady=8)

    def _log_activity(self):
        act = self._sel_activity.get()
        if not act:
            self._log_msg.set("⚠️  Please select an activity first.")
            return
        try:
            date = datetime.datetime.strptime(self._date_var.get(), "%Y-%m-%d")
        except ValueError:
            self._log_msg.set("⚠️  Invalid date format. Use YYYY-MM-DD.")
            return

        pts    = ACTIVITY_POINTS[act]
        bonus  = consistency_bonus(self.current_user, act, self.df_act)
        total  = pts + bonus

        new_row = {
            "username": self.current_user,
            "activity": act,
            "points":   total,
            "date":     date,
            "bonus":    bonus,
        }
        self.df_act = pd.concat([self.df_act, pd.DataFrame([new_row])], ignore_index=True)
        save_activities(self.df_act)

        msg = f"🎉  Logged '{act}' — earned {pts} pts"
        if bonus:
            msg += f" + {bonus} consistency bonus!"
        self._log_msg.set(msg)
        # Reset selection
        self._sel_activity.set("")
        for cc in self._act_buttons.values():
            cc.config(highlightbackground=C["border"])

    # ── PAGE: ANALYTICS ────────────────────────
    def _page_analytics(self):
        self._clear_main()
        self._highlight_nav(2)
        m = self._main

        label(m, "  Analytics & Progress", size=16, bold=True, color=C["accent"]).pack(anchor="w", padx=30, pady=(28, 4))
        ttk.Separator(m).pack(fill="x", padx=30, pady=14)

        user_acts = self.df_act[self.df_act["username"] == self.current_user].copy()

        tab_frame = tk.Frame(m, bg=C["bg"])
        tab_frame.pack(fill="x", padx=30, pady=(0, 12))

        chart_container = tk.Frame(m, bg=C["bg"])
        chart_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        def show_weekly():
            for w in chart_container.winfo_children():
                w.destroy()
            _weekly_chart(user_acts, chart_container)
            wk_btn.config(bg=C["accent"], fg=C["bg"])
            mo_btn.config(bg=C["panel"], fg=C["text"])

        def show_monthly():
            for w in chart_container.winfo_children():
                w.destroy()
            _monthly_chart(user_acts, chart_container)
            mo_btn.config(bg=C["accent"], fg=C["bg"])
            wk_btn.config(bg=C["panel"], fg=C["text"])

        wk_btn = styled_button(tab_frame, "Weekly Chart",  show_weekly,  width=16)
        wk_btn.pack(side="left")
        mo_btn = styled_button(tab_frame, "Monthly Graph", show_monthly, width=16, bg=C["panel"], fg=C["text"])
        mo_btn.pack(side="left", padx=10)

        show_weekly()

    def _page_leaderboard(self):
        self._clear_main()
        self._highlight_nav(3)
        m = self._main

        label(m, "  🏆 Leaderboard", size=16, bold=True, color=C["gold"]).pack(anchor="w", padx=30, pady=(28, 4))
        label(m, "  Ranked by total eco-points earned.", size=10, color=C["muted"]).pack(anchor="w", padx=30)
        ttk.Separator(m).pack(fill="x", padx=30, pady=18)

        if self.df_act.empty or self.df_users.empty:
            label(m, "No data yet. Be the first to log an activity!", size=12, color=C["muted"]).pack(pady=40)
            return

        # Build leaderboard
        scores = (
            self.df_act.groupby("username")["points"]
            .sum()
            .reset_index()
            .rename(columns={"points": "total"})
            .sort_values("total", ascending=False)
            .reset_index(drop=True)
        )

        cf = card_frame(m, padx=0, pady=0)
        cf.pack(fill="both", expand=True, padx=30, pady=0)

        hrow = tk.Frame(cf, bg=C["border"])
        hrow.pack(fill="x")
        for txt, w in [("Rank", 60), ("Username", 260), ("Total Points", 140), ("Rating", 200)]:
            label(hrow, txt, size=9, bold=True, color=C["muted"]).pack(side="left", padx=14, pady=10, width=w//7)

        medal = {0: ("🥇", C["gold"]), 1: ("🥈", C["silver"]), 2: ("🥉", C["bronze"])}

        for i, row in scores.iterrows():
            ic, tc = medal.get(i, (str(i + 1), C["muted"]))
            rat, rc = performance_rating(int(row["total"]))
            bg = C["accent"] if row["username"] == self.current_user else C["panel"]

            rrow = tk.Frame(cf, bg=bg)
            rrow.pack(fill="x")
            tk.Frame(cf, bg=C["border"], height=1).pack(fill="x")

            label(rrow, ic, size=12, bold=True, color=tc).pack(side="left", padx=14, pady=10, width=8)
            label(rrow, row["username"], size=10, bold=(row["username"] == self.current_user),
                  color=C["accent"] if row["username"] == self.current_user else C["text"]).pack(side="left", padx=14, width=37)
            label(rrow, str(int(row["total"])), size=12, bold=True, color=C["accent"]).pack(side="left", padx=14, width=20)
            label(rrow, rat, size=9, color=rc).pack(side="left", padx=14)

    def _page_top_performer(self):
        self._clear_main()
        self._highlight_nav(4)
        m = self._main

        label(m, "  ⭐ Annual Top Performer", size=16, bold=True, color=C["gold"]).pack(anchor="w", padx=30, pady=(28, 4))
        ttk.Separator(m).pack(fill="x", padx=30, pady=18)

        year = datetime.date.today().year
        year_acts = self.df_act[self.df_act["date"].dt.year == year]

        if year_acts.empty:
            label(m, f"No activities recorded for {year} yet.", size=12, color=C["muted"]).pack(pady=40)
            return

        scores = year_acts.groupby("username")["points"].sum().reset_index()
        top = scores.loc[scores["points"].idxmax()]

        # Trophy card
        cf = card_frame(m, padx=40, pady=40)
        cf.pack(padx=80, pady=20)

        tk.Label(cf, text="🏆", bg=C["panel"], font=("", 64)).pack()
        label(cf, f"Top Performer {year}", size=12, color=C["muted"], bold=True).pack(pady=(10, 4))
        label(cf, top["username"], size=28, bold=True, color=C["gold"]).pack()
        label(cf, f"{int(top['points'])} eco-points earned this year", size=12, color=C["accent"]).pack(pady=8)

        rat, rc = performance_rating(int(top["points"]))
        label(cf, rat, size=14, bold=True, color=rc).pack(pady=4)

        # Activity breakdown for top user
        top_acts = year_acts[year_acts["username"] == top["username"]]
        breakdown = top_acts.groupby("activity")["points"].sum().reset_index().sort_values("points", ascending=False)

        label(cf, "─── Activity Breakdown ───", size=10, color=C["muted"]).pack(pady=(20, 8))
        for _, r in breakdown.iterrows():
            row_f = tk.Frame(cf, bg=C["panel"])
            row_f.pack(fill="x", pady=2)
            label(row_f, r["activity"], size=10, color=C["text"]).pack(side="left")
            label(row_f, f"+{int(r['points'])} pts", size=10, bold=True, color=C["accent"]).pack(side="right")


# ─────────────────────────────────────────────
#  CHART FUNCTIONS
# ─────────────────────────────────────────────
def _make_fig():
    fig = Figure(figsize=(8, 4.2), dpi=96, facecolor=C["chart_bg"])
    ax  = fig.add_subplot(111, facecolor=C["chart_bg"])
    for spine in ax.spines.values():
        spine.set_edgecolor(C["border"])
    ax.tick_params(colors=C["muted"], labelsize=8)
    ax.xaxis.label.set_color(C["muted"])
    ax.yaxis.label.set_color(C["muted"])
    ax.title.set_color(C["accent"])
    ax.grid(axis="y", color=C["border"], linestyle="--", alpha=0.5)
    return fig, ax


def _embed_chart(fig, parent):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def _weekly_chart(user_acts: pd.DataFrame, parent):
    fig, ax = _make_fig()
    if user_acts.empty:
        ax.text(0.5, 0.5, "No data yet!", ha="center", va="center",
                color=C["muted"], fontsize=14, transform=ax.transAxes)
        _embed_chart(fig, parent)
        return

    today   = datetime.date.today()
    week    = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    labels  = [d.strftime("%a\n%d") for d in week]
    acts    = list(ACTIVITY_POINTS.keys())
    colors  = ["#4ADE80", "#22C55E", "#86EFAC", "#A3E635", "#84CC16", "#16A34A", "#15803D"]

    data = {}
    for a in acts:
        sub = user_acts[user_acts["activity"] == a].copy()
        sub["day"] = sub["date"].dt.date
        daily = {d: int(sub[sub["day"] == d]["points"].sum()) for d in week}
        data[a] = [daily.get(d, 0) for d in week]

    bottoms = [0] * 7
    for i, (act, vals) in enumerate(data.items()):
        bars = ax.bar(labels, vals, bottom=bottoms,
                      color=colors[i % len(colors)], label=act.split(" ")[0], width=0.55, zorder=3)
        bottoms = [b + v for b, v in zip(bottoms, vals)]

    ax.set_title("Weekly Activity Points", fontsize=12, pad=10)
    ax.set_ylabel("Points")
    ax.legend(loc="upper left", facecolor=C["panel"], edgecolor=C["border"],
              labelcolor=C["text"], fontsize=7)
    fig.tight_layout(pad=2)
    _embed_chart(fig, parent)


def _monthly_chart(user_acts: pd.DataFrame, parent):
    fig, ax = _make_fig()
    if user_acts.empty:
        ax.text(0.5, 0.5, "No data yet!", ha="center", va="center",
                color=C["muted"], fontsize=14, transform=ax.transAxes)
        _embed_chart(fig, parent)
        return

    today    = datetime.date.today()
    months   = [(today.replace(day=1) - pd.DateOffset(months=i)).to_pydatetime().date()
                for i in range(5, -1, -1)]
    labels   = [m.strftime("%b %Y") for m in months]
    totals   = []
    for m in months:
        sub = user_acts[
            (user_acts["date"].dt.year  == m.year) &
            (user_acts["date"].dt.month == m.month)
        ]
        totals.append(int(sub["points"].sum()))

    ax.fill_between(labels, totals, color=C["accent"], alpha=0.15, zorder=2)
    ax.plot(labels, totals, color=C["accent"], linewidth=2.5,
            marker="o", markersize=7, markerfacecolor=C["lime"], zorder=3)

    for i, (lbl, val) in enumerate(zip(labels, totals)):
        if val > 0:
            ax.annotate(str(val), (lbl, val), textcoords="offset points",
                        xytext=(0, 10), ha="center", color=C["lime"], fontsize=9)

    ax.set_title("Monthly Points Progress (Last 6 Months)", fontsize=12, pad=10)
    ax.set_ylabel("Total Points")
    fig.tight_layout(pad=2)
    _embed_chart(fig, parent)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = EcoApp()
    app.mainloop()
