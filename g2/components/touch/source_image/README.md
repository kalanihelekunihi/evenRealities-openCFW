# G2 Touch source image

SPDX-License-Identifier: MIT

This target links every openCFW Touch translation unit into one freestanding
ARMv6-M ELF, extracts the flash image, appends its reflected CRC-32C, and
wraps it in the type-3 FWPK container accepted by the G2 host updater.

The image is a software-link artifact, not a hardware-qualified release. The
SCB1, MSCLP, flash/EEPROM migration, GPIO/pin routing, and resident DFU
contracts cannot be selected honestly from the available physical evidence.
Their interrupt vectors are therefore evidence-locked. Do not flash the image.

Build with:

```sh
python3 components/touch/source_image/build_image.py
```

The summary explicitly reports `production_routed: false` and
`hardware_validation: deferred by project direction` while this phase remains
software-only. Board qualification is a separate pre-release activity.
