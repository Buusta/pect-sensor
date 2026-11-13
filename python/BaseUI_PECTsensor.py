import tkinter as tk
from tkinter import ttk
import numpy as np

# Import stuff from other python files
import pec_sensor as pec
import pect as p

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

test_data = p.DataProcessor(file='calibration.csv')
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
menu_test.add_command(label=';)')
menu_test.add_command(label ='Exit', command= lambda: exit())

# Connection
connection_label = tk.Label(
    root,
    text="Not Connected",
    font=("Arial", 10)
)
connection_label.pack(side=tk.TOP)

for p in sensor.protocol.available_ports:
    menu_ports.add_command(label=f'{p}', command= lambda p=p: [sensor.protocol.connect(p.vid),
                                                               connection_label.config(
                                                                   text=f"Connected via: {p}"
                                                                   )])
    
if not sensor.protocol.serial == None:
    if sensor.protocol.serial.is_open == True:
        menu_ports.add_separator()
        menu_ports.add_command(label='Disconnect', command= lambda: [sensor.protocol.disconnect(),
                                                                    connection_label.config(
                                                                        text=f"Disconnected"
                                                                        )])
else:
    menu_ports.add_command(label='No port found', state="disabled")

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

# Matplotlib figure
fig = Figure(figsize=(7, 4))
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)

data = []

running = False
after_id = None

def update_graph():
    global data, after_id

    if not running:
        return

    keuze = dropdown.get()

    # Nieuwe meetwaarde simuleren !!DIT VERVANGEN MET UITEINDELIJK REËLE DATA!!
    Residuals = np.random.normal(10, 2, 20)
    Fit = np.random.normal(10, 1, 20)
    Tesla = np.random.normal(10, 5, 20)

    data = Residuals
    data_fit = Fit
    raw_data = Tesla

    if keuze == "Residuals en Fit":
        ax.clear()
        ax.plot(data, label="Residuals", color="red")
        ax.plot(data_fit, label="Fit", color="blue")

    elif keuze == "Residuals":
        ax.clear()
        ax.plot(data, label="Residuals", color="red")

    elif keuze == "Fit":
        ax.clear()
        ax.plot(data_fit, label="Fit", color="blue")

    elif keuze == "Raw Hallsensor Data":
        ax.clear()
        ax.plot(raw_data, label="Raw Hallsensor Data", color="green")

        # Actual calibration data from pect.py | Doesnt work yet tho 
        #p.plot_signal(data=test_data, label="Raw Hallsensor Data")

    ax.legend(loc="upper right")
    ax.set_ylim(0, 25)
    ax.set_title("Live metingen")
    ax.set_ylabel("Intensiteit (in mT)")
    ax.set_xlabel("Tijd (in milliseconden)")

    canvas.draw()

    average = np.mean(data)
    data_label.config(
        text=f"{average:.3f}",
        foreground="#039903"
    )

    after_id = root.after(100, update_graph)


# Start knop
def start():
    global running

    if not running:
        running = True
        update_graph()

# Stop knop
def stop():
    global running, after_id

    running = False

    if after_id is not None:
        root.after_cancel(after_id)
        after_id = None


# Knoppen
button_frame = tk.Frame(root)
button_frame.pack()

start_button = tk.Button(
    button_frame,
    text="Start",
    command=start
)
start_button.pack(side=tk.LEFT, padx=5, pady=5)

stop_button = tk.Button(
    button_frame,
    text="Stop",
    command=stop
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
