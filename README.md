# DIY MP3 Player 🎵

A fully hand-built MP3 player using a Raspberry Pi Pico,
DFPlayer Mini audio module, and SSD1306 OLED display.
Built in progressive phases from breadboard to custom PCB.

## Demo
![Breadboard prototype](hardware/photos/breadboard.jpg)

## Features
- MP3 playback from microSD card
- 128×64 OLED showing track name and progress bar
- Scrolling text for long song titles
- Real-time elapsed time (hardware clock accurate)
- Auto-advance via DFPlayer BUSY pin
- Loops through all tracks continuously

## Hardware

| Component          | Purpose                      | 
|-------------------|------------------------------|
| Raspberry Pi Pico | Main microcontroller         |
| DFPlayer Mini     | MP3 decoding + amp + SD card |
| SSD1306 0.96"    | 128×64 OLED display          |
| Small speaker     | Audio output (4Ω or 8Ω)     |

## Project Phases

- [x] **Phase 1** — Breadboard prototype
- [ ] **Phase 2** — Protoboard layout
- [ ] **Phase 3** — Custom PCB in KiCad
- [ ] **Phase 4** — 3D printed enclosure
- [ ] **Phase 5** — Firmware optimisation and polish

## Wiring

See [docs/wiring.md](docs/wiring.md) for full pin reference.

## Software Setup

1. Flash MicroPython to your Pico
2. Copy `firmware/lib/ssd1306.py` to `/lib/` on the Pico
3. Edit the `SONGS` list in `firmware/main.py`
4. Copy `firmware/main.py` to the Pico as `main.py`
5. Power on — playback starts automatically

## Build Log

See [docs/build-log.md](docs/build-log.md) for problems
solved and lessons learned at each phase.

## License
MIT
