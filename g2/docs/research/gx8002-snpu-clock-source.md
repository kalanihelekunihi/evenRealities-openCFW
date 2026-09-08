# GX8002 SNPU clock gate

The reconstructed C routine occupies all 36 original bytes at runtime
`0x100251ec` / package `0x17200`. It saves interrupt state via the separately
source-qualified IRQ helper, reads `0xa0300018`, clears bit8 for any nonzero
enable argument or sets bit8 for zero, writes the register, then restores
the exact saved state. The frame is eight bytes.

Decoded stock and source instructions match an independent ordered trace
in 8,442 cases, varying enable encodings, all single-bit/inverted-single-bit
register values, saved-state return patterns and initial registers. Eight
regression tests check direction, high-bit enable values, register/bit,
restore-state preservation and helper/frame errors. The public interface
matches the authenticated NationalChip clock header at the pinned SDK commit.

Saved-state patterns are helper-return contracts, not assertions that every
pattern is a valid hardware PSR. The IRQ helper has separate qualification;
these checks do not prove physical clock/interrupt timing.

```sh
python3 g2/tools/verify_gx8002_snpu_clock.py
python3 -m unittest discover -s g2/tests -p test_gx8002_snpu_clock.py
```

Evidence: `gx8002-snpu-clock-verification.json`.

This function is integrated with the IRQ mask wrappers. All 398 integration
tests pass; full firmware and hardware qualification remain incomplete.
