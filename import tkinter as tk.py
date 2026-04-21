import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
import os


def setup_data():
    if not os.path.exists("eco_data.csv"):
        df = pd.DataFrame(columns=["User", "Activity", "Points"])
        df.to_csv("eco_data.csv", index=False)

eco_points = {
    "Planting Tree": 50,
    "Cycling": 10,
    "Recycling": 20,
    "Saving Power": 15
}

def log_activity(activity_name):
    user = user_entry.get().strip()
    if not user:
        messagebox.showwarning("Input Required", "Please enter your name to log progress.")
        return

    points = eco_points[activity_name]
    new_data = pd.DataFrame([[user, activity_name, points]], columns=["User", "Activity", "Points"])
    new_data.to_csv("eco_data.csv", mode='a', header=False, index=False)
    
    messagebox.showinfo("Success", f"Logged {activity_name} for {user}!\n+{points} points added.")
    update_total_display()

def update_total_display():
    try:
        df = pd.read_csv("eco_data.csv")
        user = user_entry.get().strip()
        if not user:
            points_label.config(text="0", fg="#95a5a6")
            rating_label.config(text="Enter name to see rank", fg="#95a5a6")
            return

        user_rows = df[df["User"] == user]
        total = user_rows["Points"].sum()
        
        if total > 100:
            rating, color = "Excellent 🥇", "#27ae60"
        elif total > 50:
            rating, color = "Good 👍", "#2ecc71"
        else:
            rating, color = "Beginner 🌱", "#f39c12"
            
        points_label.config(text=str(total), fg=color)
        rating_label.config(text=rating, fg=color)
    except:
        points_label.config(text="0", fg="#95a5a6")

def show_graph():
    try:
        df = pd.read_csv("eco_data.csv")
        user = [user_entry.get()]
        user_data = df[df["User"] == user]
        
        if user_data.empty:
            messagebox.showinfo("No Data", f"No activities found for '{user}'.")
            return

        summary = user_data.groupby("Activity")["Points"].sum()
        
        plt.figure(figsize=(8, 5))
        summary.plot(kind='bar', color='#2ecc71', edgecolor='#27ae60')
        plt.title(f"Impact Dashboard: {user}", fontsize=14, fontweight='bold')
        plt.ylabel("Lifetime Points")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    except:
        messagebox.showerror("Error", "Could not load chart.")


def show_leaderboard():
    try:
        df = pd.read_csv("eco_data.csv")

        if df.empty:
            messagebox.showinfo("No Data", "No user data available yet.")
            return

        leaderboard = df.groupby("User")["Points"].sum().reset_index()
        leaderboard = leaderboard.sort_values(by="Points", ascending=False)
        leaderboard["Rank"] = leaderboard["Points"].rank(method="dense", ascending=False).astype(int)

        lb_window = tk.Toplevel(root)
        lb_window.title("🏆 Leaderboard")
        lb_window.geometry("400x400")
        lb_window.configure(bg="#f4f7f6")

        tk.Label(lb_window, text="🏆 Leaderboard", font=("Helvetica", 16, "bold"),
                 bg="#f4f7f6", fg="#2c3e50").pack(pady=10)

        tree = ttk.Treeview(lb_window, columns=("Rank", "User", "Points"), show="headings")
        tree.heading("Rank", text="Rank")
        tree.heading("User", text="User")
        tree.heading("Points", text="Points")

        tree.column("Rank", width=60, anchor="center")
        tree.column("User", width=150, anchor="center")
        tree.column("Points", width=100, anchor="center")

        tree.pack(pady=10, fill="both", expand=True)

        for _, row in leaderboard.iterrows():
            tree.insert("", "end", values=(row["Rank"], row["User"], row["Points"]))

    except:
        messagebox.showerror("Error", "Could not load leaderboard.")


setup_data()
root = tk.Tk()
root.title("EcoTracker Pro")
root.geometry("450x650")
root.configure(bg="#f4f7f6")

header_font = ("Helvetica", 18, "bold")
label_font = ("Helvetica", 10)
btn_font = ("Helvetica", 10, "bold")


header_frame = tk.Frame(root, bg="#2ecc71", height=80)
header_frame.pack(fill="x")
tk.Label(header_frame, text="🌿 ECO TRACKER", font=header_font, bg="#2ecc71", fg="white").pack(pady=20)


input_frame = tk.Frame(root, bg="#f4f7f6", pady=20)
input_frame.pack()

tk.Label(input_frame, text="User Profile", font=label_font, bg="#f4f7f6", fg="#7f8c8d").pack()
user_entry = tk.Entry(input_frame, font=("Helvetica", 14), width=20, bd=0, highlightthickness=1)
user_entry.config(highlightbackground="#bdc3c7", highlightcolor="#2ecc71")
user_entry.pack(pady=5)


score_frame = tk.Frame(root, bg="white", padx=20, pady=15)
score_frame.pack(pady=10, fill="x", padx=40)

tk.Label(score_frame, text="CURRENT SCORE", font=("Helvetica", 9, "bold"), bg="white", fg="#95a5a6").pack()
points_label = tk.Label(score_frame, text="0", font=("Helvetica", 32, "bold"), bg="white", fg="#2ecc71")
points_label.pack()
rating_label = tk.Label(score_frame, text="Enter name to start", font=("Helvetica", 10, "italic"), bg="white", fg="#bdc3c7")
rating_label.pack()


tk.Label(root, text="LOG NEW ACTIVITY", font=("Helvetica", 10, "bold"), bg="#f4f7f6", fg="#7f8c8d").pack(pady=(20, 5))

activity_container = tk.Frame(root, bg="#f4f7f6")
activity_container.pack(pady=5)

for i, (activity, pt) in enumerate(eco_points.items()):
    row = i // 2
    col = i % 2
    btn = tk.Button(activity_container, text=f"{activity}\n(+{pt} pts)", 
                    font=btn_font, width=15, height=3,
                    bg="#ffffff", fg="#2c3e50",
                    activebackground="#2ecc71", activeforeground="white",
                    relief="flat",
                    command=lambda a=activity: log_activity(a))
    btn.grid(row=row, column=col, padx=10, pady=10)


footer_frame = tk.Frame(root, bg="#f4f7f6", pady=20)
footer_frame.pack(fill="x", side="bottom")

tk.Button(footer_frame, text="🔄 REFRESH SCORE", width=20,
          command=update_total_display, bg="#3498db", fg="white").pack(pady=5)

tk.Button(footer_frame, text="📊 VIEW IMPACT CHART", width=20,
          command=show_graph, bg="#2c3e50", fg="white").pack(pady=5)

tk.Button(footer_frame, text="🏆 VIEW LEADERBOARD", width=20,
          command=show_leaderboard, bg="#e67e22", fg="white").pack(pady=5)

root.mainloop()