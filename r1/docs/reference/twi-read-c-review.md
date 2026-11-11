# TWI register reads: direct C with the native exposed frame

Current implementation: [ordinary C register-read status ABI](twi-register-read-pure-c-review.md). Read-adapter scratch-register/frame preservation described below is historical.

`application/board/native_hw_twi_register.c` now implements both register-read
adapters directly in C. The read bridges and their helper kernels were
removed. The write source and its compiled code/relocations are unchanged,
including the [length-80 saved-R4 overlap](twi-legacy-tx-c-review.md).

REA read the complete native windows at `0x54ff8` and `0x550c0`. The primary
body has 96 code bytes and a four-byte literal; the secondary has 90 code
bytes, two padding bytes and a four-byte literal. Both expose a 40-byte frame.
The outgoing fifth word at `+0` doubles as the restored R2 word; the register
byte at `+4` overlays the saved incoming length word restored into R3.

The C implementations retain those aliases. A volatile word starts with the
full incoming length, then receives the register byte. An empty SP-bound
compiler output reads the actual outgoing word before return, and empty
R0/R2/R3 constraints retain the restored results. These are nonportable ABI
annotations tied to the verified normal Clang layout, not portable stack
object assumptions or emitted assembly instructions.

Empty R4–R10 constraints also preserve provider-visible values. The post-TX
constraint is necessary: without that lifetime, the compiler can reuse a
native incoming register while preparing the fifth argument. The read paths
now call the typed legacy TX providers and pass the embedded instance to RX.
Primary RX truncates length to a byte; secondary RX forwards the full word.
Both choose the final timeout using the full incoming length. Raw nonzero
statuses stop the sequence before conversion to the returned low byte.

The actual normal Clang object passes 18,396 pairs in each of two modes:
modeled legacy TX and actual native/C legacy TX wrappers. The latter verifies
the 56-byte SDK TX depth, comprising the read frame and legacy wrapper frame.
The previous read bridges reach SDK TX at 112 bytes and are rejected by this
check. Coverage includes:

- Success and each failure stage, including nonzero statuses whose low byte
  is zero; raw register/length words and timeout boundaries.
- Partial buffer writes, control byte resets and output aliases into the two
  exposed frame words, control state and the caller's fifth word.
- 504 null-output cases per mode, returned R0/R2/R3, R4–R11 at provider entry,
  final saved registers, SP and interrupt masks.

Five mutation controls reject incorrect length handling, timeout truncation,
initial-value restoration and early status truncation; a sixth control rejects
the old bridges. TX/RX and wait operations remain modeled. Addresses are valid
byte values; raw APSR and other caller-clobbered registers, private saved-word
and padding aliases, arbitrary faults, concurrent access and physical bus/DMA/
IRQ behavior remain outside this proof.

GCC is not covered by the normal ABI validation. Strict qualification is
blocked by the pinned SDK's unused-parameter SVC diagnostics. A probe that
changes only that diagnostic's error severity compiles, but its primary and
secondary provider frames are 56 and 48 bytes instead of 40. Both rejections
are retained; the product warning policy is unchanged.

All 577 R1 units compile with no failures or duplicate strong symbols. The
other 576 objects, manifest and strong symbol sets are unchanged. Imports
remain 164 application and 34 bootloader symbols. The previously unused
legacy TX providers now have a live source consumer. Bootstrap remains
compile-only pending its separate ABI work.

Official generic qualification compiles 15 variants and selects no regions;
all nine strict GCC variants fail on the SDK diagnostics. The source plan is
unchanged. The canonical hybrid retains locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,035 source-built bytes, 642,125 retained executable bytes and 248
resource bytes. Source-built totals include assembly/data. Complete source
firmware and read-adapter byte identity remain unproven.

The [machine-readable receipt](twi-read-c-review.json) records REA, execution,
controls, compiler limits, qualification and audits. Probes are under
`build/goal-r1-twi-read-c/`.

The subsequent [shared SP observation review](native-stack-c-review.md) centralizes read-only SP capture and removes the unsafe GCC output form. Normal Clang objects remain identical; this does not close the GCC consumer frame gap.

The subsequent [register-write C review](twi-register-write-c-review.md) replaces both register-write bridges while preserving the length-80 overlap. Read function bytes and relocations are unchanged. The actual bulk packet/register/legacy-TX C chain passes 9,000 comparisons at native SDK depth 136.
