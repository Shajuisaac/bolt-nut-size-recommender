# Bolt and Nut Selector – Professional Tool (With Preview + Torque Extension + GD&T Diagram)

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# --------------------------- Constants ---------------------------- #
ASME_BOLT_SIZES = {
    "M6": {"nut_height": 5.2, "washer_thickness": 1.6, "min_engagement": 6,  "torque": 9},
    "M8": {"nut_height": 6.5, "washer_thickness": 1.6, "min_engagement": 8,  "torque": 22},
    "M10": {"nut_height": 8,   "washer_thickness": 2.0, "min_engagement": 10, "torque": 45},
    "M12": {"nut_height": 10,  "washer_thickness": 2.5, "min_engagement": 12, "torque": 77},
    "M16": {"nut_height": 13,  "washer_thickness": 3.0, "min_engagement": 16, "torque": 190}
}

TEMPERATURE_CLASSES = {
    "Normal (0°C to 60°C)": 1.0,
    "High (>60°C)": 1.2,
    "Low (<0°C to -50°C)": 1.1
}

# --------------------------- UI Setup ---------------------------- #
root = tk.Tk()
root.title("Bolt and Nut Selector – Professional Tool")
root.geometry("700x780")

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True)

hole_type = tk.StringVar()
depth = tk.DoubleVar()
temp_class = tk.StringVar()
plate_thickness = tk.DoubleVar()
washer_under_head = tk.BooleanVar()
washer_under_nut = tk.BooleanVar()
custom_washer_thickness = tk.DoubleVar(value=2.0)
safety_allowance = tk.DoubleVar(value=3.0)

# --------------------------- UI Widgets ---------------------------- #
tk.Label(frame, text="Hole Type:").grid(row=0, column=0, sticky='w')
ttks = ttk.Combobox(frame, textvariable=hole_type, values=["Through Hole", "Blind Hole"], state='readonly')
ttks.grid(row=0, column=1)
ttks.current(0)

# Depth / Thickness Inputs
tk.Label(frame, text="Hole Depth / Plate Thickness (mm):").grid(row=1, column=0, sticky='w')
tk.Entry(frame, textvariable=depth).grid(row=1, column=1)

tk.Label(frame, text="Plate Thickness (mm) – Through Hole only:").grid(row=2, column=0, sticky='w')
tk.Entry(frame, textvariable=plate_thickness).grid(row=2, column=1)

# Temperature
tk.Label(frame, text="Temperature Class:").grid(row=3, column=0, sticky='w')
ttk.Combobox(frame, textvariable=temp_class, values=list(TEMPERATURE_CLASSES.keys()), state='readonly').grid(row=3, column=1)

# Washer selections
tk.Checkbutton(frame, text="Washer under Bolt Head", variable=washer_under_head).grid(row=4, column=0, sticky='w')
tk.Checkbutton(frame, text="Washer under Nut", variable=washer_under_nut).grid(row=4, column=1, sticky='w')
tk.Label(frame, text="Washer Thickness (mm):").grid(row=5, column=0, sticky='w')
tk.Entry(frame, textvariable=custom_washer_thickness).grid(row=5, column=1)

# Safety allowance
tk.Label(frame, text="Safety Allowance (mm):").grid(row=6, column=0, sticky='w')
tk.Entry(frame, textvariable=safety_allowance).grid(row=6, column=1)

# Output expectations for user clarity
tk.Label(frame, text="\nExpected Output:", font=('Arial', 10, 'bold')).grid(row=7, column=0, columnspan=2, sticky='w', pady=10)
expected_outputs = [
    "• Recommended Bolt Type",
    "• Recommended Nut Type",
    "• Total Bolt Length (for through holes)",
    "• Thread Engagement (for blind holes)",
    "• Temperature-based length adjustment",
    "• Washer Consideration in Bolt Length",
    "• Recommended Tightening Torque",
    "• Visual Layout Preview (with GD&T style)"
]
for i, line in enumerate(expected_outputs):
    tk.Label(frame, text=line).grid(row=8 + i, column=0, columnspan=2, sticky='w')

# --------------------------- Diagram Function ---------------------------- #
def show_gear_preview(length):
    fig, ax = plt.subplots(figsize=(2, 6))
    ax.set_xlim(-5, 20)
    ax.set_ylim(0, length + 10)
    y = 0

    def draw_section(h, label, color):
        nonlocal y
        rect = patches.Rectangle((5, y), 5, h, linewidth=1, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.text(12, y + h/2, f"{label} ({h} mm)", va='center')
        y += h

    draw_section(safety_allowance.get(), "Safety", 'lightgray')
    if washer_under_nut.get():
        draw_section(custom_washer_thickness.get(), "Washer (Nut Side)", 'lightblue')
    draw_section(ASME_BOLT_SIZES['M10']['nut_height'], "Nut", 'orange')
    draw_section(plate_thickness.get(), "Plate", 'gray')
    if washer_under_head.get():
        draw_section(custom_washer_thickness.get(), "Washer (Head Side)", 'lightblue')
    draw_section(5, "Bolt Head", 'black')

    ax.set_title("Vertical Bolt Assembly View", fontsize=10)
    ax.axis('off')
    plt.tight_layout()
    plt.show()

# --------------------------- Calculation Logic ---------------------------- #
def calculate():
    try:
        sizes = list(ASME_BOLT_SIZES.keys())
        best_fit = None
        hole = hole_type.get()
        temp = temp_class.get()
        multiplier = TEMPERATURE_CLASSES[temp]

        washer_thickness = custom_washer_thickness.get()
        safety = safety_allowance.get()

        total_thickness = 0
        if washer_under_head.get():
            total_thickness += washer_thickness

        if hole == "Through Hole":
            total_thickness += plate_thickness.get()
            if washer_under_nut.get():
                total_thickness += washer_thickness

            max_req_len = total_thickness + max([v["nut_height"] for v in ASME_BOLT_SIZES.values()]) + 2 + safety

            for s in sizes:
                bolt_props = ASME_BOLT_SIZES[s]
                bolt_length = (plate_thickness.get() +
                               (washer_thickness if washer_under_head.get() else 0) +
                               (washer_thickness if washer_under_nut.get() else 0) +
                               bolt_props["nut_height"] + 2 + safety)
                final_length = round(bolt_length * multiplier)
                if final_length >= max_req_len:
                    best_fit = s
                    break

            if best_fit:
                torque = ASME_BOLT_SIZES[best_fit]['torque']
                show_gear_preview(final_length)
                messagebox.showinfo("Recommendation",
                    f"Recommended Bolt: {best_fit} Hex Bolt\n"
                    f"Recommended Nut: {best_fit} DIN 934\n"
                    f"Total Required Length: {final_length} mm\n"
                    f"Washer Thickness: {washer_thickness} mm each\n"
                    f"Safety Allowance: {safety} mm\n"
                    f"Temperature Adjustment Factor: {multiplier}\n"
                    f"Recommended Torque: {torque} Nm")
            else:
                messagebox.showwarning("Not Found", "No suitable bolt size found based on requirements.")

        elif hole == "Blind Hole":
            for s in sizes:
                bolt_props = ASME_BOLT_SIZES[s]
                min_engage = bolt_props["min_engagement"]
                depth_avail = depth.get() - (washer_thickness if washer_under_head.get() else 0) - safety
                if depth_avail >= min_engage:
                    best_fit = s
                    break

            if best_fit:
                torque = ASME_BOLT_SIZES[best_fit]['torque']
                show_gear_preview(depth.get())
                messagebox.showinfo("Recommendation",
                    f"Recommended Bolt: {best_fit} Socket Head Cap Screw\n"
                    f"Minimum Engagement: {ASME_BOLT_SIZES[best_fit]['min_engagement']} mm\n"
                    f"Depth Available: {depth_avail:.2f} mm\n"
                    f"Temperature Adjustment Factor: {multiplier}\n"
                    f"Recommended Torque: {torque} Nm")
            else:
                messagebox.showwarning("Insufficient Depth", "Depth is not sufficient for any standard bolt engagement.")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# --------------------------- Button ---------------------------- #
tk.Button(frame, text="Get Recommendation", command=calculate).grid(row=16, column=0, columnspan=2, pady=10)

root.mainloop()
