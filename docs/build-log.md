# Build Log

## Phase 1 — Breadboard Prototype ✅

### What was built
- Raspberry Pi Pico running MicroPython
- DFPlayer Mini connected via UART (GP0/GP1)
- SSD1306 128×64 OLED connected via I2C (GP4/GP5)
- BUSY pin (GP15) used for track detection

### Problems solved
- DFPlayer clone returns status 512 instead of 0/1/2
  Fix: switched from UART status polling to BUSY pin detection
- Elapsed time drifted out of sync with audio
  Fix: switched from tick counting to hardware clock subtraction
- OLED showing ETIMEDOUT error on boot
  Fix: SDA/SCL wires were swapped

### Current features
- Auto-plays all tracks in order
- Loops back to track 1 after last track
- OLED shows track number, scrolling title,
  progress bar, and elapsed/total time
- Real-time sync using time.ticks_ms()
- Ctrl+C stops playback cleanly

### Next steps
- Add 5x buttons for play/pause and track control
- Move to protoboard layout (Phase 2)
