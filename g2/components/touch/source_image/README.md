# G2 Touch source image

SPDX-License-Identifier: MIT

This target links every openCFW Touch translation unit into one freestanding
ARMv6-M ELF, extracts the flash image, appends its reflected CRC-32C, and
wraps it in the type-3 FWPK container accepted by the G2 host updater.

The image is a software-link artifact, not a hardware-qualified release. Do
not flash the image.

`psoc4000t_nvic.h` names which PSoC 4000T NVIC IRQ number is SCB1, MSCLP, and
every other external interrupt, citing the public `psoc4000t.svd` ordering
already cross-checked against the shipped vector-table shape in
`g2/docs/research/g2-touch-identity-recovery.md`. That slot *assignment* is
silicon configuration, not a hardware blocker, and `startup.c`'s vector table
is built from it by name (see `tests/test_runtime_touch_nvic_config.py`).
What remains genuinely hardware-blocked -- because it requires a physical
part to observe or qualify -- is the runtime MMIO *behavior* each handler
would perform (SCB1 I2C shift-register service, MSCLP CapSense scan
draining, flash/EEPROM row migration, GPIO/pin routing, and the separate
resident DFU entry point reached after a mailbox/reset handoff, which this
image does not implement). Those stay documented as
`hardware_validation: blocked by unavailable physical evidence`.

Build with:

```sh
python3 components/touch/source_image/build_image.py
```

The summary explicitly reports `production_routed: false` (this script's own,
manifest-independent report) and `hardware_validation: blocked by
unavailable physical evidence`. Production routing is a manifest-level fact:
`manifests/g2-2.2.6.10-touch-source-experimental.json` overrides the `touch`
component to this image's `source_build` provider (see `make
touch-source-experimental`). Board qualification is a separate pre-release
activity.
