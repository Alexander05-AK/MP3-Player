# player_display.py
# Auto-playing MP3 player — complete unified code
# Uses BUSY pin for track detection, real clock for elapsed time
# Platform: Raspberry Pi Pico + MicroPython

from machine import Pin, UART, I2C
import ssd1306
import time

# ═══════════════════════════════════════════════════════════════
# PIN DEFINITIONS
# ═══════════════════════════════════════════════════════════════
UART_TX  = 0
UART_RX  = 1
I2C_SDA  = 4
I2C_SCL  = 5
BUSY_PIN = 15

# ═══════════════════════════════════════════════════════════════
# SONG LIBRARY
# Edit this to match your SD card files exactly.
# Duration only needs to be approximate — it's for the
# progress bar visual only. Track advance is handled by
# the BUSY pin, not this number.
# 0001.mp3 → SONGS[0], 0002.mp3 → SONGS[1], etc.
# ═══════════════════════════════════════════════════════════════
SONGS = [
  ("resonance, Home",  212),
    ("bags", 260),
    ("Hallejuah",   391),

]

# ═══════════════════════════════════════════════════════════════
# DFPLAYER DRIVER
# ═══════════════════════════════════════════════════════════════
class DFPlayer:
    def __init__(self, tx, rx):
        self.uart = UART(0, baudrate=9600, tx=Pin(tx), rx=Pin(rx),
                         bits=8, parity=None, stop=1)
        time.sleep_ms(1000)

    def _send(self, cmd, param=0):
        p_hi = (param >> 8) & 0xFF
        p_lo = param & 0xFF
        s    = 0xFF + 0x06 + cmd + 0x00 + p_hi + p_lo
        cs   = (~s + 1) & 0xFFFF
        pkt  = bytes([0x7E, 0xFF, 0x06, cmd, 0x00,
                       p_hi, p_lo, (cs>>8)&0xFF, cs&0xFF, 0xEF])
        self.uart.write(pkt)
        time.sleep_ms(30)

    def reset(self):         self._send(0x0C); time.sleep_ms(1500)
    def set_source(self):    self._send(0x09, 2); time.sleep_ms(200)
    def set_volume(self, v): self._send(0x06, max(0, min(30, v)))
    def play_index(self, i): self._send(0x03, i)
    def stop(self):          self._send(0x16)

# ═══════════════════════════════════════════════════════════════
# BUSY PIN
# ═══════════════════════════════════════════════════════════════
busy = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)

def is_busy():
    """
    Returns True if DFPlayer is currently playing.
    BUSY LOW  = playing
    BUSY HIGH = stopped
    """
    return busy.value() == 0

# ═══════════════════════════════════════════════════════════════
# OLED SETUP
# ═══════════════════════════════════════════════════════════════
i2c  = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# ═══════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════

def fmt_time(seconds):
    """Convert seconds to M:SS — e.g. 254 → '4:14'"""
    s = max(0, int(seconds))
    return f"{s // 60}:{s % 60:02d}"

def draw_progress_bar(elapsed, total, x, y, w, h):
    """
    Hollow rectangle with filled portion showing progress.
    Clamps fill between 0 and full width so it never
    overflows if elapsed slightly exceeds duration.
    """
    oled.rect(x, y, w, h, 1)
    if total > 0 and elapsed > 0:
        filled = max(0, min(w - 2, int((elapsed / total) * (w - 2))))
        if filled > 0:
            oled.fill_rect(x + 1, y + 1, filled, h - 2, 1)

def draw_scrolling_text(text, y, offset):
    """
    Draws text that scrolls left when longer than 16 chars.
    Loops seamlessly by drawing the string twice side by side
    and sliding a window across both copies.
    """
    if len(text) <= 16:
        oled.text(text, 0, y)
    else:
        padded      = text + "    "      # gap before text repeats
        pixel_width = len(padded) * 8
        x           = -(offset % pixel_width)
        oled.text(padded + padded, x, y)

def render_ui(song_idx, elapsed, scroll_offset, playing):
    """
    Full screen layout:
    ┌──────────────────────────────┐
    │ Track 01/03              ▶  │  y=0
    │ Song Title Scrolling...      │  y=14
    │ ██████████████░░░░░░░░░░░░  │  y=28  progress bar
    │ 1:23          /      5:54   │  y=40  time
    │ CTR+C = stop                 │  y=54  hint
    └──────────────────────────────┘
    """
    oled.fill(0)

    name, duration = SONGS[song_idx]

    # ── Track counter ─────────────────────────────────────────
    oled.text(f"Track {song_idx+1}/{len(SONGS)}", 0, 0)

    # ── Playback status icon (top right) ─────────────────────
    if playing:
        # Play triangle pointing right
        oled.fill_rect(118, 1, 2, 7, 1)
        oled.fill_rect(120, 2, 2, 5, 1)
        oled.fill_rect(122, 3, 2, 3, 1)
        oled.fill_rect(124, 4, 2, 1, 1)
    else:
        # Pause — two vertical bars
        oled.fill_rect(118, 1, 3, 7, 1)
        oled.fill_rect(123, 1, 3, 7, 1)

    # ── Scrolling song title ──────────────────────────────────
    draw_scrolling_text(name, 14, scroll_offset)

    # ── Progress bar ──────────────────────────────────────────
    draw_progress_bar(elapsed, duration, 0, 28, 128, 7)

    # ── Elapsed / total time ──────────────────────────────────
    oled.text(fmt_time(elapsed), 0, 40)
    oled.text("/", 50, 40)
    oled.text(fmt_time(duration), 62, 40)

    # ── Bottom hint ───────────────────────────────────────────
    oled.text("CTR+C = stop", 4, 54)

    oled.show()

def splash():
    """Boot screen shown while DFPlayer initializes."""
    oled.fill(0)
    oled.text("  MP3 Player", 4, 16)
    oled.text("  Loading...", 4, 32)
    oled.show()

# ═══════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════
splash()

df = DFPlayer(tx=UART_TX, rx=UART_RX)
df.reset()
df.set_source()
df.set_volume(20)    # 0–30, adjust to taste

# ═══════════════════════════════════════════════════════════════
# PLAYER STATE
# ═══════════════════════════════════════════════════════════════
current        = 0
elapsed        = 0.0
scroll_offset  = 0
scroll_delay   = 0
track_start_ms = 0       # real clock ms when current track started

TICK_MS        = 100     # main loop interval
SCROLL_PAUSE   = 20      # frames to hold before scrolling starts
GRACE_PERIOD_S = 3.0     # seconds to ignore BUSY pin after track start

def start_track(idx):
    """
    Start playing a track and reset all state.
    Records exact start time for real-clock elapsed tracking.
    """
    global current, elapsed, scroll_offset
    global scroll_delay, track_start_ms

    current        = idx % len(SONGS)
    elapsed        = 0.0
    scroll_offset  = 0
    scroll_delay   = SCROLL_PAUSE
    track_start_ms = time.ticks_ms()   # snapshot real clock

    df.play_index(current + 1)         # DFPlayer is 1-based
    print(f"Now playing: {SONGS[current][0]}")

    # Give DFPlayer time to assert BUSY LOW before
    # the main loop starts checking it
    time.sleep_ms(500)

# ═══════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════
start_track(0)

try:
    while True:

        # ── Real elapsed time ─────────────────────────────────
        # ticks_diff handles millisecond counter overflow safely.
        # This is always accurate — no drift from loop timing.
        elapsed = time.ticks_diff(
                      time.ticks_ms(),
                      track_start_ms
                  ) / 1000.0

        # ── Track finished detection ──────────────────────────
        # Wait for grace period so DFPlayer has fully started
        # before we trust the BUSY pin reading.
        # Double-check after 300ms to rule out brief gaps
        # between buffer loads on clone modules.
        if elapsed > GRACE_PERIOD_S and not is_busy():
            time.sleep_ms(300)
            if not is_busy():
                print(f"Track finished at {fmt_time(elapsed)}")
                start_track(current + 1)

        # ── Title scroll ──────────────────────────────────────
        name, _ = SONGS[current]
        if len(name) > 16:
            if scroll_delay > 0:
                scroll_delay -= 1
            else:
                scroll_offset += 1

        # ── Redraw display ────────────────────────────────────
        render_ui(current, elapsed, scroll_offset, is_busy())

        time.sleep_ms(TICK_MS)

except KeyboardInterrupt:
    df.stop()
    oled.fill(0)
    oled.text("  Stopped.", 16, 24)
    oled.text("Press F5 to", 16, 36)
    oled.text("play again.", 16, 46)
    oled.show()
    print("Stopped.")

