# GX8002 IRQ mask wrappers

`gx_mask_irq` at `0x100254fc` / package `0x17510` and `gx_unmask_irq` at
`0x10025504` / package `0x17518` are reconstructed as distinct C call entries.
They call the separately recovered internal disable/enable routines at
`0x100254c8` and `0x100254ac`, respectively. Each compiles to eight exact
stock bytes and preserves its four-byte frame. The public declarations are
checked against the authenticated NationalChip IRQ header at commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`.

Decoded comparisons cover 1,884 input/seed cases, including high-bit values
and inverted single-bit patterns. The target compiler preserves the original
32-bit argument representation through conversion from unsigned public input
to signed internal input. Helpers clobber caller-saved registers. Five
regression tests cover dispatch direction, bit preservation and frame checks.
This validates the wrappers, not out-of-domain IRQ values or hardware timing
in the underlying routines. They and the SNPU clock gate are integrated; all 398 integration tests pass.

```sh
python3 g2/tools/verify_gx8002_irq_mask.py
python3 -m unittest discover -s g2/tests -p test_gx8002_irq_mask.py
```

Next clock candidate: `runtime_gx8002_snpu_clock.c` compiles to36 text bytes,
fitting the original36-byte envelope at runtime `0x100251ec` /package
`0x17200`. It saves interrupt state using the already recovered IRQ save
routine (`0x10025560`), reads clock register `0xa0300018`, clears bit8 when
enable is nonzero or sets bit8 when zero, writes it, then restores the exact
saved state through `0x1002556c`. Need a reproducible linked builder and
independent save/read/write/restore oracle, helper-clobber and frame checks.
No source admission yet. The object and disassembly are under
`build/gx8002-board/snpu-clock-candidate*`.

The SNPU clock candidate described above is now linked, qualified and
integrated; see gx8002-snpu-clock-source.md for current evidence.
