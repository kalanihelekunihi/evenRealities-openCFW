# Native image-B audio IRQ frontier

The formerly remaining linked import is the native unseeded handler
`0x10015830..0x10015b60` in the pinned image-B corpus. It lies beyond the
288-function retained Ghidra catalogue. Native C-SKY disassembly establishes:

- Peripheral base `0xa0a00000`; interrupt enable at `+0x100` and status/W1C
  at `+0x104`.
- Bits 18, 19, and 20 are checked first. The handler acknowledges active
  bits and calls the callback at state `0x20017624+0x14` with a 1/2/4 mask
  when any is active.
- Bits 0, 1, and 2 form a record callback mask; three address words come
  from `+0x124`, `+0x148`, and `+0x168`. Callback is at state `+0x0c`.
- Bits 3, 4, and 5 form an update callback mask; corresponding address words
  come from `+0x128`, `+0x14c`, and `+0x16c`. Callback is at state `+0x10`.
- Bits 16 and 17 form the final 1/2 event mask. Callback is at state `+0x18`.
  The native CFG reaches this callback even when neither bit is active.
- The native body includes non-linear branches to `0x10015b0e`,
  `0x10015b2a`, `0x10015b3c`, `0x10015b4a`, and `0x10015b54`. A source
  implementation needs ordered MMIO read/W1C and callback-trace comparison
  over these edges; a single status snapshot is insufficient evidence.

`backup_audio_irq.c` now expresses those branches as a C candidate. Its
target relocatable links and 8,192 bounded host callback/W1C traces pass.
The fixture does not run the original C-SKY instructions, so exact read timing
and whole-body native equality remain unqualified.

The pinned vendor `drivers_lib/audio_in/v2.0/audio_in.o` contains a related
local `_AudioInISR` object symbol. It is provenance for the peripheral API,
not source or a proven byte/behavioral match to this native handler. No
image-A ISR body is substituted into image-B.
