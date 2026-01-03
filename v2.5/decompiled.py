#!/usr/bin/env python3
"""
Macrov2.py - Exact reconstruction from Python 3.14 bytecode
awesome macro by choco v2
"""

# Line 1-11: Imports
import time                                          # line 1
import threading                                     # line 2
import sys                                           # line 3
import json                                          # line 4
import re                                            # line 5
import urllib.request                                # line 6
import urllib.error                                  # line 7
import tkinter as tk                                 # line 8
from tkinter import ttk                              # line 9
from pynput.mouse import Controller as MouseController, Button  # line 10
from pynput.keyboard import Controller as KeyboardController, Key, KeyCode, Listener  # line 11

# Line 19: Screen constants
BASE_W, BASE_H = 1920, 1080

# Line 20-21: Platform detection
IS_WINDOWS = sys.platform.startswith('win')
ENABLE_DPI_AWARE = False

# Line 23-34: DPI awareness setup
if IS_WINDOWS and ENABLE_DPI_AWARE:
    # line 24
    try:
        # line 25
        import ctypes
        # line 26
        try:
            # line 27
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            # line 29
            try:
                # line 30
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                # line 32
                pass
    except Exception:
        # line 34
        pass


# Line 36-53: _get_screen_size function
def _get_screen_size():
    # line 37
    if IS_WINDOWS and ENABLE_DPI_AWARE:
        # line 38
        try:
            # line 39
            import ctypes
            # line 40
            w = int(ctypes.windll.user32.GetSystemMetrics(0))
            # line 41
            h = int(ctypes.windll.user32.GetSystemMetrics(1))
            # line 42
            return w, h
        except Exception:
            # line 44
            pass
    # line 46
    try:
        # line 47
        _r = tk.Tk()
        # line 48
        _r.withdraw()
        # line 49
        w = _r.winfo_screenwidth()
        h = _r.winfo_screenheight()
        # line 50
        _r.destroy()
        # line 51
        return w, h
    except Exception:
        # line 53
        return BASE_W, BASE_H


# Line 55: Get screen size
SCREEN_W, SCREEN_H = _get_screen_size()

# Line 57-59: Scale factors
SCALE_X = SCREEN_W / float(BASE_W)
SCALE_Y = SCREEN_H / float(BASE_H)
SCALE_MIN = min(SCALE_X, SCALE_Y)


# Line 61-62: sx function
def sx(px: float) -> int:
    return int(round(px * SCALE_X))


# Line 64-65: sy function
def sy(px: float) -> int:
    return int(round(px * SCALE_Y))


# Line 67-68: smin function
def smin(px: float) -> int:
    return int(round(px * SCALE_MIN))


# Line 77-82: Key gate config
KEY_GATE_ENABLED = False
KEYS_URL = 'https://www.fragbin.com/r/NU8L2'

KEY_FETCH_TIMEOUT = 8.0
KEYS_CACHE_SECONDS = 15.0
KEY_ENTRY_GEOMETRY = '350x100+60+60'

# Line 84-86: Threading primitives
unlocked_event = threading.Event()
_keys_cache_lock = threading.Lock()
_keys_cache = {'ts': 0.0, 'keys': set()}


# Line 88-106: _resolve_keys_url function
def _resolve_keys_url(url: str) -> str:
    # line 90
    u = (url or '').strip()
    # line 91
    m = re.match(r'^https?://gist\.github\.com/[^/]+/([0-9a-fA-F]+)(?:/.*)?$', u)
    # line 92
    if not m:
        # line 93
        return u
    # line 95
    gist_id = m.group(1)
    # line 96
    api_url = f'https://api.github.com/gists/{gist_id}'
    # line 97
    req = urllib.request.Request(api_url, headers={'User-Agent': 'choco-macro'})
    # line 98
    with urllib.request.urlopen(req, timeout=KEY_FETCH_TIMEOUT) as resp:
        # line 99
        data = json.loads((resp.read().decode('utf-8', errors='ignore') or '{}'))
    # line 100
    files = data.get('files') or {}
    # line 102
    for _, info in files.items():
        # line 103
        raw_url = (info or {}).get('raw_url')
        # line 104
        if not raw_url:
            continue
        # line 105
        return str(raw_url)
    # line 106
    return u


# Line 108-126: _fetch_keys_raw function
def _fetch_keys_raw() -> set:
    # line 110
    resolved = _resolve_keys_url(KEYS_URL)
    # line 111
    if not resolved:
        # line 112
        return set()
    # line 114
    req = urllib.request.Request(resolved, headers={'User-Agent': 'choco-macro'})
    # line 115
    with urllib.request.urlopen(req, timeout=KEY_FETCH_TIMEOUT) as resp:
        # line 116
        txt = resp.read().decode('utf-8', errors='ignore')
    # line 118
    keys = set()
    # line 119
    for line in txt.splitlines():
        # line 120
        k = line.strip()
        # line 121
        if not k:
            # line 122
            continue
        # line 123
        if k.startswith('#') or k.startswith('//'):
            # line 124
            continue
        # line 125
        keys.add(k)
    # line 126
    return keys


# Line 128-137: fetch_keys_cached function
def fetch_keys_cached() -> set:
    # line 130
    with _keys_cache_lock:
        # line 131
        now = time.time()
        # line 132
        if now - _keys_cache['ts'] < KEYS_CACHE_SECONDS:
            # line 133
            return set(_keys_cache['keys'])
    # line 134
    keys = _fetch_keys_raw()
    # line 134
    with _keys_cache_lock:
        # line 135
        _keys_cache['ts'] = time.time()
        # line 136
        _keys_cache['keys'] = set(keys)
    # line 137
    return set(keys)


# Line 139-147: validate_key function
def validate_key(key: str) -> bool:
    # line 140
    k = (key or '').strip()
    # line 141
    if not k:
        # line 142
        return False
    # line 143
    try:
        # line 144
        keys = fetch_keys_cached()
    except Exception:
        # line 146
        return False
    # line 147
    return k in keys


# Line 149-152: clamp_xy function
def clamp_xy(x: int, y: int):
    # line 150
    x = max(0, min(SCREEN_W - 1, int(x)))
    # line 151
    y = max(0, min(SCREEN_H - 1, int(y)))
    # line 152
    return x, y


# Line 157: SendInput availability
SENDINPUT_AVAILABLE = False

# Line 159-244: Windows SendInput setup
if IS_WINDOWS:
    # line 160
    try:
        # line 161
        import ctypes
        # line 162
        from ctypes import wintypes

        # line 164
        if not hasattr(wintypes, 'ULONG_PTR'):
            # line 165
            wintypes.ULONG_PTR = ctypes.c_size_t

        # line 167
        _user32 = ctypes.WinDLL('user32', use_last_error=True)

        # line 169-178
        INPUT_MOUSE = 0
        INPUT_KEYBOARD = 1
        MOUSEEVENTF_LEFTDOWN = 2
        MOUSEEVENTF_LEFTUP = 4
        KEYEVENTF_SCANCODE = 8
        KEYEVENTF_KEYUP = 2
        VK_LBUTTON = 1

        # line 180-188: MOUSEINPUT structure
        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [
                ('dx', wintypes.LONG),
                ('dy', wintypes.LONG),
                ('mouseData', wintypes.DWORD),
                ('dwFlags', wintypes.DWORD),
                ('time', wintypes.DWORD),
                ('dwExtraInfo', wintypes.ULONG_PTR),
            ]

        # line 190-197: KEYBDINPUT structure
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ('wVk', wintypes.WORD),
                ('wScan', wintypes.WORD),
                ('dwFlags', wintypes.DWORD),
                ('time', wintypes.DWORD),
                ('dwExtraInfo', wintypes.ULONG_PTR),
            ]

        # line 199-200: INPUT_UNION
        class INPUT_UNION(ctypes.Union):
            _fields_ = [('mi', MOUSEINPUT), ('ki', KEYBDINPUT)]

        # line 202-203: INPUT structure
        class INPUT(ctypes.Structure):
            _fields_ = [('type', wintypes.DWORD), ('union', INPUT_UNION)]

        # line 205-206: _send_input function
        def _send_input(*inputs):
            n = len(inputs)
            arr = (INPUT * n)(*inputs)
            _user32.SendInput(n, arr, ctypes.sizeof(INPUT))

        # line 208-210: _send_mouse function
        def _send_mouse(flags: int):
            mi = MOUSEINPUT(0, 0, 0, flags, 0, 0)
            inp = INPUT(INPUT_MOUSE, INPUT_UNION(mi=mi))
            _send_input(inp)

        # line 212-213: mouse_left_down_si
        def mouse_left_down_si():
            _send_mouse(MOUSEEVENTF_LEFTDOWN)

        # line 215-216: mouse_left_up_si
        def mouse_left_up_si():
            _send_mouse(MOUSEEVENTF_LEFTUP)

        # line 223-224: lbutton_is_down
        def lbutton_is_down() -> bool:
            return bool(_user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)

        # line 226-227: set_cursor_pos
        def set_cursor_pos(x: int, y: int):
            _user32.SetCursorPos(int(x), int(y))

        # line 230-231: map_vk_to_sc
        def map_vk_to_sc(vk: int) -> int:
            return _user32.MapVirtualKeyW(vk, 0)

        # line 233-235: key_down_sc
        def key_down_sc(sc: int):
            ki = KEYBDINPUT(0, sc, KEYEVENTF_SCANCODE, 0, 0)
            inp = INPUT(INPUT_KEYBOARD, INPUT_UNION(ki=ki))
            _send_input(inp)

        # line 237-239: key_up_sc
        def key_up_sc(sc: int):
            ki = KEYBDINPUT(0, sc, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, 0)
            inp = INPUT(INPUT_KEYBOARD, INPUT_UNION(ki=ki))
            _send_input(inp)

        # line 241
        SENDINPUT_AVAILABLE = True
    except Exception:
        # line 243
        SENDINPUT_AVAILABLE = False

# Line 245-252: Fallback stubs
if not SENDINPUT_AVAILABLE:
    # line 246
    def mouse_left_down_si():
        pass
    # line 247
    def mouse_left_up_si():
        pass
    # line 248
    def lbutton_is_down() -> bool:
        return False
    # line 249
    def set_cursor_pos(x: int, y: int):
        pass
    # line 250
    def map_vk_to_sc(vk: int) -> int:
        return 0
    # line 251
    def key_down_sc(sc: int):
        pass
    # line 252
    def key_up_sc(sc: int):
        pass

# Line 257-258: Mouse and keyboard controllers
mouse = MouseController()
keyboard = KeyboardController()


# Line 261-265: mouse_left_down
def mouse_left_down():
    # line 262
    if SENDINPUT_AVAILABLE:
        # line 263
        mouse_left_down_si()
    else:
        # line 265
        mouse.press(Button.left)


# Line 267-271: mouse_left_up
def mouse_left_up():
    # line 268
    if SENDINPUT_AVAILABLE:
        # line 269
        mouse_left_up_si()
    else:
        # line 271
        mouse.release(Button.left)


# Line 273-289: mouse_safe_release
def mouse_safe_release(max_wait=0.45):
    # line 275
    for _ in range(6):
        # line 276
        try:
            # line 277
            mouse_left_up()
        except Exception:
            # line 279
            pass
        # line 280
        time.sleep(0.004)
    # line 283
    deadline = time.perf_counter() + max_wait
    # line 284
    while SENDINPUT_AVAILABLE and lbutton_is_down() and time.perf_counter() < deadline:
        # line 285
        try:
            # line 286
            mouse_left_up_si()
        except Exception:
            # line 288
            pass
        # line 289
        time.sleep(0.006)


# Line 291-296: cursor_set
def cursor_set(x: int, y: int):
    # line 292
    x, y = clamp_xy(x, y)
    # line 293
    if SENDINPUT_AVAILABLE:
        # line 294
        set_cursor_pos(x, y)
    else:
        # line 296
        mouse.position = (x, y)


# Line 301-305: Global state
run_thread = None
run_lock = threading.Lock()
is_running = False
macro_start_time = None
macro_total_duration = 1.0

# Line 310-314: Key bindings
exit_key = Key.f12
toggle_ui_key = Key.end
start_key = Key.f6
capture_start_key = False
capture_clumsy_key = False

# Line 319-327: Throw macro timing constants
CLICK_PERIOD = 0.0437
HOLD_TIME = 0.03
PHASE2_DURATION = 1.85
BRACKET_OFFSET = 1.61

PHASE1_TOTAL = 2.01
THROW_TOTAL_DURATION = PHASE1_TOTAL + PHASE2_DURATION

# Line 327-334: Key codes
BRACKET_VK = 219
BRACKET_KEY = KeyCode.from_vk(BRACKET_VK)

E_KEY = KeyCode.from_char('e')
Q_KEY = KeyCode.from_char('q')
THROW_REPEAT_E_DWELL = 0.03
THROW_REPEAT_GAP = 0.05
THROW_REPEAT_RESTART_DELAY = 0.5

# Line 336-345: More timing constants
THROW_AFTER_E_BEFORE_TAB_DELAY = 0.05
THROW_AFTER_TAB_BEFORE_AIM_DELAY = 0.05
THROW_AIM_ANGLE_DEG = 70
THROW_AIM_UP_DISTANCE = smin(250)
THROW_AIM_HORIZONTAL_DIR = 1
THROW_TAB_DWELL = 0.03

THROW_DOUBLECLICK_HOLD = 0.022
THROW_DOUBLECLICK_GAP = 0.055

# Line 347-348: Threading events
throw_repeat_event = threading.Event()
stop_after_cycle_event = threading.Event()


# Line 350-379: tap_e function
def tap_e(dwell=THROW_REPEAT_E_DWELL):
    # line 352
    if SENDINPUT_AVAILABLE:
        # line 353
        try:
            # line 354
            with KEY_IO_LOCK:
                # line 355
                try:
                    # line 356
                    key_up_sc(KEY_SC_E)
                except Exception:
                    # line 358
                    pass
                # line 359
                try:
                    # line 360
                    key_down_sc(KEY_SC_E)
                except Exception:
                    # line 362
                    pass
            # line 363
            time.sleep(max(0.0, float(dwell)))
            # line 364
            with KEY_IO_LOCK:
                # line 365
                try:
                    # line 366
                    key_up_sc(KEY_SC_E)
                except Exception:
                    # line 368
                    pass
        except Exception:
            # line 370
            with KEY_IO_LOCK:
                # line 371
                try:
                    # line 372
                    key_up_sc(KEY_SC_E)
                except Exception:
                    # line 374
                    pass
    else:
        # line 376
        try:
            # line 377
            keyboard.press(E_KEY)
            time.sleep(max(0.0, dwell))
            keyboard.release(E_KEY)
        except Exception:
            # line 379
            try:
                keyboard.release(E_KEY)
            except Exception:
                pass


# Line 381-391: tap_q function
def tap_q(dwell: float = 0.03):
    # line 383
    try:
        # line 384
        keyboard.press(Q_KEY)
        # line 385
        time.sleep(max(0.0, dwell))
        # line 386
        keyboard.release(Q_KEY)
    except Exception:
        # line 388
        try:
            # line 389
            keyboard.release(Q_KEY)
        except Exception:
            # line 391
            pass


# Line 393-422: tap_tab function
def tap_tab(dwell: float = THROW_TAB_DWELL):
    # line 395
    if SENDINPUT_AVAILABLE:
        # line 396
        try:
            # line 397
            with KEY_IO_LOCK:
                # line 398
                try:
                    key_up_sc(KEY_SC_TAB)
                except Exception:
                    pass
                # line 400
                try:
                    key_down_sc(KEY_SC_TAB)
                except Exception:
                    pass
            # line 401
            time.sleep(max(0.0, float(dwell)))
            # line 402
            with KEY_IO_LOCK:
                # line 403
                try:
                    key_up_sc(KEY_SC_TAB)
                except Exception:
                    pass
        except Exception:
            # line 409
            with KEY_IO_LOCK:
                # line 410
                try:
                    key_up_sc(KEY_SC_TAB)
                except Exception:
                    pass
    else:
        # line 415
        try:
            # line 416
            keyboard.press(Key.tab)
            # line 417
            time.sleep(max(0.0, float(dwell)))
            # line 418
            keyboard.release(Key.tab)
        except Exception:
            # line 420
            try:
                keyboard.release(Key.tab)
            except Exception:
                # line 422
                pass


# Line 424-442: move_mouse_up_angle function
def move_mouse_up_angle(angle_deg=THROW_AIM_ANGLE_DEG, h_dir=THROW_AIM_HORIZONTAL_DIR, steps=30):
    # line 426
    import math
    # line 427
    rad = math.radians(angle_deg)
    # line 428
    total_dy = -THROW_AIM_UP_DISTANCE
    # line 429
    total_dx = int(abs(total_dy) * math.tan(rad)) * h_dir
    # line 431
    dx_step = total_dx / steps
    dy_step = total_dy / steps
    # line 433
    for _ in range(steps):
        # line 434
        try:
            # line 435
            mouse.move(dx_step, dy_step)
        except Exception:
            # line 437
            pass
        # line 438
        time.sleep(0.001)


# Line 444-480: double_click_left function
def double_click_left(hold: float = THROW_DOUBLECLICK_HOLD, gap: float = THROW_DOUBLECLICK_GAP):
    # line 446
    try:
        # line 447
        mouse_left_down()
        # line 448
        time.sleep(hold)
        # line 449
        mouse_left_up()
    except Exception:
        # line 451
        try:
            mouse_left_up()
        except Exception:
            pass
    # line 455
    time.sleep(gap)
    # line 457
    try:
        # line 458
        mouse_left_down()
        # line 459
        time.sleep(hold)
        # line 460
        mouse_left_up()
    except Exception:
        # line 462
        try:
            mouse_left_up()
        except Exception:
            pass


# Line 482-538: shift_alt_click_once function
def shift_alt_click_once(hold: float = 0.018, post: float = 0.006):
    # line 484
    try:
        # line 485
        keyboard.press(Key.shift)
        # line 486
        keyboard.press(Key.alt)
        # line 487
        time.sleep(0.002)
        # line 489
        try:
            # line 490
            mouse_left_down()
            # line 491
            time.sleep(hold)
            # line 492
            mouse_left_up()
        except Exception:
            # line 494
            try:
                mouse_left_up()
            except Exception:
                pass
        # line 498
        time.sleep(0.002)
        # line 500
        try:
            keyboard.release(Key.alt)
        except Exception:
            pass
        # line 504
        try:
            keyboard.release(Key.shift)
        except Exception:
            pass
    except Exception:
        # line 509
        try:
            keyboard.release(Key.alt)
        except Exception:
            pass
        try:
            keyboard.release(Key.shift)
        except Exception:
            pass
    # line 518
    if post > 0:
        time.sleep(post)


# Line 540-546: wait_until function
def wait_until(target_time: float):
    # line 542
    while True:
        # line 543
        now = time.perf_counter()
        remain = target_time - now
        # line 544
        if remain <= 0:
            return
        # line 545
        if remain > 0.002:
            time.sleep(remain * 0.5)


# Line 548-554: tap_bracket function
def tap_bracket(count=1, dwell=0.006, gap=0.001):
    # line 549
    for i in range(count):
        # line 550
        keyboard.press(BRACKET_KEY)
        # line 551
        time.sleep(dwell)
        # line 552
        keyboard.release(BRACKET_KEY)
        # line 553
        if i != count - 1:
            # line 554
            time.sleep(gap)


# Line 556-609: run_throw_macro_once function
def run_throw_macro_once():
    # line 557
    phase1_start = time.perf_counter()
    # line 559
    mouse_left_down()
    # line 560
    wait_until(phase1_start + 0.9)
    # line 561
    mouse_left_up()
    # line 563
    wait_until(phase1_start + 0.9 + 0.05)
    # line 565
    keyboard.press(BRACKET_KEY)
    # line 566
    wait_until(time.perf_counter() + 0.06)
    # line 567
    keyboard.release(BRACKET_KEY)
    # line 568
    time.sleep(0.008)
    # line 570
    wait_until(time.perf_counter() + 1.0)
    # line 572
    p2_start = time.perf_counter()
    # line 573
    p2_end = p2_start + PHASE2_DURATION
    # line 574
    bracket_time = p2_start + BRACKET_OFFSET
    # line 576
    bracket_done = False
    # line 577
    next_click_time = p2_start
    # line 579
    while True:
        # line 580
        now = time.perf_counter()
        # line 582
        if not bracket_done and now >= bracket_time:
            # line 583
            tap_bracket(count=4, dwell=0.006, gap=0.001)
            # line 584
            bracket_done = True
        # line 586
        if now >= p2_end:
            # line 587
            return
        # line 589
        if now >= next_click_time:
            # line 590
            if now - next_click_time > CLICK_PERIOD * 2:
                # line 591
                next_click_time = now
            # line 593
            mouse_left_down()
            # line 594
            wait_until(time.perf_counter() + HOLD_TIME)
            # line 595
            mouse_left_up()
            # line 597
            next_click_time += CLICK_PERIOD
        else:
            # line 600
            next_event = min(next_click_time, p2_end)
            # line 601
            if not bracket_done:
                # line 602
                next_event = min(next_event, bracket_time)
            # line 604
            sleep_time = next_event - now - 0.0005
            # line 605
            if sleep_time > 0:
                # line 606
                time.sleep(sleep_time)


# Line 611-636: Key macro configuration
KEY_START_SETTLE_DELAY = 0.03
KEY_PRE_DRAG_DELAY = 0.06
KEY_TAB_DELAY_AFTER_DRAG = 0.3
KEY_STOP_DRAG_DELAY = 0.05
KEY_PRE_SPAM_DELAY = 0.03

KEY_BRACKET_E_START_DELAY = 0.0
KEY_POST_TAB_TO_E_SPAM_DELAY = 0.004
KEY_E_LEAD_BEFORE_BRACKET = 0.01

KEY_DRAG_LEFT_PIXELS = sx(1300)
KEY_DRAG_DY = 0
KEY_DRAG_TIME = 0.5

KEY_BRACKET_DWELL = 0.04
KEY_TAB_DWELL = 0.02
KEY_E_DWELL = 0.0389

KEY_SPAM_DURATION = 2.25
KEY_E_PERIOD = 0.0219

KEY_DRAG_END_LEFTCLICK_SPAM = True
KEY_DRAG_END_SPAM_LEAD = 0.005
KEY_DRAG_END_SPAM_DURATION = 0.05
KEY_DRAG_END_SPAM_PERIOD = 0.01
KEY_DRAG_END_SPAM_HOLD = 0.001

KEY_VK_BRACKET = BRACKET_VK

# Line 640-651: KEY_TOTAL_DURATION calculation
KEY_TOTAL_DURATION = (
    KEY_START_SETTLE_DELAY +
    KEY_BRACKET_DWELL +
    KEY_PRE_DRAG_DELAY +
    KEY_DRAG_TIME +
    KEY_TAB_DELAY_AFTER_DRAG +
    KEY_TAB_DWELL +
    KEY_POST_TAB_TO_E_SPAM_DELAY +
    KEY_PRE_SPAM_DELAY +
    KEY_BRACKET_E_START_DELAY +
    KEY_SPAM_DURATION +
    0.25
)

# Line 654-662: Key IO primitives
KEY_IO_LOCK = threading.Lock()
KEY_PAUSE_E = threading.Event()

KEY_SC_TAB = 15
KEY_SC_E = 18
KEY_SC_BRACKET = map_vk_to_sc(KEY_VK_BRACKET) if SENDINPUT_AVAILABLE else 26
if not KEY_SC_BRACKET:
    KEY_SC_BRACKET = 26


# Line 671-699: _vk_from_pynput_key function
def _vk_from_pynput_key(k):
    # line 673
    if isinstance(k, Key):
        # line 674
        if hasattr(k, 'value') and hasattr(k.value, 'vk'):
            # line 675
            return k.value.vk
        # line 677
        return None
    # line 679
    if isinstance(k, KeyCode):
        # line 680
        if k.vk:
            # line 681
            return k.vk
        # line 683
        if k.char:
            # line 684
            c = k.char.lower()
            # line 685
            if len(c) == 1 and c.isalpha():
                # line 686
                return ord(c.upper())
        # line 688
        return None
    # line 690
    if hasattr(k, 'vk'):
        # line 691
        return k.vk
    # line 693
    if hasattr(k, 'value') and hasattr(k.value, 'vk'):
        # line 694
        return k.value.vk
    # line 696
    return None


# Line 701-727: set_clumsy_key function
def set_clumsy_key(new_key):
    global KEY_VK_BRACKET, KEY_SC_BRACKET, BRACKET_VK, BRACKET_KEY
    # line 703
    vk = _vk_from_pynput_key(new_key)
    # line 704
    if vk:
        # line 705
        KEY_VK_BRACKET = vk
        # line 706
        BRACKET_VK = vk
        # line 707
        BRACKET_KEY = KeyCode.from_vk(vk)
        # line 709
        if SENDINPUT_AVAILABLE:
            # line 710
            try:
                # line 711
                KEY_SC_BRACKET = map_vk_to_sc(vk)
            except Exception:
                # line 713
                KEY_SC_BRACKET = 26
            # line 715
            if not KEY_SC_BRACKET:
                KEY_SC_BRACKET = 26
    else:
        # line 719
        try:
            # line 720
            BRACKET_KEY = new_key
        except Exception:
            # line 722
            pass


# Line 729-730: Scancode constants
KEY_SC_SHIFT = 42
KEY_SC_ALT = 56


# Line 732-737: key_hard_up function
def key_hard_up(sc: int):
    # line 733
    with KEY_IO_LOCK:
        # line 734
        try:
            # line 735
            key_up_sc(sc)
        except Exception:
            # line 737
            pass


# Line 739-750: key_tap_sc function
def key_tap_sc(sc: int, dwell: float = 0.002, post: float = 0.0):
    # line 740
    with KEY_IO_LOCK:
        # line 741
        try:
            # line 742
            key_up_sc(sc)
        except Exception:
            pass
        # line 745
        try:
            key_down_sc(sc)
        except Exception:
            pass
    # line 746
    time.sleep(dwell)
    # line 747
    with KEY_IO_LOCK:
        # line 748
        key_up_sc(sc)
    # line 749
    if post > 0:
        # line 750
        time.sleep(post)


# Line 752-762: key_safe_mouse_release function
def key_safe_mouse_release(max_wait=0.45):
    # line 753
    mouse_safe_release(max_wait=max_wait)
    # line 755
    try:
        # line 756
        x, y = mouse.position
        # line 757
        cursor_set(x + 1, y)
        # line 758
        time.sleep(0.003)
        # line 759
        cursor_set(x, y)
        # line 760
        time.sleep(0.003)
    except Exception:
        # line 762
        pass


# Line 764-787: key_smooth_move_abs_with_hook function
def key_smooth_move_abs_with_hook(x1, y1, x2, y2, duration, hook_at_seconds_before_end=None, hook_fn=None):
    # line 765
    if duration <= 0:
        # line 766
        cursor_set(x2, y2)
        # line 767
        return
    # line 769
    steps = max(60, int(duration / 0.004))
    # line 770
    t0 = time.perf_counter()
    # line 771
    hook_fired = False
    # line 773
    for i in range(1, steps + 1):
        # line 774
        a = i / steps
        # line 775
        x = int(x1 + (x2 - x1) * a)
        # line 776
        y = int(y1 + (y2 - y1) * a)
        # line 777
        cursor_set(x, y)
        # line 779
        elapsed = time.perf_counter() - t0
        # line 780
        if not hook_fired and hook_fn and hook_at_seconds_before_end is not None:
            # line 781
            if elapsed >= max(0.0, duration - hook_at_seconds_before_end):
                # line 782
                hook_fired = True
                # line 783
                hook_fn()
        # line 785
        target = t0 + duration * a
        # line 786
        while time.perf_counter() < target:
            # line 787
            time.sleep(0.001)


# Line 789-809: key_spam_left_clicks function
def key_spam_left_clicks(duration: float, period: float, hold: float):
    # line 791
    end_time = time.perf_counter() + duration
    # line 792
    while time.perf_counter() < end_time:
        # line 793
        try:
            # line 794
            mouse_left_down()
            # line 795
            time.sleep(hold)
            # line 796
            mouse_left_up()
        except Exception:
            # line 798
            try:
                mouse_left_up()
            except Exception:
                pass
        # line 802
        remaining = end_time - time.perf_counter()
        # line 803
        if remaining > 0:
            # line 804
            time.sleep(min(period - hold, remaining))


# Line 811: Threading event
_key_drag_end_spam_started = threading.Event()


# Line 813-823: key_maybe_start_drag_end_spam function
def key_maybe_start_drag_end_spam():
    # line 814
    if KEY_DRAG_END_LEFTCLICK_SPAM and not _key_drag_end_spam_started.is_set():
        # line 815
        _key_drag_end_spam_started.set()
        # line 816
        t = threading.Thread(
            target=key_spam_left_clicks,
            args=(KEY_DRAG_END_SPAM_DURATION, KEY_DRAG_END_SPAM_PERIOD, KEY_DRAG_END_SPAM_HOLD),
            daemon=True
        )
        # line 822
        t.start()


# Line 825-847: _key_delayed_bracket_tap function
def _key_delayed_bracket_tap(delay: float):
    # line 826
    if delay > 0:
        # line 827
        time.sleep(delay)
    # line 829
    with KEY_IO_LOCK:
        # line 830
        try:
            # line 831
            key_up_sc(KEY_SC_E)
        except Exception:
            pass
        # line 835
        try:
            # line 836
            key_down_sc(KEY_SC_BRACKET)
        except Exception:
            pass
    # line 840
    time.sleep(KEY_BRACKET_DWELL)
    # line 841
    with KEY_IO_LOCK:
        # line 842
        try:
            # line 843
            key_up_sc(KEY_SC_BRACKET)
        except Exception:
            pass


# Line 849-893: key_spam_e_then_bracket function
def key_spam_e_then_bracket(spam_duration: float):
    # line 851
    end_time = time.perf_counter() + spam_duration
    # line 852
    bracket_time = time.perf_counter() + KEY_E_LEAD_BEFORE_BRACKET
    # line 853
    bracket_scheduled = False
    # line 855
    next_e = time.perf_counter()
    # line 857
    while True:
        # line 858
        now = time.perf_counter()
        # line 859
        if now >= end_time:
            # line 860
            break
        # line 862
        if not bracket_scheduled and now >= bracket_time:
            # line 863
            t = threading.Thread(
                target=_key_delayed_bracket_tap,
                args=(0.0,),
                daemon=True
            )
            # line 870
            t.start()
            # line 871
            bracket_scheduled = True
        # line 873
        if now >= next_e:
            # line 874
            with KEY_IO_LOCK:
                # line 875
                try:
                    key_up_sc(KEY_SC_E)
                except Exception:
                    pass
                # line 879
                try:
                    key_down_sc(KEY_SC_E)
                except Exception:
                    pass
            # line 883
            time.sleep(KEY_E_DWELL)
            # line 884
            with KEY_IO_LOCK:
                # line 885
                try:
                    key_up_sc(KEY_SC_E)
                except Exception:
                    pass
            # line 889
            next_e += KEY_E_PERIOD
        else:
            # line 891
            time.sleep(0.001)
    # line 893
    with KEY_IO_LOCK:
        try:
            key_up_sc(KEY_SC_E)
        except Exception:
            pass
        try:
            key_up_sc(KEY_SC_BRACKET)
        except Exception:
            pass


# Line 895-930: run_key_macro_once function
def run_key_macro_once():
    # line 897
    _key_drag_end_spam_started.clear()
    # line 899
    time.sleep(max(0.0, KEY_START_SETTLE_DELAY))
    # line 901
    key_tap_sc(KEY_SC_BRACKET, KEY_BRACKET_DWELL, post=0.002)
    # line 902
    time.sleep(max(0.0, KEY_PRE_DRAG_DELAY))
    # line 904
    x1, y1 = mouse.position
    # line 905
    x2 = x1 - abs(KEY_DRAG_LEFT_PIXELS)
    y2 = y1 + KEY_DRAG_DY
    # line 907
    mouse_left_down()
    # line 909-912
    key_smooth_move_abs_with_hook(
        x1, y1, x2, y2, KEY_DRAG_TIME,
        hook_at_seconds_before_end=KEY_DRAG_END_SPAM_LEAD,
        hook_fn=key_maybe_start_drag_end_spam
    )
    # line 915
    time.sleep(max(0.0, KEY_TAB_DELAY_AFTER_DRAG))
    # line 916
    key_tap_sc(KEY_SC_TAB, KEY_TAB_DWELL, post=0.002)
    # line 918
    key_hard_up(KEY_SC_TAB)
    # line 919
    mouse_safe_release(max_wait=0.08)
    # line 921
    time.sleep(max(0.0, KEY_PRE_SPAM_DELAY))
    # line 922
    time.sleep(max(0.0, KEY_POST_TAB_TO_E_SPAM_DELAY))
    # line 923
    time.sleep(max(0.0, KEY_BRACKET_E_START_DELAY))
    # line 925
    key_spam_e_then_bracket(KEY_SPAM_DURATION)
    # line 927
    time.sleep(max(0.0, KEY_STOP_DRAG_DELAY))
    # line 928
    key_safe_mouse_release(max_wait=0.6)


# Line 933-940: key_signature function
def key_signature(k):
    # line 934
    if isinstance(k, Key):
        # line 935
        return ('Key', k.name)
    # line 936
    if isinstance(k, KeyCode):
        # line 937
        if k.char:
            # line 938
            return ('Char', k.char.lower())
        # line 939
        return ('Vk', k.vk)
    # line 940
    return ('Other', str(k))


# Line 942-943: keys_equal function
def keys_equal(a, b):
    return key_signature(a) == key_signature(b)


# Line 945-952: key_to_label function
def key_to_label(k):
    # line 946
    if isinstance(k, Key):
        # line 947
        return (k.name or str(k)).upper()
    # line 948
    if isinstance(k, KeyCode):
        # line 949
        if k.char:
            # line 950
            return k.char.upper()
        # line 951
        return f'VK_{k.vk}'
    # line 952
    return 'UNKNOWN'


# Line 957-958: UI Constants
UI_W, UI_H = 500, 600
MINI_H = 120

# Line 960-964: Create root window
root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.geometry(f'{UI_W}x{UI_H}+40+40')
root.configure(bg='#0b0b0b')

# Line 966-978: Style setup
style = ttk.Style(root)
try:
    style.theme_use('clam')
except Exception:
    pass

style.configure(
    'Gray.Horizontal.TProgressbar',
    troughcolor='#2a2a2a',
    background='#7a7a7a',
    bordercolor='#2a2a2a',
    lightcolor='#7a7a7a',
    darkcolor='#7a7a7a'
)

# Line 981-985: Button colors
BTN_BG = '#2b2b2b'
BTN_BG_ACTIVE = '#3a3a3a'
BTN_BG_SELECTED = '#404040'
BTN_FG = 'white'
BTN_FG_DISABLED = '#7a7a7a'


# Line 987-997: style_action_button function
def style_action_button(b: tk.Button):
    b.config(
        bg=BTN_BG,
        fg=BTN_FG,
        activebackground=BTN_BG_ACTIVE,
        activeforeground=BTN_FG,
        disabledforeground=BTN_FG_DISABLED,
        bd=0,
        highlightthickness=0,
        relief='flat',
        cursor='hand2'
    )


# Line 1000-1007: Global UI state
ui_visible = True
is_minimized = False

status_var = tk.StringVar(value='Idle (press start key)')
start_key_var = tk.StringVar(value=f'Start key: {key_to_label(start_key)}')
clumsy_key_var = tk.StringVar(value=f'Clumsy key: {key_to_label(BRACKET_KEY)}')
progress_var = tk.DoubleVar(value=0.0)
macro_var = tk.StringVar(value='Macro: Throw')

current_macro = 'Throw'


# Line 1009-1010: set_status function
def set_status(text: str):
    try:
        status_var.set(text)
    except Exception:
        pass


# Line 1012-1014: refresh_start_key_label function
def refresh_start_key_label():
    try:
        start_key_var.set(f'Start key: {key_to_label(start_key)}')
    except Exception:
        pass


# Line 1016-1018: refresh_clumsy_key_label function
def refresh_clumsy_key_label():
    try:
        clumsy_key_var.set(f'Clumsy key: {key_to_label(BRACKET_KEY)}')
    except Exception:
        pass


# Line 1020-1022: set_macro_label function
def set_macro_label():
    try:
        macro_var.set(f'Macro: {current_macro}')
    except Exception:
        pass


# Line 1023-1032: toggle_ui function
def toggle_ui():
    global ui_visible
    # line 1025
    ui_visible = not ui_visible
    # line 1026
    if ui_visible:
        # line 1027
        root.deiconify()
        # line 1028
        root.lift()
    else:
        # line 1030
        root.withdraw()


# Line 1034-1036: apply_size function
def apply_size(h: int):
    root.geometry(f'{UI_W}x{h}')


# Line 1038-1059: set_minimized function
def set_minimized(mini: bool):
    global is_minimized
    # line 1040
    is_minimized = mini
    # line 1041
    if mini:
        # line 1042
        apply_size(MINI_H)
        # line 1043
        for w in expanded_widgets:
            # line 1044
            try:
                w.place_forget()
            except Exception:
                pass
        # line 1048
        try:
            mini_status_lbl.place(x=20, y=58)
        except Exception:
            pass
        # line 1052
        try:
            mini_bar.place(x=20, y=88, width=UI_W - 40, height=8)
        except Exception:
            pass
    else:
        # line 1056
        apply_size(UI_H)
        # line 1057
        try:
            mini_status_lbl.place_forget()
            mini_bar.place_forget()
        except Exception:
            pass
        # line 1059
        for w, opts in expanded_layout:
            try:
                w.place(**opts)
            except Exception:
                pass


# Line 1061-1062: toggle_minimize function
def toggle_minimize():
    set_minimized(not is_minimized)


# Line 1064-1073: Drag support
_drag = {'x': 0, 'y': 0}


def start_drag(event):
    _drag['x'] = event.x
    _drag['y'] = event.y


def do_drag(event):
    x = root.winfo_x() + event.x - _drag['x']
    y = root.winfo_y() + event.y - _drag['y']
    root.geometry(f'+{x}+{y}')


# Line 1075-1084: Header frame
header = tk.Frame(root, bg='#111111', width=UI_W, height=48)
header.place(x=0, y=0)
header.bind('<Button-1>', start_drag)
header.bind('<B1-Motion>', do_drag)

# Line 1080-1084: Title label
title = tk.Label(header, text='awesome macro by choco v2', fg='white', bg='#111111', font=('Segoe UI', 14, 'bold'))
title.place(x=14, y=10)
title.bind('<Button-1>', start_drag)
title.bind('<B1-Motion>', do_drag)

# Line 1086-1091: Minimize button
minimize_btn = tk.Button(
    header, text='—', fg='white', bg='#111111',
    activebackground='#1a1a1a', activeforeground='white',
    bd=0, command=lambda: toggle_minimize()
)
minimize_btn.place(x=UI_W - 84, y=8, width=34, height=32)

# Line 1093-1098: Close button
close_btn = tk.Button(
    header, text='✕', fg='white', bg='#111111',
    activebackground='#1a1a1a', activeforeground='white',
    bd=0
)
close_btn.place(x=UI_W - 42, y=8, width=34, height=32)

# Line 1101-1124: Labels
status_lbl = tk.Label(root, textvariable=status_var, fg='#cfcfcf', bg='#0b0b0b', font=('Segoe UI', 11))
startkey_lbl = tk.Label(root, textvariable=start_key_var, fg='#9a9a9a', bg='#0b0b0b', font=('Segoe UI', 10))
macro_lbl = tk.Label(root, textvariable=macro_var, fg='#9a9a9a', bg='#0b0b0b', font=('Segoe UI', 11))

instructions = tk.Label(
    root,
    text="• Official Version Of V2, Choco's Macro :)\n• If you wish to send donations, Cashapp is $cooljtank\n• Key macro has 100% success with keys. Raider Hatch is 30-80% non guarantee.\n• F6 is default to run. To close press F12. \n• Click 'Change Start Key' or 'Change Clumsy Key' then press a key\n• Toggle UI with END.\n",
    fg='#8a8a8a', bg='#0b0b0b', justify='left', font=('Segoe UI', 10)
)

clumsykey_lbl = tk.Label(root, textvariable=clumsy_key_var, fg='#9a9a9a', bg='#0b0b0b', font=('Segoe UI', 10))

# Line 1126-1128: Buttons
change_key_btn = tk.Button(root, text='Change Start Key', font=('Segoe UI', 10))
change_clumsy_btn = tk.Button(root, text='Change Clumsy Key', font=('Segoe UI', 10))
exit_btn = tk.Button(root, text='EXIT (F12)', font=('Segoe UI', 10))

# Line 1131-1144: Panel
panel = tk.Frame(root, bg='#101010')
panel_title = tk.Label(panel, text='Select macro', fg='#bdbdbd', bg='#101010', font=('Segoe UI', 10, 'bold'))

btn_throw = tk.Button(panel, text='Throw', font=('Segoe UI', 10))
btn_key = tk.Button(panel, text='Key', font=('Segoe UI', 10))
repeat_btn = tk.Button(panel, text='Repeat: OFF', font=('Segoe UI', 9))
stop_btn = tk.Button(panel, text='Stop after cycle', font=('Segoe UI', 9))
panel_hint = tk.Label(panel, text='(Switch which script runs on START)', fg='#6f6f6f', bg='#101010', font=('Segoe UI', 9))

# Line 1147-1155: Mini mode widgets
mini_status_lbl = tk.Label(root, textvariable=status_var, fg='#cfcfcf', bg='#0b0b0b', font=('Segoe UI', 11))
mini_bar = ttk.Progressbar(
    root, orient='horizontal', mode='determinate',
    maximum=100.0, variable=progress_var,
    style='Gray.Horizontal.TProgressbar'
)

# Line 1158-1160: Layout calculations
PANEL_W = UI_W - 40
HALF_PANEL_BTN_W = (PANEL_W - 30) // 2
HALF_MAIN_BTN_W = (PANEL_W - 10) // 2

# Line 1162-1181: Expanded layout definition
expanded_layout = [
    (status_lbl, {'x': 20, 'y': 80}),
    (startkey_lbl, {'x': 20, 'y': 112}),
    (clumsykey_lbl, {'x': 20, 'y': 132}),
    (macro_lbl, {'x': 20, 'y': 156}),
    (instructions, {'x': 20, 'y': 193}),
    (change_key_btn, {'x': 20, 'y': 310, 'width': HALF_MAIN_BTN_W, 'height': 34}),
    (change_clumsy_btn, {'x': 20 + HALF_MAIN_BTN_W + 10, 'y': 310, 'width': HALF_MAIN_BTN_W, 'height': 34}),
    (exit_btn, {'x': 20, 'y': 352, 'width': PANEL_W, 'height': 34}),
    (panel, {'x': 20, 'y': 410, 'width': PANEL_W, 'height': 170}),
]

expanded_widgets = [w for w, _ in expanded_layout]


# Line 1183-1190: set_controls_enabled function
def set_controls_enabled(enabled: bool):
    state = 'normal' if enabled else 'disabled'
    try:
        change_key_btn.config(state=state)
        change_clumsy_btn.config(state=state)
        btn_throw.config(state=state)
        btn_key.config(state=state)
    except Exception:
        pass


# Line 1192-1203: try_exit function
def try_exit():
    global is_running
    # line 1194
    with run_lock:
        is_running = False
    # line 1197
    try:
        root.quit()
    except Exception:
        pass
    # line 1201
    try:
        root.destroy()
    except Exception:
        pass
    # line 1203
    sys.exit(0)


close_btn.configure(command=lambda: root.after(0, try_exit))
exit_btn.configure(command=lambda: root.after(0, try_exit))


# Line 1206-1207: stop_btn_text_default function
def stop_btn_text_default():
    return f'Stop after cycle ({key_to_label(start_key)})'


# Line 1209-1224: request_stop_after_cycle function
def request_stop_after_cycle():
    # line 1210
    with run_lock:
        running = is_running
    # line 1212
    if not running:
        return
    # line 1214
    if current_macro != 'Throw':
        return
    # line 1216
    if not throw_repeat_event.is_set():
        return
    # line 1219
    stop_after_cycle_event.set()
    # line 1220
    set_status('Stopping after this cycle…')
    # line 1221
    try:
        stop_btn.config(text='Stopping…', bg=BTN_BG_SELECTED)
    except Exception:
        pass


# Line 1226-1246: refresh_repeat_button function
def refresh_repeat_button():
    # line 1228
    if current_macro != 'Throw':
        # line 1229
        try:
            repeat_btn.place_forget()
        except Exception:
            pass
        # line 1231
        try:
            stop_btn.place_forget()
        except Exception:
            pass
        return
    # line 1235
    on = throw_repeat_event.is_set()
    # line 1237
    repeat_btn.place(x=10, y=90, width=PANEL_W - 20, height=32)
    # line 1238
    repeat_btn.config(state='normal')
    # line 1239
    repeat_btn.config(text=f'Repeat: {"ON" if on else "OFF"}')
    # line 1240
    repeat_btn.config(bg=BTN_BG_SELECTED if on else BTN_BG)
    # line 1242
    if on:
        stop_btn.place(x=10, y=90 + 36, width=PANEL_W - 20, height=32)
        stop_btn.config(text=stop_btn_text_default(), state='normal', bg=BTN_BG)
    else:
        try:
            stop_btn.place_forget()
        except Exception:
            pass


# Line 1248-1257: toggle_throw_repeat function
def toggle_throw_repeat():
    # line 1249
    if throw_repeat_event.is_set():
        # line 1250
        throw_repeat_event.clear()
        # line 1251
        stop_after_cycle_event.clear()
    else:
        # line 1253
        throw_repeat_event.set()
        # line 1254
        stop_after_cycle_event.clear()
    # line 1256
    refresh_repeat_button()


repeat_btn.configure(command=lambda: toggle_throw_repeat())
stop_btn.configure(command=lambda: request_stop_after_cycle())


# Line 1262-1270: _style_macro_buttons function
def _style_macro_buttons():
    if current_macro == 'Throw':
        btn_throw.config(bg=BTN_BG_SELECTED)
        btn_key.config(bg=BTN_BG)
    else:
        btn_throw.config(bg=BTN_BG)
        btn_key.config(bg=BTN_BG_SELECTED)


# Line 1272-1279: select_throw function
def select_throw():
    global current_macro, macro_total_duration
    # line 1274
    current_macro = 'Throw'
    # line 1275
    macro_total_duration = THROW_TOTAL_DURATION
    # line 1276
    set_macro_label()
    # line 1277
    _style_macro_buttons()
    # line 1278
    refresh_repeat_button()


# Line 1281-1288: select_key function
def select_key():
    global current_macro, macro_total_duration
    # line 1283
    current_macro = 'Key'
    # line 1284
    macro_total_duration = KEY_TOTAL_DURATION
    # line 1285
    set_macro_label()
    # line 1286
    _style_macro_buttons()
    # line 1287
    refresh_repeat_button()


btn_throw.configure(command=lambda: select_throw())
btn_key.configure(command=lambda: select_key())


# Line 1300-1313: update_progress_loop function
def update_progress_loop():
    # line 1301
    with run_lock:
        running = is_running
        start_t = macro_start_time
        dur = macro_total_duration
    # line 1306
    if not running or start_t is None or dur <= 0:
        # line 1307
        progress_var.set(0.0)
        return
    # line 1310
    elapsed = time.perf_counter() - start_t
    # line 1311
    pct = max(0.0, min(100.0, elapsed / dur * 100.0))
    # line 1312
    progress_var.set(pct)
    # line 1313
    root.after(20, update_progress_loop)


# Line 1318-1409: worker function
def worker():
    global is_running, macro_start_time
    # line 1320
    stopped_by_user = False
    # line 1322
    try:
        # line 1323
        if current_macro == 'Throw':
            # line 1324
            while True:
                # line 1325
                with run_lock:
                    macro_start_time = time.perf_counter()
                # line 1328
                run_throw_macro_once()
                # line 1331
                if not throw_repeat_event.is_set():
                    break
                # line 1336
                tap_e(THROW_REPEAT_E_DWELL)
                # line 1337
                time.sleep(max(0.0, THROW_REPEAT_GAP))
                # line 1338
                if not throw_repeat_event.is_set():
                    break
                # line 1341
                time.sleep(max(0.0, THROW_AFTER_E_BEFORE_TAB_DELAY))
                # line 1342
                if not throw_repeat_event.is_set():
                    break
                # line 1345
                tap_tab(THROW_TAB_DWELL)
                # line 1346
                if not throw_repeat_event.is_set():
                    break
                # line 1349
                time.sleep(max(0.0, THROW_AFTER_TAB_BEFORE_AIM_DELAY))
                # line 1350
                if not throw_repeat_event.is_set():
                    break
                # line 1353
                move_mouse_up_angle()
                # line 1354
                double_click_left()
                # line 1356
                if stop_after_cycle_event.is_set():
                    stopped_by_user = True
                    break
                # line 1360
                time.sleep(max(0.0, THROW_REPEAT_RESTART_DELAY))
                # line 1361
                if not throw_repeat_event.is_set():
                    break
                # line 1364
                if stop_after_cycle_event.is_set():
                    stopped_by_user = True
                    break
        else:
            # line 1369
            with run_lock:
                macro_start_time = time.perf_counter()
            # line 1372
            run_key_macro_once()
    except Exception:
        pass
    finally:
        # line 1377
        mouse_safe_release(0.25)
        # line 1379
        with run_lock:
            is_running = False
            macro_start_time = None
        # line 1384
        stop_after_cycle_event.clear()
        # line 1386
        try:
            stop_btn.config(text=stop_btn_text_default(), bg=BTN_BG, state='normal')
        except Exception:
            pass
        # line 1392
        def _after_finish():
            set_status('Idle (press start key)')
            set_controls_enabled(True)
        # line 1397
        try:
            root.after(0, _after_finish)
        except Exception:
            pass


# Line 1412-1417: start key capture button commands
def begin_capture_start_key():
    global capture_start_key
    capture_start_key = True
    set_status('Press any key for START...')
    set_controls_enabled(False)


def begin_capture_clumsy_key():
    global capture_clumsy_key
    capture_clumsy_key = True
    set_status('Press any key for CLUMSY...')
    set_controls_enabled(False)


change_key_btn.configure(command=lambda: begin_capture_start_key())
change_clumsy_btn.configure(command=lambda: begin_capture_clumsy_key())


# Line 1420-1439: start_macro function
def start_macro():
    global is_running, run_thread, macro_start_time, macro_total_duration
    # line 1422
    with run_lock:
        if is_running:
            return
        is_running = True
        if current_macro == 'Throw':
            macro_total_duration = THROW_TOTAL_DURATION
        else:
            macro_total_duration = KEY_TOTAL_DURATION
        macro_start_time = time.perf_counter()
    # line 1432
    set_status(f'Running {current_macro}...')
    # line 1433
    set_controls_enabled(False)
    # line 1434
    stop_after_cycle_event.clear()
    # line 1436
    run_thread = threading.Thread(target=worker, daemon=True)
    run_thread.start()
    # line 1439
    root.after(20, update_progress_loop)


# Line 1466-1537: on_press function
def on_press(key):
    global start_key, capture_start_key, capture_clumsy_key, is_running
    # line 1468
    if keys_equal(key, exit_key):
        try_exit()
        return False
    # line 1473
    if keys_equal(key, toggle_ui_key):
        root.after(0, toggle_ui)
        return True
    # line 1478
    if capture_start_key:
        capture_start_key = False
        start_key = key
        def _after():
            refresh_start_key_label()
            set_status('Idle (press start key)')
            set_controls_enabled(True)
        root.after(0, _after)
        return True
    # line 1490
    if capture_clumsy_key:
        capture_clumsy_key = False
        set_clumsy_key(key)
        def _after():
            refresh_clumsy_key_label()
            set_status('Idle (press start key)')
            set_controls_enabled(True)
        root.after(0, _after)
        return True
    # line 1502
    if keys_equal(key, start_key):
        with run_lock:
            running = is_running
        if running:
            # line 1507
            with run_lock:
                is_running = False
            # line 1510
            if current_macro == 'Throw' and throw_repeat_event.is_set():
                request_stop_after_cycle()
            else:
                # line 1514
                root.after(0, lambda: set_status('Stopping...'))
        else:
            # line 1517
            root.after(0, start_macro)
        return True
    # line 1521
    return True


# Line 1524: Start keyboard listener
listener = Listener(on_press=on_press)
listener.start()

# Line 1527-1532: Apply initial layout
for btn in [change_key_btn, change_clumsy_btn, exit_btn, btn_throw, btn_key, repeat_btn, stop_btn]:
    style_action_button(btn)

panel_title.place(x=10, y=10)
btn_throw.place(x=10, y=42, width=HALF_PANEL_BTN_W, height=34)
btn_key.place(x=10 + HALF_PANEL_BTN_W + 10, y=42, width=HALF_PANEL_BTN_W, height=34)
panel_hint.place(x=10, y=130)

for w, opts in expanded_layout:
    w.place(**opts)

select_throw()
refresh_repeat_button()


# Line 1541-1621: show_key_gate_window function
def show_key_gate_window():
    # line 1543
    gate = tk.Toplevel(root)
    gate.title('Enter Key')
    gate.geometry(KEY_ENTRY_GEOMETRY)
    gate.configure(bg='#1a1a1a')
    gate.attributes('-topmost', True)
    gate.overrideredirect(True)
    # line 1551
    msg_var = tk.StringVar(value='Enter activation key:')
    # line 1553
    msg_lbl = tk.Label(gate, textvariable=msg_var, fg='white', bg='#1a1a1a', font=('Segoe UI', 10))
    msg_lbl.pack(pady=(15, 5))
    # line 1557
    entry = tk.Entry(gate, font=('Segoe UI', 11), width=30)
    entry.pack(pady=5)
    entry.focus_set()
    # line 1561
    btn = tk.Button(gate, text='Validate', font=('Segoe UI', 10))
    style_action_button(btn)
    btn.pack(pady=10)

    # line 1563-1570: close_all function
    def close_all():
        try:
            gate.destroy()
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass
        sys.exit(0)

    # line 1573-1581: submit function
    def submit():
        k = entry.get().strip()
        if not k:
            msg_var.set('Please enter a key.')
            return
        btn.config(state='disabled')
        entry.config(state='disabled')
        msg_var.set('Validating...')

        # line 1583-1589: _check function
        def _check():
            err = None
            try:
                ok = validate_key(k)
            except Exception as e:
                err = str(e)
                ok = False

            # line 1591-1609: _done function
            def _done():
                if ok:
                    unlocked_event.set()
                    try:
                        gate.destroy()
                    except Exception:
                        pass
                    try:
                        root.deiconify()
                        root.lift()
                        root.attributes('-topmost', True)
                    except Exception:
                        pass
                    set_status('Idle (press start key)')
                else:
                    entry.config(state='normal')
                    btn.config(state='normal')
                    entry.focus_set()
                    msg_var.set(f'Error: {err[:70]}' if err else 'Invalid key.')

            gate.after(0, _done)

        threading.Thread(target=_check, daemon=True).start()

    btn.configure(command=submit)
    entry.bind('<Return>', lambda e: submit())
    gate.protocol('WM_DELETE_WINDOW', close_all)


# Line 1624-1630: Main entry point
if KEY_GATE_ENABLED:
    root.withdraw()
    show_key_gate_window()
else:
    unlocked_event.set()

root.mainloop()