import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button

# --- 1. Initial Parameters & Constants ---
m = 1.0        # Mass (kg)
k_init = 5.0   # Initial spring constant (N/m)
b_init = 0.2   # Initial damping coefficient (kg/s)
F0_init = 0.0  # Initial driving amplitude (N)
wd_init = 1.0  # Initial driving frequency (rad/s)
speed_init = 1.0 

# Simulation state variables
x = 2.0        
v = 0.0        
t = 0.0        
base_dt = 0.04 

t_history, ke_history, pe_history, total_history = [], [], [], []
max_history_len = 150 
current_planet = "Earth"

# --- 2. Plot Layout Setup (Wider bottom space for sidebars) ---
fig, (ax_sim, ax_eng) = plt.subplots(1, 2, figsize=(13, 7))
# Adjusting subplots to leave a 25% margin on the left for the sidebar
plt.subplots_adjust(left=0.25, bottom=0.35) 

# Left Plot: Physics Window
ax_sim.set_xlim(-4, 4)
ax_sim.set_ylim(-1, 1)
ax_sim.get_yaxis().set_visible(False)
ax_sim.axhline(0, color='gray', linestyle='--')
mass, = ax_sim.plot([], [], 'bo', markersize=20)
time_text = ax_sim.text(-3.8, 0.8, '', fontsize=10)

# Right Plot: Energy Tracker
ax_eng.set_xlim(0, 6)
ax_eng.set_ylim(0, 15)
ax_eng.set_xlabel("Time (s)")
ax_eng.set_ylabel("Energy (Joules)")
ax_eng.grid(True, linestyle=':')
line_ke, = ax_eng.plot([], [], 'g-', label='Kinetic (KE)')
line_pe, = ax_eng.plot([], [], 'r-', label='Potential (PE)')
line_tot, = ax_eng.plot([], [], 'k--', linewidth=2, label='Total Energy')
ax_eng.legend(loc='upper right')

# --- 3. Creating the Vertical Sidebar Widgets (Left Side) ---
# Format: [left, bottom, width, height]
ax_title   = plt.axes([0.02, 0.85, 0.16, 0.05])
ax_earth   = plt.axes([0.02, 0.75, 0.16, 0.06])
ax_mars    = plt.axes([0.02, 0.67, 0.16, 0.06])
ax_jupiter = plt.axes([0.02, 0.59, 0.16, 0.06])
ax_moon    = plt.axes([0.02, 0.51, 0.16, 0.06])

# Make a decorative text box for the sidebar title
ax_title.axis('off')
title_text = ax_title.text(0.1, 0.3, "SPACE PRESETS", fontsize=11, fontweight='bold')

btn_earth   = Button(ax_earth, 'Earth\n(Standard Air)', color='lightblue', hovercolor='deepskyblue')
btn_mars    = Button(ax_mars, 'Mars\n(Thin Atmosphere)', color='coral', hovercolor='orangered')
btn_jupiter = Button(ax_jupiter, 'Jupiter\n(Crushing Drag)', color='goldenrod', hovercolor='darkgoldenrod')
btn_moon    = Button(ax_moon, 'Moon\n(Pure Vacuum)', color='darkgray', hovercolor='lightgray')

# --- 4. Creating Bottom Controls (Shifted right to match layout) ---
ax_k     = plt.axes([0.30, 0.24, 0.60, 0.03])
ax_b     = plt.axes([0.30, 0.19, 0.60, 0.03])
ax_F0    = plt.axes([0.30, 0.14, 0.60, 0.03])
ax_wd    = plt.axes([0.30, 0.09, 0.60, 0.03])
ax_speed = plt.axes([0.30, 0.04, 0.60, 0.03])
ax_reset = plt.axes([0.02, 0.35, 0.16, 0.05])

slider_k     = Slider(ax_k, 'Spring Const (k)', 0.1, 10.0, valinit=k_init)
slider_b     = Slider(ax_b, 'Damping (b)', 0.0, 4.0, valinit=b_init) # Max increased to 4 for Jupiter
slider_F0    = Slider(ax_F0, 'Driving Force (F0)', 0.0, 5.0, valinit=F0_init)
slider_wd    = Slider(ax_wd, 'Drive Freq (wd)', 0.1, 5.0, valinit=wd_init)
slider_speed = Slider(ax_speed, 'Time Speed', 0.0, 3.0, valinit=speed_init)
btn_reset    = Button(ax_reset, 'RESET ALL', color='silver', hovercolor='tomato')

# --- 5. Interactive Preset Behaviors ---
def apply_earth(event):
    global current_planet
    current_planet = "Earth"
    slider_b.set_val(0.2)   # Normal standard air resistance
    slider_k.set_val(5.0)   # Normal spring tension

def apply_mars(event):
    global current_planet
    current_planet = "Mars"
    slider_b.set_val(0.03)  # Thin atmosphere means barely any drag
    slider_k.set_val(4.0)   # Simulating a slightly relaxed thermal spring environment

def apply_jupiter(event):
    global current_planet
    current_planet = "Jupiter"
    slider_b.set_val(3.5)   # Super thick, crushing gas atmosphere = ultra high damping
    slider_k.set_val(9.0)   # High pressure forces acting on system mechanics

def apply_moon(event):
    global current_planet
    current_planet = "Moon"
    slider_b.set_val(0.0)   # Absolute vacuum. Zero damping!

def reset_simulation(event):
    global x, v, t, t_history, ke_history, pe_history, total_history, current_planet
    x, v, t = 2.0, 0.0, 0.0
    t_history.clear(); ke_history.clear(); pe_history.clear(); total_history.clear()
    current_planet = "Earth"
    slider_k.reset(); slider_b.reset(); slider_F0.reset(); slider_wd.reset(); slider_speed.reset()

# Hook up callbacks
btn_earth.on_clicked(apply_earth)
btn_mars.on_clicked(apply_mars)
btn_jupiter.on_clicked(apply_jupiter)
btn_moon.on_clicked(apply_moon)
btn_reset.on_clicked(reset_simulation)

# --- 6. The Physics Engine ---
def update(frame):
    global x, v, t
    
    k = slider_k.val
    b = slider_b.val
    F0 = slider_F0.val
    wd = slider_wd.val
    dt = base_dt * slider_speed.val
    
    # Physics Loop
    F_net = (-k * x) + (-b * v) + (F0 * np.cos(wd * t))
    a = F_net / m        
    v = v + a * dt       
    x = x + v * dt       
    t = t + dt           
    
    if abs(x) > 4: 
        x = np.sign(x) * 4
        v = 0
        
    # Process Energy Data
    ke = 0.5 * m * (v**2)
    pe = 0.5 * k * (x**2)
    total_e = ke + pe
    
    t_history.append(t)
    ke_history.append(ke)
    pe_history.append(pe)
    total_history.append(total_e)
    
    if len(t_history) > max_history_len:
        t_history.pop(0); ke_history.pop(0); pe_history.pop(0); total_history.pop(0)
        
    # Update Graphics
    mass.set_data([x], [0])
    ax_sim.set_title(f"Physical System Location: {current_planet}", color='darkblue', fontweight='bold')
    time_text.set_text(f"Time: {t:.2f}s\nPosition: {x:.2f}m\nLocal Damping: {b:.2f}")
    
    line_ke.set_data(t_history, ke_history)
    line_pe.set_data(t_history, pe_history)
    line_tot.set_data(t_history, total_history)
    
    if len(t_history) > 0:
        ax_eng.set_xlim(t_history[0], max(t_history[0] + 6, t_history[-1]))
        current_max_energy = max(total_history)
        if current_max_energy > ax_eng.get_ylim()[1] - 2:
            ax_eng.set_ylim(0, current_max_energy + 5)
            
    return mass, time_text, line_ke, line_pe, line_tot

# --- 7. Fire up Dashboard ---
ani = animation.FuncAnimation(fig, update, frames=200, interval=40, blit=False, cache_frame_data=False)
plt.show()
