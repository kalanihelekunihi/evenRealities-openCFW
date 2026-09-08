# Interrupt stack architecture evidence

The C-SKY ISA manual mirrored at <https://docs.alexrp.com/csky/csky.pdf>
has SHA-256 `579bd296dbf88b0b6842a473432e65199b87c0c19fcf04bb214f67241c68d509`.
Local analysis copy: `g2/build/csky-isa-manual.pdf`. This is a vendor-authored
document on a third-party mirror; it does not establish GX8002-specific errata.

Printed page 182 (PDF page 183), visually inspected, defines IPUSH as storing
R13 at old SP-4, R12 at SP-8, then R3, R2, R1 and R0 through SP-24.
SP decreases by 24. The heading incorrectly calls IPUSH a pop; both operation
formulas and the description identify a store. Printed page 180's visually inspected
IPOP definition restores R0, R1, R2, R3, R12, R13 from increasing addresses
starting at SP and increases SP by 24.

This supports identifying the pinned plugin's IPUSH order as inconsistent
with the manual, rather than changing IPOP to accommodate it. No upstream
plugin files have been changed. See `gx8002-irq-sleigh-audit.json` for the
authenticated model audit.

The NIE/NIR entries on printed pages 297 and 299 were visually inspected.
They describe an additional eight-byte EPC/EPSR frame and restoration of
PC/PSR. The architecture-frame verifier now models their saved values and
stack transfers, but not PSR enable-bit timing. Interrupt arrival, nesting eligibility, stack capacity and
GX8002 implementation details remain to be qualified. The IRQ candidate is
not admitted to the package.


`verify_gx8002_irq_architecture_frame.py` authenticates the manual and rebuilds
and decodes the native macOS IRQ candidate. All 24 seed/depth cases restore
shared stack memory, volatile registers and saved control values. One through
four callback levels consume modeled peaks of 136, 272, 408 and 544 bytes.
Three tests independently check fixed stack addresses and detect corrupted
saved R0 and EPC. Existing 24 software-only cases and three negative tests
still pass. Nested entry is injected only at the callback point, not every
instruction; no physical stack-capacity claim follows from these results.
