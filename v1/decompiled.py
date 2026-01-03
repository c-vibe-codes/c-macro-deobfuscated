#!/usr/bin/env python3
"""
main.py - V1 Macro
funny arc throw macro by c.
Reconstructed from Python 3.14 bytecode
"""

# Line 1-6: Imports
import time                                          # line 1
import threading                                     # line 2
import tkinter as tk                                 # line 3
from tkinter import ttk                              # line 4
from pynput.mouse import Controller as MouseController, Button  # line 5
from pynput.keyboard import Controller as KeyboardController, Key, KeyCode, Listener  # line 6

# Line 11-12: Controllers
mouse = MouseController()
keyboard = KeyboardController()

# Line 17-19: Global state
run_thread = None
run_lock = threading.Lock()
is_running = False

# Line 24-27: Key bindings
exit_key = Key.f12
toggle_ui_key = Key.end
start_key = Key.f6
capture_start_key = False

# Line 32-38: Timing constants
CLICK_PERIOD = 0.0437
HOLD_TIME = 0.03
PHASE2_DURATION = 1.85
BRACKET_OFFSET = 1.61

PHASE1_TOTAL = 2.01
TOTAL_DURATION = PHASE1_TOTAL + PHASE2_DURATION

# Line 40: macro timing
macro_start_time = None


# Line 46-53: key_signature function
def key_signature(k):
    # line 47
    if isinstance(k, Key):
        # line 48
        return ('Key', k.name)
    # line 49
    if isinstance(k, KeyCode):
        # line 50
        if k.char:
            # line 51
            return ('Char', k.char.lower())
        # line 52
        return ('Vk', k.vk)
    # line 53
    return ('Other', str(k))


# Line 56-57: keys_equal function
def keys_equal(a, b):
    return key_signature(a) == key_signature(b)


# Line 60-70: key_to_label function
def key_to_label(k):
    # line 61
    if isinstance(k, Key):
        # line 62
        return (k.name or str(k)).upper()
    # line 63
    if isinstance(k, KeyCode):
        # line 64
        if k.char:
            # line 65
            return k.char.upper()
        # line 66
        return f'VK_{k.vk}'
    # line 67
    return 'UNKNOWN'


# Line 73-74: UI Constants
UI_W, UI_H = 400, 500
MINI_H = 120

# Line 76-80: Create root window
root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.geometry(f'{UI_W}x{UI_H}+40+40')
root.configure(bg='#0b0b0b')

# Line 83-95: Style setup
style = ttk.Style(root)
try:
    # line 85
    style.theme_use('clam')
except Exception:
    # line 87
    pass

# line 89-95
style.configure(
    'Gray.Horizontal.TProgressbar',
    troughcolor='#2a2a2a',
    background='#7a7a7a',
    bordercolor='#2a2a2a',
    lightcolor='#7a7a7a',
    darkcolor='#7a7a7a'
)

# Line 98-99: UI state
ui_visible = True
is_minimized = False

# Line 101-103: Variables
status_var = tk.StringVar(value='Idle')
start_key_var = tk.StringVar(value=f'Start key: {key_to_label(start_key)}')
progress_var = tk.DoubleVar(value=0.0)


# Line 106-108: set_status function
def set_status(text: str):
    try:
        status_var.set(text)
    except Exception:
        pass


# Line 110-112: refresh_start_key_label function
def refresh_start_key_label():
    try:
        start_key_var.set(f'Start key: {key_to_label(start_key)}')
    except Exception:
        pass


# Line 114-125: toggle_ui function
def toggle_ui():
    global ui_visible
    # line 116
    ui_visible = not ui_visible
    # line 117
    if ui_visible:
        # line 118
        root.deiconify()
        # line 119
        root.lift()
    else:
        # line 121
        root.withdraw()


# Line 127-130: apply_size function
def apply_size(h: int):
    root.geometry(f'{UI_W}x{h}')


# Line 132-155: set_minimized function
def set_minimized(mini: bool):
    global is_minimized
    # line 134
    is_minimized = mini
    # line 135
    if mini:
        # line 136
        apply_size(MINI_H)
        # line 137
        for w in expanded_widgets:
            # line 138
            try:
                w.place_forget()
            except Exception:
                pass
        # line 142
        try:
            mini_status_lbl.place(x=20, y=58)
        except Exception:
            pass
        # line 146
        try:
            mini_bar.place(x=20, y=88, width=UI_W - 40, height=8)
        except Exception:
            pass
    else:
        # line 150
        apply_size(UI_H)
        # line 151
        try:
            mini_status_lbl.place_forget()
            mini_bar.place_forget()
        except Exception:
            pass
        # line 153
        for w, cfg in expanded_layout:
            try:
                w.place(**cfg)
            except Exception:
                pass


# Line 157-159: toggle_minimize function
def toggle_minimize():
    set_minimized(not is_minimized)


# Line 162-171: Drag support
_drag = {'x': 0, 'y': 0}


def start_drag(event):
    _drag['x'] = event.x
    _drag['y'] = event.y


def do_drag(event):
    x = root.winfo_x() + event.x - _drag['x']
    y = root.winfo_y() + event.y - _drag['y']
    root.geometry(f'+{x}+{y}')


# Line 174-183: Header frame
header = tk.Frame(root, bg='#111111', width=UI_W, height=48)
header.place(x=0, y=0)
header.bind('<Button-1>', start_drag)
header.bind('<B1-Motion>', do_drag)

# Line 179-183: Title label
title = tk.Label(header, text='funny arc throw macro by c.', fg='white', bg='#111111', font=('Segoe UI', 14, 'bold'))
title.place(x=14, y=10)
title.bind('<Button-1>', start_drag)
title.bind('<B1-Motion>', do_drag)

# Line 186-191: Minimize button
minimize_btn = tk.Button(
    header, text='—', fg='white', bg='#111111',
    activebackground='#1a1a1a', activeforeground='white',
    bd=0, command=lambda: toggle_minimize()
)
minimize_btn.place(x=UI_W - 84, y=8, width=34, height=32)

# Line 194-199: Close button
close_btn = tk.Button(
    header, text='✕', fg='white', bg='#111111',
    activebackground='#1a1a1a', activeforeground='white',
    bd=0
)
close_btn.place(x=UI_W - 42, y=8, width=34, height=32)

# Line 202-205: Status label
status_lbl = tk.Label(root, textvariable=status_var, fg='#cfcfcf', bg='#0b0b0b', font=('Segoe UI', 11))

# Line 204-205: Start key label
startkey_lbl = tk.Label(root, textvariable=start_key_var, fg='#9a9a9a', bg='#0b0b0b', font=('Segoe UI', 11))

# Line 207-218: Instructions
instructions = tk.Label(
    root,
    text="• Press your START key to run.\n• Click 'Change Start Key' then press a key.\n• Toggle UI with END.\n• Exit with F12 (only when not running).",
    fg='#8a8a8a', bg='#0b0b0b', justify='left', font=('Segoe UI', 10)
)

# Line 221-222: Buttons
change_key_btn = tk.Button(root, text='Change Start Key', font=('Segoe UI', 11))
exit_btn = tk.Button(root, text='EXIT (F12)', font=('Segoe UI', 11))

# Line 224-226: Panel
panel = tk.Frame(root, bg='#101010')
panel_label = tk.Label(panel, text='(Customize your UI here)', fg='#6f6f6f', bg='#101010', font=('Segoe UI', 10))

# Line 229-237: Mini mode widgets
mini_status_lbl = tk.Label(root, textvariable=status_var, fg='#cfcfcf', bg='#0b0b0b', font=('Segoe UI', 11))
mini_bar = ttk.Progressbar(
    root, orient='horizontal', mode='determinate',
    maximum=100.0, variable=progress_var,
    style='Gray.Horizontal.TProgressbar'
)

# Line 240-246: Expanded layout definition
expanded_layout = [
    (status_lbl, {'x': 20, 'y': 70}),
    (startkey_lbl, {'x': 20, 'y': 105}),
    (instructions, {'x': 20, 'y': 150}),
    (change_key_btn, {'x': 20, 'y': 250, 'width': 360, 'height': 48}),
    (exit_btn, {'x': 20, 'y': 310, 'width': 360, 'height': 48}),
    (panel, {'x': 20, 'y': 380, 'width': 360, 'height': 100}),
]

# Line 248: Extract widgets
expanded_widgets = [w for w, _ in expanded_layout]

# Line 250-251: Place all widgets
for w, cfg in expanded_layout:
    w.place(**cfg)

# Line 252: Place panel label
panel_label.place(x=10, y=10)


# Line 255-261: set_controls_enabled function
def set_controls_enabled(enabled: bool):
    state = 'normal' if enabled else 'disabled'
    try:
        change_key_btn.config(state=state)
        exit_btn.config(state=state)
    except Exception:
        pass


# Line 263-269: try_exit function
def try_exit():
    global is_running
    # line 265
    with run_lock:
        is_running = False
    # line 267
    try:
        root.quit()
    except Exception:
        pass
    # line 269
    try:
        root.destroy()
    except Exception:
        pass
    import sys
    sys.exit(0)


# Line 271-272: Button commands
close_btn.configure(command=lambda: root.after(0, try_exit))
exit_btn.configure(command=lambda: root.after(0, try_exit))

# Line 274: Refresh label
refresh_start_key_label()


# Line 280-293: update_progress_loop function
def update_progress_loop():
    # line 281
    with run_lock:
        running = is_running
        start_t = macro_start_time
    # line 285
    if not running or start_t is None:
        # line 286
        progress_var.set(0.0)
        # line 287
        return
    # line 289
    elapsed = time.perf_counter() - start_t
    # line 290
    pct = max(0.0, min(100.0, elapsed / TOTAL_DURATION * 100.0))
    # line 291
    progress_var.set(pct)
    # line 293
    root.after(20, update_progress_loop)


# Line 299-305: wait_until function
def wait_until(target_time: float):
    # line 300
    while True:
        # line 301
        now = time.perf_counter()
        # line 302
        if now >= target_time:
            # line 303
            return
        # line 304
        remaining = target_time - now
        # line 305
        time.sleep(0.005 if remaining > 0.01 else 0.001)


# Line 307-310: tap_key function
def tap_key(key_char: str, dwell: float = 0.008):
    # line 308
    keyboard.press(key_char)
    # line 309
    time.sleep(dwell)
    # line 310
    keyboard.release(key_char)


# Line 317-371: run_macro_once function
def run_macro_once():
    # line 319
    phase1_start = time.perf_counter()
    
    # line 321
    mouse.press(Button.left)
    # line 322
    wait_until(phase1_start + 0.9)
    # line 323
    mouse.release(Button.left)
    
    # line 325
    wait_until(phase1_start + 0.9 + 0.05)
    
    # line 327
    keyboard.press('[')
    # line 328
    wait_until(time.perf_counter() + 0.06)
    # line 329
    keyboard.release('[')
    # line 330
    time.sleep(0.008)
    
    # line 332
    wait_until(time.perf_counter() + 1.0)
    
    # line 335
    p2_start = time.perf_counter()
    # line 336
    p2_end = p2_start + PHASE2_DURATION
    # line 337
    bracket_time = p2_start + BRACKET_OFFSET
    
    # line 339
    bracket_done = False
    # line 340
    next_click_time = p2_start
    
    # line 342
    while True:
        # line 343
        now = time.perf_counter()
        # line 344
        if now >= p2_end:
            # line 345
            return
        
        # line 347
        if not bracket_done and now >= bracket_time:
            # line 348
            tap_key('[', dwell=0.004)
            # line 349
            tap_key('[', dwell=0.004)
            # line 350
            tap_key('[', dwell=0.004)
            # line 351
            tap_key('[', dwell=0.004)
            # line 352
            bracket_done = True
        
        # line 354
        if now >= next_click_time:
            # line 355
            if now - next_click_time > CLICK_PERIOD * 2:
                # line 356
                next_click_time = now
            
            # line 358
            mouse.press(Button.left)
            # line 359
            wait_until(time.perf_counter() + HOLD_TIME)
            # line 360
            mouse.release(Button.left)
            
            # line 362
            next_click_time += CLICK_PERIOD
        else:
            # line 365
            next_event = min(next_click_time, p2_end)
            # line 366
            if not bracket_done:
                # line 367
                next_event = min(next_event, bracket_time)
            
            # line 369
            remaining = next_event - time.perf_counter()
            # line 370
            if remaining > 0:
                # line 371
                time.sleep(min(0.005, remaining))


# Line 377-398: worker function
def worker():
    global is_running, macro_start_time
    # line 379
    try:
        # line 380
        run_macro_once()
        # line 381
        set_status('Done. Press start key to run again.')
    finally:
        # line 383
        try:
            # line 384
            mouse.release(Button.left)
        except Exception:
            # line 386
            pass
        
        # line 387
        try:
            # line 388
            keyboard.release('[')
        except Exception:
            # line 390
            pass
        
        # line 392
        with run_lock:
            # line 393
            is_running = False
            # line 394
            macro_start_time = None
        
        # line 396
        root.after(0, lambda: set_status('Done. Press start key to run again.'))
        # line 397
        root.after(400, lambda: progress_var.set(0.0))
        # line 398
        root.after(0, lambda: set_controls_enabled(True))


# Line 401-419: start_macro function
def start_macro():
    global is_running, run_thread, macro_start_time
    # line 403
    with run_lock:
        # line 404
        if is_running:
            # line 406
            return
        # line 407
        is_running = True
        # line 408
        macro_start_time = time.perf_counter()
    
    # line 410
    set_controls_enabled(False)
    # line 411
    progress_var.set(0.0)
    
    # line 414
    set_status('IN PROGRESS')
    
    # line 416
    root.after(0, update_progress_loop)
    
    # line 418
    run_thread = threading.Thread(target=worker, daemon=True)
    # line 419
    run_thread.start()


# Line 422-429: begin_capture_start_key function
def begin_capture_start_key():
    global capture_start_key
    # line 424
    with run_lock:
        # line 425
        if is_running:
            # line 427
            return
    # line 428
    capture_start_key = True
    # line 429
    set_status('Press a key to set as START (global).')


# Line 432: Button command
change_key_btn.configure(command=lambda: root.after(0, begin_capture_start_key))


# Line 438-471: on_press function
def on_press(key):
    global start_key, capture_start_key
    
    # line 442
    if keys_equal(key, toggle_ui_key):
        # line 443
        root.after(0, toggle_ui)
        # line 444
        return None
    
    # line 447
    if capture_start_key:
        # line 448
        if keys_equal(key, exit_key) or keys_equal(key, toggle_ui_key):
            # line 449
            set_status('That key is reserved. Pick another.')
            # line 450
            return None
        
        # line 452
        start_key = key
        # line 453
        capture_start_key = False
        # line 454
        refresh_start_key_label()
        # line 455
        set_status('Start key updated.')
        # line 456
        return None
    
    # line 459
    if keys_equal(key, start_key):
        # line 460
        root.after(0, start_macro)
        # line 461
        return None
    
    # line 464
    if keys_equal(key, exit_key):
        # line 465
        with run_lock:
            # line 466
            running = is_running
        # line 467
        if running:
            # line 469
            return None
        # line 470
        root.after(0, try_exit)
        # line 471
        return False
    
    return None


# Line 474-476: Start keyboard listener
listener = Listener(on_press=on_press)
listener.daemon = True
listener.start()

# Line 479-480: Initialize UI state
set_minimized(False)
set_status('Idle (press start key)')

# Line 482: Main loop
root.mainloop()