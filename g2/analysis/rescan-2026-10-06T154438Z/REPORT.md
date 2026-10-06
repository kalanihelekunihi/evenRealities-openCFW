# Source rescan

Compared with the 14:50 UTC snapshot.

{
  "utc": "2026-10-06T15:44:38.168420+00:00",
  "baseline": "g2/analysis/rescan-2026-10-06T145020Z",
  "counts": {
    "g2/components/bootloader": 43,
    "g2/components/foundation": 89
  },
  "added": [
    "g2/components/bootloader/nor_read/nor_read.c",
    "g2/components/bootloader/nor_read/nor_read.h",
    "g2/components/bootloader/platform_control/critical_save.S",
    "g2/components/bootloader/platform_control/power_guards.c",
    "g2/components/bootloader/queue/mutex.c",
    "g2/components/bootloader/queue/queue_wrappers.c",
    "g2/components/bootloader/queue/queue_wrappers.h",
    "g2/components/bootloader/queue/runtime_mode.c"
  ],
  "modified": [
    "g2/components/bootloader/platform_control/control.c"
  ],
  "ignored": 0
}

This is an on-disk source/ignore comparison, not a fresh execution or firmware-completeness claim. No staging, cleanup or firmware writes performed.
