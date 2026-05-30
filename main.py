###############################################################
# Gravitational Tunnel Through Earth
####

from vpython import *

scene.width = 900
scene.height = 600
scene.background = color.black
scene.title = "Gravitational Tunnel With Layered Density and Tube"

###############################################################
# --------------------- User Toggles -------------------------- #
###############################################################

# Tunnel direction:
# True  = left <-> right (x-axis)
# False = up <-> down (y-axis)
HORIZONTAL = True      

# Gravity Model:
USE_UNIFORM_DENSITY = False    # Simple harmonic motion
USE_LAYERED_DENSITY = True   # Realistic Earth layers

# Optional effects:
USE_AIR_DRAG = True
USE_ROTATION = True

###############################################################
# -------------------- Physical Parameters -------------------- #
###############################################################

G = 6.67430e-11
Re = 6.371e6  
Me = 5.972e24         

rho_uniform = Me / ((4/3)*pi*Re**3)

dt = 0.2
t = 0

m = 70   # mass of falling object

###############################################################
# ----------------- Layered Density Structure ----------------- #
###############################################################

# PREM-style simplified density profile (radius, density)
layers = [
    (1221e3, 13000),  # inner core
    (3480e3, 11200),  # outer core
    (5701e3, 5500),   # lower mantle
    (Re,     3500)    # upper mantle
]

def rho_layered(r):
    """Return density at radius r using PREM-style layers."""
    for boundary, density in layers:
        if r <= boundary:
            return density
    return 0

###############################################################
# -------------- Function to Build Tunnel Geometry ------------ #
###############################################################

def define_tunnel():
    if HORIZONTAL:
        # left ↔ right
        A = vector(-Re, 0, 0)
        B = vector(+Re, 0, 0)
    else:
        # up ↕ down
        A = vector(0, +Re, 0)
        B = vector(0, -Re, 0)

    axis_vec = norm(B - A)
    length = mag(B - A)
    return A, B, axis_vec, length

# Get geometry based on toggle
A, B, axis_vec, tunnel_length = define_tunnel()

###############################################################
# ----------------------- Visual Setup ------------------------ #
###############################################################

earth = sphere(pos=vector(0,0,0), radius=Re,
               color=color.blue, opacity=0.2)

# ------------------- Visual Tunnel ------------------------
tunnel_radius = 1e5  # visual thickness of tunnel
tunnel = cylinder(pos=A, axis=(B-A), radius=tunnel_radius,
                  color=color.white, opacity=0.2)

# Mass object
mass = sphere(pos=A, radius=1e5, color=color.red, make_trail=True)
v = vector(0,0,0)

###############################################################
# ---------------- Gravitational Acceleration ---------------- #
###############################################################

def gravity_accel(pos):
    r = mag(pos)
    if r == 0:
        return vector(0,0,0)

    # ------------- Uniform Density Model -------------
    if USE_UNIFORM_DENSITY:
        factor = -(4/3) * pi * G * rho_uniform
        return factor * pos

    # ------------- Layered Density Model -------------
    if USE_LAYERED_DENSITY:
        # Numerical integration of enclosed mass
        N = 150
        dr = r / N
        enclosed_mass = 0

        for i in range(N):
            shell_r = (i + 0.5) * dr
            shell_vol = 4 * pi * shell_r**2 * dr
            enclosed_mass += rho_layered(shell_r) * shell_vol

        return -(G * enclosed_mass / (r**3)) * pos

    return vector(0,0,0)

###############################################################
# ------------------ Air Drag (Optional) --------------------- #
###############################################################

def air_drag(v):
    if not USE_AIR_DRAG:
        return vector(0,0,0)
    rho_air = 1.2
    Cd = 0.5
    A_cross = 0.5
    return -0.5 * rho_air * Cd * A_cross * mag(v) * v

###############################################################
# ---------------- Rotation (Optional) ----------------------- #
###############################################################

omega = vector(0, 2*pi/86400, 0)

def coriolis(v):
    if not USE_ROTATION:
        return vector(0,0,0)
    return -2 * cross(omega, v)

###############################################################
# --------------------- Data Graph ---------------------------- #
###############################################################

graph_speed = graph(title="Speed vs Time",
                    xtitle="t (s)", ytitle="speed (m/s)")
g_speed = gcurve(color=color.green)

###############################################################
# --------------------- Simulation Loop ----------------------- #
###############################################################

while True:
    rate(10000000000)

    a = gravity_accel(mass.pos)
    a += air_drag(v) / m
    a += coriolis(v)

    v += a * dt
    mass.pos += v * dt

    g_speed.plot(t, mag(v))

    t += dt
