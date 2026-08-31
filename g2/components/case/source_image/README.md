# G2 charging-case source image

SPDX-License-Identifier: MIT

This target compiles every clean-room charging-case translation unit for the
ARMv6-M Cortex-M0+ target, links a complete STM32G0-class ELF, extracts a raw
flash image, and produces the 32-byte `EVEN` transport package with the
big-endian additive checksum used by the G2 case updater.

The build is software-link complete but not hardware-qualified. Exact board
interrupt ownership, GPIO/timer routing, dual-bank updater handoff, and
identity-window copy-forward behavior cannot be selected or validated from the
available physical evidence. Startup therefore remains inert and must not be
flashed. Hardware validation is blocked by unavailable physical evidence.

Run `python3 components/case/source_image/build_image.py --check` for a
non-persistent verification build.
