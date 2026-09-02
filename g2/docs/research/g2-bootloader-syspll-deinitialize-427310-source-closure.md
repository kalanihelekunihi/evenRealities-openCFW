# G2 bootloader SYSPLL deinitialization source closure at `0x00427310`

The bootloader interval `[0x00427310,0x00427360)` is the AmbiqSuite 5.1.0
`am_hal_syspll_deinitialize()` service. This admission closes the software
implementation gap with reviewable BSD-3-Clause C; it does not claim physical
PLL validation.

## Authentication

- Stock interval: 80 bytes, SHA-256
  `1eba50a003fd2dbc10b692f916c95ac832659ee8245f1420e20cf06373631424`.
- Apollo-main analogue: `[0x00539944,0x00539994)`, 80 bytes, SHA-256
  `15762cbfef691f5bc58b02426033212a57b18b62f4f594a1c40167790a83629c`.
- The two bodies have 74 identical bytes. Their five difference runs are
  confined to the handle-magic literal load and the three image-local provider
  branch encodings.
- The stock direct callers are `0x00422198` and `0x00422266`, both inside the
  already source-owned row-six lifecycle services.
- The stock provider edges call the authenticated SYSPLL stop service at
  `0x004273dc`, power-state query at `0x0041cae8`, and power-disable service at
  `0x0041caa2`. The Apollo-main counterparts are `0x00539a10`, `0x004800e4`,
  and `0x0048009e`.
- The handle-check literal at `0x004275ac` is `0x01504c30`; its four-byte
  SHA-256 is
  `c9767509276a128588c8373a4e0a1757b7e97633a7a1cc7cabbc92cd5f260a6e`.
- The reviewed official source is
  `mcu/apollo510/hal/mcu/am_hal_syspll.c` at commit
  `e8baebd44008dfec7197d40d53c8a62f3a36b38b`. The 48,933-byte source has
  SHA-256
  `b2ac1b4a89ff7c2e17f57f199998688e9de4a67ca9035d5dbf8063b94da18b28`.

## Production realization

`runtime_syspll_deinitialize_427310.c` implements the exact handle-mask and
magic validation, conditional stop with status propagation, unconditional
power-state query, conditional power disable, and initialization-bit clear.
The query and power-disable return values are intentionally ignored, matching
the official implementation. The file contains no raw instruction encoding.

Apple Clang 21.0.0 and Homebrew Clang 22.1.8 both compile the service to 80
bytes. The unrelocated SHA-256 is
`613b87866651212d7ea0584e9fe70602aedce9203e096caa825b3f84d6538ddd`.
After the three `R_ARM_THM_CALL` relocations at offsets 38, 48, and 60, the
in-place body SHA-256 is
`cadcef39ea58cdba4a2059dd41ca75ed8c569d6cc3edf941d8a321dc4a343189`.
The complete stock body is replaced directly by this same-size compiled C
body; no trampoline, instruction-byte transcription, or appended executable
space is used.

Host semantic tests cover invalid handles, the disabled/unpowered path, the
enabled/powered path, stop-status propagation, ignored power-provider status,
call ordering, and exact bit preservation. Both reviewed firmware toolchains
rebuild the complete bootloader provider with the admitted service.

## Hardware evidence boundary

On-device SYSPLL power, lock, clock-distribution, current, and timing behavior
requires an authorized G2 unit, debug/programming access, measurement
equipment, and a recorded test procedure. None is available in this
workspace. The exact hardware status is therefore **blocked by unavailable
physical evidence**. No MMIO access, flashing, signing, reset, or hardware
communication was performed for this admission.
