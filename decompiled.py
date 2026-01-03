import time
import threading
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key, KeyCode, Listener

# --- Globals & Constants ---
mouse = MouseController()
keyboard = KeyboardController()

run_thread = None
run_lock = threading.Lock()
is_running = False

exit_key = Key.f12
toggle_ui_key = Key.end
start_key = Key.f6
capture_start_key = False

# Macro Timing Constants
CLICK_PERIOD = 0.0437
HOLD_TIME = 0.03
PHASE2_DURATION = 1.85
BRACKET_OFFSET = 1.61
PHASE1_TOTAL = 2.01
TOTAL_DURATION = PHASE1_TOTAL + PHASE2_DURATION

macro_start_time = None

# --- Helper Functions ---

def key_signature(k):
    # Generates a unique signature for a key to allow easy comparison
    if isinstance(k, Key):
        return ('Key', k.name)
    if isinstance(k, KeyCode):
        if k.char:
            return ('Char', k.char.lower())
        return ('Vk', k.vk)
    return ('Other', str(k))

def keys_equal(a, b):
    return key_signature(a) == key_signature(b)

def key_to_label(k):
    # Converts a key object to a readable string for the UI
    if isinstance(k, Key):
        if k.name: return str(k.name).upper()
    if isinstance(k, KeyCode):
        if k.char: return k.char.upper()
        return f"VK_{k.vk}"
    return "UNKNOWN"

# --- UI Helper Functions ---

def set_status(text):
    root.after(0, status_var.set, text)

def refresh_start_key_label():
    root.after(0, lambda: start_key_var.set(f"Start key: {key_to_label(start_key)}"))

def toggle_ui():
    global ui_visible
    if ui_visible:
        ui_visible = False
        root.withdraw()
    else:
        ui_visible = True
        root.deiconify()
        root.lift()
        root.attributes('-topmost', True)

def apply_size(height):
    x, y = root.winfo_x(), root.winfo_y()
    root.geometry(f"{UI_W}x{height}+{x}+{y}")

def set_minimized(mini):
    global is_minimized
    is_minimized = mini
    if is_minimized:
        for w in expanded_widgets:
            w.place_forget()
        mini_status_lbl.place(x=20, y=65)
        mini_bar.place(x=20, y=90, width=360, height=18)
        minimize_btn.config(text='▢')
        apply_size(MINI_H)
    else:
        mini_status_lbl.place_forget()
        mini_bar.place_forget()
        for w, cfg in expanded_layout:
            w.place(**cfg)
        minimize_btn.config(text='—')
        apply_size(UI_H)

def toggle_minimize():
    set_minimized(not is_minimized)

# Custom Window Dragging Logic
_drag = {'x': 0, 'y': 0}

def start_drag(e):
    _drag['x'] = e.x
    _drag['y'] = e.y

def do_drag(e):
    x = root.winfo_x() + (e.x - _drag['x'])
    y = root.winfo_y() + (e.y - _drag['y'])
    root.geometry(f"+{x}+{y}")

def set_controls_enabled(enabled):
    state = 'normal' if enabled else 'disabled'
    change_key_btn.config(state=state)
    exit_btn.config(state=state)
    close_btn.config(state=state)

def try_exit():
    with run_lock:
        if is_running: return # Don't exit while running
    root.destroy()

def update_progress_loop():
    with run_lock:
        running = is_running
        start_t = macro_start_time
    
    if running and start_t is not None:
        elapsed = time.perf_counter() - start_t
        pct = max(0.0, min(100.0, (elapsed / TOTAL_DURATION) * 100.0))
        progress_var.set(pct)
        root.after(20, update_progress_loop)
    else:
        progress_var.set(0.0)

def wait_until(target_time):
    # Precision sleep loop
    while True:
        now = time.perf_counter()
        if now >= target_time: break
        remaining = target_time - now
        if remaining > 0.01:
            time.sleep(0.005)
        else:
            time.sleep(0.001)

def tap_key(key_char, dwell):
    keyboard.press(key_char)
    time.sleep(dwell)
    keyboard.release(key_char)

# --- Main Macro Logic ---

def run_macro_once():
    # Phase 1: Setup
    phase1_start = time.perf_counter()
    mouse.press(Button.left)
    wait_until(phase1_start + 0.9)
    mouse.release(Button.left)
    
    wait_until(phase1_start + 0.9 + 0.05)
    
    keyboard.press('[')
    wait_until(time.perf_counter() + 0.06)
    keyboard.release('[')
    
    time.sleep(0.008)
    wait_until(time.perf_counter() + 1.0)
    
    # Phase 2: Action Loop
    p2_start = time.perf_counter()
    p2_end = p2_start + PHASE2_DURATION
    bracket_time = p2_start + BRACKET_OFFSET
    bracket_done = False
    next_click_time = p2_start
    
    while True:
        now = time.perf_counter()
        if now >= p2_end: break
        
        # Trigger bracket spam at specific offset
        if not bracket_done and now >= bracket_time:
            tap_key('[', 0.004)
            tap_key('[', 0.004)
            tap_key('[', 0.004)
            tap_key('[', 0.004)
            bracket_done = True
        
        # Trigger periodic clicks
        if now >= next_click_time:
            if (now - next_click_time) > CLICK_PERIOD * 2:
                next_click_time = now # Catch up if lagging
            
            mouse.press(Button.left)
            wait_until(time.perf_counter() + HOLD_TIME)
            mouse.release(Button.left)
            
            next_click_time += CLICK_PERIOD
            continue 
            
        # Efficient waiting
        next_event = min(next_click_time, p2_end)
        if not bracket_done:
            next_event = min(next_event, bracket_time)
            
        remaining = next_event - time.perf_counter()
        if remaining > 0:
            time.sleep(min(remaining, 0.005))

def worker():
    global is_running, macro_start_time
    try:
        run_macro_once()
        set_status('Done. Press start key to run again.')
    except Exception:
        pass
    finally:
        # Cleanup state
        try: mouse.release(Button.left)
        except: pass
        try: keyboard.release('[')
        except: pass
        
        with run_lock:
            is_running = False
            macro_start_time = None
        
        root.after(0, lambda: progress_var.set(100.0))
        root.after(400, lambda: progress_var.set(0.0))
        root.after(0, lambda: set_controls_enabled(True))

def start_macro():
    global is_running, macro_start_time, run_thread
    with run_lock:
        if is_running: return
        is_running = True
        macro_start_time = time.perf_counter()
        
    set_controls_enabled(False)
    progress_var.set(0.0)
    set_status('IN PROGRESS')
    root.after(0, update_progress_loop)
    
    run_thread = threading.Thread(target=worker, daemon=True)
    run_thread.start()

def begin_capture_start_key():
    global capture_start_key
    with run_lock:
        if is_running: return
    capture_start_key = True
    set_status('Press a key to set as START (global).')

def on_press(key):
    global start_key, capture_start_key, ui_visible
    
    if keys_equal(key, toggle_ui_key):
        root.after(0, toggle_ui)
        return

    if capture_start_key:
        if keys_equal(key, exit_key) or keys_equal(key, toggle_ui_key):
            set_status('That key is reserved. Pick another.')
            return
        start_key = key
        capture_start_key = False
        refresh_start_key_label()
        set_status('Start key updated.')
        return

    if keys_equal(key, start_key):
        root.after(0, start_macro)
        return

    if keys_equal(key, exit_key):
        with run_lock:
            running = is_running
        if not running:
            root.after(0, try_exit)
            return False # Stop listener

# --- UI Setup ---

UI_W, UI_H = 400, 500
MINI_H = 120

root = tk.Tk()
root.overrideredirect(True) # Remove title bar
root.attributes('-topmost', True)
root.geometry(f"{UI_W}x{UI_H}+40+40")
root.configure(bg='#0b0b0b')

style = ttk.Style(root)
style.theme_use('clam')
style.configure('Gray.Horizontal.TProgressbar',
                troughcolor='#2a2a2a', background='#7a7a7a',
                bordercolor='#2a2a2a', lightcolor='#7a7a7a', darkcolor='#7a7a7a')

ui_visible = True
is_minimized = False

status_var = tk.StringVar(value='Idle')
start_key_var = tk.StringVar(value=f"Start key: {key_to_label(start_key)}")
progress_var = tk.DoubleVar(value=0.0)

# Custom Header (Title Bar)
header = tk.Frame(root, bg='#111111', width=UI_W, height=48)
header.place(x=0, y=0)
header.bind('<Button-1>', start_drag)
header.bind('<B1-Motion>', do_drag)

title = tk.Label(header, text="funny arc throw macro by c.", fg='white', bg='#111111', font=('Segoe UI', 14, 'bold'))
title.place(x=14, y=10)
title.bind('<Button-1>', start_drag)
title.bind('<B1-Motion>', do_drag)

minimize_btn = tk.Button(header, text='—', fg='white', bg='#111111', activebackground='#1a1a1a', 
                         activeforeground='white', bd=0, command=lambda: root.after(0, toggle_minimize))
minimize_btn.place(x=UI_W - 84, y=8, width=34, height=32)

close_btn = tk.Button(header, text='✕', fg='white', bg='#111111', activebackground='#1a1a1a', 
                      activeforeground='white', bd=0, command=lambda: root.after(0, try_exit))
close_btn.place(x=UI_W - 42, y=8, width=34, height=32)

# Main UI Elements
status_lbl = tk.Label(root, textvariable=status_var, fg='#cfcfcf', bg='#0b0b0b', font=('Segoe UI', 11))
startkey_lbl = tk.Label(root, textvariable=start_key_var, fg='#9a9a9a', bg='#0b0b0b', font=('Segoe UI', 11))
instructions = tk.Label(root, text="• Press your START key to run.\n• Click 'Change Start Key' then press a key.\n• Toggle UI with END.\n• Exit with F12 (only when not running).", 
                        fg='#8a8a8a', bg='#0b0b0b', justify='left', font=('Segoe UI', 10))

change_key_btn = tk.Button(root, text='Change Start Key', font=('Segoe UI', 11), command=lambda: root.after(0, begin_capture_start_key))
exit_btn = tk.Button(root, text='EXIT (F12)', font=('Segoe UI', 11), command=lambda: root.after(0, try_exit))

panel = tk.Frame(root, bg='#101010')
panel_label = tk.Label(panel, text='(Customize your UI here)', fg='#6f6f6f', bg='#101010', font=('Segoe UI', 10))

mini_status_lbl = tk.Label(root, textvariable=status_var, fg='#cfcfcf', bg='#0b0b0b', font=('Segoe UI', 11))
mini_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', maximum=100.0, variable=progress_var, style='Gray.Horizontal.TProgressbar')

# Layout Configuration
expanded_layout = [
    (status_lbl, {'x': 20, 'y': 70}),
    (startkey_lbl, {'x': 20, 'y': 105}),
    (instructions, {'x': 20, 'y': 150}),
    (change_key_btn, {'x': 20, 'y': 250, 'width': 360, 'height': 48}),
    (exit_btn, {'x': 20, 'y': 310, 'width': 360, 'height': 48}),
    (panel, {'x': 20, 'y': 380, 'width': 360, 'height': 100})
]
expanded_widgets = [w for w, _ in expanded_layout]
panel_label.place(x=10, y=10)

# Initial Setup
set_minimized(False)
set_controls_enabled(True)
set_status('Idle (press start key)')

listener = Listener(on_press=on_press)
listener.daemon = True
listener.start()

root.mainloop()