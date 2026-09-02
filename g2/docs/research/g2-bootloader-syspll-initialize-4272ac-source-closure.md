# G2 bootloader SYSPLL initialization source closure at `0x004272ac`

The bootloader interval `[0x004272ac,0x00427308)` is the AmbiqSuite 5.1.0
`am_hal_syspll_initialize()` service.  This admission closes the software
implementation gap with reviewable BSD-3-Clause C; it does not claim physical
PLL validation.

## Authentication

- Stock interval: 92 bytes, SHA-256
  `3284295a51640dd35e9518837d69df3369ff537705ef07e88586fb2a0f8a1414`.
- Apollo-main analogue: `[0x005398e0,0x0053993c)`, 92 bytes, SHA-256
  `344102274cb76e2a8e22e731aeb54f9905ff60611af472e0f2651fa87da23230`.
- The two bodies have 86 identical bytes.  Their four difference runs are
  confined to the state-array literal load, magic literal load, and
  image-local power-provider branch encoding.
- The only stock direct caller is `0x0042215e`, inside the already source-owned
  row-six enable transaction.
- The stock provider edge at offset `0x4e` calls `0x0041ca5c`, the authenticated
  bootloader SYSPLL power-enable service.  The Apollo-main analogue calls its
  image-local provider at `0x00480058`.
- The state-array literal at `0x004275a4` is `0x20027010`; its four-byte SHA-256
  is `f14031f7f4ab831f8796faf88fd60abc9862157144c8323dc0fc87344c564f5c`.
  The handle-magic literal at `0x004275a8` is `0x00504c30`; its four-byte
  SHA-256 is
  `0316b8f8552e5da7138d905d0738f73b207f3bdf980ca5bcd3afbae0c653bc63`.
- The official AmbiqSuite source file is 48,933 bytes with SHA-256
  `b2ac1b4a89ff7c2e17f57f199998688e9de4a67ca9035d5dbf8063b94da18b28`
  at commit `e8baebd44008dfec7197d40d53c8a62f3a36b38b`.

## Production realization

`runtime_syspll_initialize_4272ac.c` implements the authenticated one-module
range check, null-handle rejection, initialized-state rejection, preservation
of the prefix high byte, initialization-bit and `0x504c30` magic publication,
module publication, power-enable call, and handle return.  It contains no raw
instruction encoding.

Apple Clang 21.0.0 and Homebrew Clang 22.1.8 both compile the leaf to 60 bytes.
The unrelocated SHA-256 is
`64d2229baba9bb087b18085b981384b12128878de3b8e3fae89769f5b9d4a444`;
after the single `R_ARM_THM_CALL` relocation at offset 34 to `0x0041ca5c`, the
SHA-256 is
`14ec1958a36f051655ae9420ae0574fd83c9773848760f0592be766725004716`.
The complete stock body is replaced by an 8-byte generated entry redirect,
the 60-byte source cave at `[0x004272b4,0x004272f0)`, and 24 bytes of
unreachable generated NOP fill through `0x00427308`.

Host semantic tests cover every status path and verify that rejected calls
have no side effects, successful initialization preserves unrelated high
flags, publishes the exact prefix and module, invokes power once, and returns
the state handle.  Both reviewed firmware toolchains rebuild the complete
bootloader provider with the admitted leaf.

## Hardware evidence boundary

On-device SYSPLL power, lock, clock-distribution, current, and timing behavior
requires an authorized G2 unit, debug/programming access, measurement
equipment, and a recorded test procedure.  None is available in this
workspace.  The exact hardware status is therefore **blocked by unavailable
physical evidence**.  No MMIO access, flashing, signing, reset, or hardware
communication was performed for this admission.
