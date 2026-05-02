import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_db_connection
import re
from datetime import datetime
import csv

# ---------------- VALIDATION ----------------
def validate_inputs(roll, name, dob):
    if not roll.isdigit():
        messagebox.showerror("Error", "Roll must be numeric")
        return False

    if not re.match("^[A-Za-z ]+$", name):
        messagebox.showerror("Error", "Name must contain only letters")
        return False

    try:
        datetime.strptime(dob, "%Y-%m-%d")
    except:
        messagebox.showerror("Error", "DOB must be YYYY-MM-DD")
        return False

    return True


def clear_fields():
    entry_roll.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_dob.delete(0, tk.END)


# ---------------- CRUD ----------------
def add_student():
    roll = entry_roll.get()
    name = entry_name.get()
    dob = entry_dob.get()

    if not validate_inputs(roll, name, dob):
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO students (roll_number, name, dob) VALUES (%s, %s, %s)",
            (roll, name, dob)
        )
        conn.commit()
        messagebox.showinfo("Success", "Student added!")
        clear_fields()
        view_students()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cursor.close()
        conn.close()


def view_students():
    tree.delete(*tree.get_children())

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, roll_number, name, dob FROM students")

    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

    cursor.close()
    conn.close()


def delete_student():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a student")
        return

    confirm = messagebox.askyesno("Confirm", "Delete selected student?")
    if not confirm:
        return

    student_id = tree.item(selected)['values'][0]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
    conn.commit()

    cursor.close()
    conn.close()

    view_students()


def update_student():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a student to update")
        return

    student_id = tree.item(selected)['values'][0]

    roll = entry_roll.get()
    name = entry_name.get()
    dob = entry_dob.get()

    if not validate_inputs(roll, name, dob):
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE students SET roll_number=%s, name=%s, dob=%s WHERE student_id=%s",
        (roll, name, dob, student_id)
    )
    conn.commit()

    cursor.close()
    conn.close()

    messagebox.showinfo("Success", "Updated successfully")
    clear_fields()
    view_students()


def search_student():
    term = entry_search.get()

    tree.delete(*tree.get_children())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id, roll_number, name, dob
        FROM students
        WHERE roll_number LIKE %s OR name LIKE %s
    """, (f"%{term}%", f"%{term}%"))

    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

    cursor.close()
    conn.close()


def select_student(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected)['values']

        entry_roll.delete(0, tk.END)
        entry_roll.insert(0, values[1])

        entry_name.delete(0, tk.END)
        entry_name.insert(0, values[2])

        entry_dob.delete(0, tk.END)
        entry_dob.insert(0, values[3])


def export_csv():
    with open("students.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Roll", "Name", "DOB"])

        for row in tree.get_children():
            writer.writerow(tree.item(row)['values'])

    messagebox.showinfo("Export", "Data exported to students.csv")


# ---------------- UI ----------------
root = tk.Tk()
root.title("Student Management System")
root.geometry("950x620")
root.configure(bg="#e6cfd8")  # baby pink background


# ---------- BUTTON WITH HOT PINK BORDER ----------
def create_pink_button(parent, text, command):
    border = tk.Frame(parent, bg="#ff69b4", padx=1.5, pady=1.5)
    btn = tk.Button(border,
                    text=text,
                    command=command,
                    bg="#f2f2f2",
                    fg="black",
                    activebackground="#e6e6e6",
                    relief="flat",
                    bd=0,
                    padx=12,
                    pady=6,
                    font=("Segoe UI", 10, "bold"))
    btn.pack()
    return border


# ---------- FORM CARD ----------
frame_form = tk.Frame(root, bg="#d9d9d9", padx=20, pady=15)
frame_form.pack(pady=20)

tk.Label(frame_form, text="Roll Number:", bg="#d9d9d9").grid(row=0, column=0, pady=5)
entry_roll = tk.Entry(frame_form, bg="#f2f2f2")
entry_roll.grid(row=0, column=1)

tk.Label(frame_form, text="Name:", bg="#d9d9d9").grid(row=1, column=0, pady=5)
entry_name = tk.Entry(frame_form, bg="#f2f2f2")
entry_name.grid(row=1, column=1)

tk.Label(frame_form, text="DOB (YYYY-MM-DD):", bg="#d9d9d9").grid(row=2, column=0, pady=5)
entry_dob = tk.Entry(frame_form, bg="#f2f2f2")
entry_dob.grid(row=2, column=1)

# Add + Update buttons
btn_row = tk.Frame(frame_form, bg="#d9d9d9")
btn_row.grid(row=3, column=0, columnspan=2, pady=10)

create_pink_button(btn_row, "Add Student", add_student).pack(side=tk.LEFT, padx=10)
create_pink_button(btn_row, "Update Student", update_student).pack(side=tk.LEFT, padx=10)


# ---------- SEARCH ----------
frame_search = tk.Frame(root, bg="#e6cfd8")
frame_search.pack(pady=5)

tk.Label(frame_search, text="Search:", bg="#e6cfd8").pack(side=tk.LEFT)

entry_search = tk.Entry(frame_search, bg="#f2f2f2", width=25)
entry_search.pack(side=tk.LEFT, padx=5)

create_pink_button(frame_search, "Go", search_student).pack(side=tk.LEFT, padx=5)
create_pink_button(frame_search, "Refresh", view_students).pack(side=tk.LEFT)


# ---------- TABLE CARD ----------
frame_table = tk.Frame(root, bg="#d9d9d9", padx=10, pady=10)
frame_table.pack(pady=15)

columns = ("ID", "Roll Number", "Name", "DOB")
tree = ttk.Treeview(frame_table, columns=columns, show='headings', height=10)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack(side=tk.LEFT)

scrollbar = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tree.bind("<<TreeviewSelect>>", select_student)


# ---------- ACTION BUTTONS (INCLUDING EXPORT CSV) ----------
frame_action = tk.Frame(root, bg="#e6cfd8")
frame_action.pack(pady=15)

create_pink_button(frame_action, "Delete Student", delete_student)\
    .pack(side=tk.LEFT, padx=10)

create_pink_button(frame_action, "Export CSV", export_csv)\
    .pack(side=tk.LEFT, padx=10)


# ---------- LOAD ----------
view_students()
root.mainloop()