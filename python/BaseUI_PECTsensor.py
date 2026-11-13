import tkinter as tk
from tkinter import ttk
import numpy as np

# Import stuff from other python files
import pec_sensor as pec
import pect as pect

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

test_data = pect.DataProcessor(file='calibration.csv')
#print(test_data)

dispatch = lambda fn: root.after(0, fn)
sensor = pec.PECSensor(dispatch=dispatch)
#print(sensor.protocol.available_ports)

root = tk.Tk()
root.wm_title("PECT-control")

def exit():
    sensor.protocol.disconnect()
    root.destroy()

# Top menu
menubar = tk.Menu(root)
root['menu'] = menubar

# Test function
def test():
    print(2+2)

menu_ports = tk.Menu(menubar, tearoff = 0)
menu_test = tk.Menu(menubar, tearoff = 0)
menubar.add_cascade(menu=menu_ports, label='Ports')
menubar.add_cascade(menu=menu_test, label='Test')

menu_test.add_command(label='2+2', command= lambda: test())
menu_test.add_command(label='serial', command= lambda: print(sensor.protocol.serial.is_open))
menu_test.add_command(label ='Exit', command= lambda: exit())

# Connection
connection_label = tk.Label(
    root,
    text="Not Connected",
    font=("Arial", 10)
)
connection_label.pack(side=tk.TOP)

# Disconnect button
def disconnect_button():
    if not sensor.protocol.serial == None:
        if sensor.protocol.serial.is_open == True:
            menu_ports.entryconfigure(
                "Disconnect",
                state='normal'
            )

for p in sensor.protocol.available_ports:
    menu_ports.add_command(label=f'{p}', command= lambda p=p: [sensor.protocol.connect(p.vid),
                                                               connection_label.config(text=f"Connected via: {p}"),
                                                               disconnect_button()])
if sensor.protocol.available_ports == []:
    menu_ports.add_command(label='No port found', state="disabled", command=None)

menu_ports.add_separator()
menu_ports.add_command(label='Disconnect',
                       command= lambda: [sensor.protocol.disconnect(),
                                        connection_label.config(text=f"Disconnected"),
                                        menu_ports.entryconfigure(
                                                        "Disconnect",
                                                        state='disabled'
                                                        )],
                        state='disabled')

# Labels voor de gemiddelde waarde
average_label = tk.Label(
    root,
    text="Average/Gemiddelde: ",
    font=("Arial", 14, "bold")
)
average_label.pack(side=tk.TOP, pady=10)

data_label = tk.Label(
    root,
    text="Wachten op data...",
    foreground="#B50000",
    font=("Arial", 18, "bold")
)
data_label.pack(side=tk.TOP, pady=5)

# Knoppen
button_frame = tk.Frame(root)
button_frame.pack()

start_button = tk.Button(
    button_frame,
    text="Start"
)
start_button.pack(side=tk.LEFT, padx=5, pady=5)

stop_button = tk.Button(
    button_frame,
    text="Stop"
)
stop_button.pack(side=tk.LEFT, padx=5, pady=5)

# Dropdown menu om meetdata aan te passen
dropdown = ttk.Combobox(
    root,
    values=["Residuals en Fit",
            "Fit",
            "Residuals",
            "Raw Hallsensor Data"],
    state="readonly"
)

dropdown.current(0)
dropdown.pack(pady=10)

# MATPLOTLIB FIGURE
fig = Figure(figsize=(7, 4))
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# DATA & VARIABLES
graph_data = {
    "Residuals": [],
    "Fit": [],
    "Tesla": []
}

running = False
after_id = None

# GRAPH DISPLAY
def update_graph_display():

    keuze = dropdown.get()

    ax.clear()

    if keuze == "Residuals en Fit":
        ax.plot(graph_data["Residuals"],
                label="Residuals", color="red")

        ax.plot(graph_data["Fit"],
                label="Fit", color="blue")

    elif keuze == "Residuals":
        ax.plot(graph_data["Residuals"],
                label="Residuals", color="red")

    elif keuze == "Fit":
        ax.plot(graph_data["Fit"],
                label="Fit", color="blue")

    elif keuze == "Raw Hallsensor Data":
        ax.plot(graph_data["Tesla"],
                label="Raw Hallsensor Data", color="green")

    ax.legend(loc="upper right")
    ax.set_ylim(0, 25)
    ax.set_title("Live metingen")
    ax.set_ylabel("Intensiteit (in mT)")
    ax.set_xlabel("Tijd (in milliseconden)")

    canvas.draw_idle()

    # Gemiddelde weergeven
    if len(graph_data["Residuals"]) > 0:
        average = np.mean(graph_data["Residuals"])

        data_label.config(
            text=f"{average:.3f}",
            foreground="#039903"
        )


# DATA UPDATE
def update_graph():

    global after_id

    if not running:
        return

    # Nieuwe meetwaarden simuleren
    # DIT LATER VERVANGEN MET REËLE SENSOR DATA

    graph_data["Residuals"] = np.random.normal(10, 2, 20)
    graph_data["Fit"] = np.random.normal(10, 1, 20)
    graph_data["Tesla"] = np.random.normal(10, 5, 20)
    
    # Grafiek vernieuwen
    update_graph_display()

    # Opnieuw uitvoeren na 100 ms
    after_id = root.after(100, update_graph)


# START / STOP
def start():

    global running

    if not running:
        running = True
        update_graph()

def stop():

    global running

    if running:
        running = False
        update_graph()

start_button.config(command=start)
stop_button.config(command=stop)

# pack_toolbar=False will make it easier to use a layout manager later on.
toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

canvas.mpl_connect(
    "key_press_event", lambda event: print(f"you pressed {event.key}"))
canvas.mpl_connect("key_press_event", key_press_handler)

button_quit = tk.Button(master=root, text="Quit", command= lambda: exit())
button_quit.pack(side=tk.BOTTOM, pady=10)

toolbar.pack(side=tk.BOTTOM, fill=tk.X)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root.mainloop()
