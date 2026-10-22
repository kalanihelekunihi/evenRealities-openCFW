# Offline GPIO and clock-request providers

Evidence, data layouts, caller errors and boundaries (`pre-consolidation:g2/analysis/audio-gpio-providers-2026-10-08/REPORT.md`). Not production firmware.

`gpio.c` (the 0x480EEE/0x480F0C pin-configuration copies) was retired in favour of the upstream AmbiqSuite 5.1.0 `am_hal_gpio.c` unit; `gpio.h` keeps the provider names, which the payload defsym map binds to `am_hal_gpio_pinconfig_get` / `am_hal_gpio_pinconfig`.
