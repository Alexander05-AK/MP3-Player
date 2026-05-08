# Wiring Reference

## Pin Assignments

| Component      | Component Pin | Pico GPIO | Notes                    |
|---------------|---------------|-----------|--------------------------|
| DFPlayer Mini | RX            | GP0       | Direct connection        |
| DFPlayer Mini | TX            | GP1       | Via 1kΩ/2kΩ divider     |
| DFPlayer Mini | BUSY          | GP15      | Direct connection        |
| DFPlayer Mini | VCC           | 3V3       | Pin 36                   |
| DFPlayer Mini | GND           | GND       | Pin 38                   |
| SSD1306 OLED  | SDA           | GP4       | Direct connection        |
| SSD1306 OLED  | SCL           | GP5       | Direct connection        |
| SSD1306 OLED  | VCC           | 3V3       | Pin 36                   |
| SSD1306 OLED  | GND           | GND       | Pin 38                   |
| Speaker       | +             | SPK1      | DFPlayer SPK1 terminal   |
| Speaker       | -             | SPK2      | DFPlayer SPK2 terminal   |

## Voltage Divider (DFPlayer TX → Pico GP1)

DFPlayer TX outputs 5V logic. Pico GPIO max is 3.3V.
This divider drops it to a safe level.

Output = 5V × (2kΩ / 3kΩ) = 3.33V ✅

## SD Card Requirements

- Format: FAT32
- Max size: 32GB (8GB recommended)
- File naming: 0001.mp3, 0002.mp3, 0003.mp3
- Location: root directory only
- Bitrate: 128kbps CBR recommended
