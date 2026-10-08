# Startup event family B: SPOT state/power callback

The selected callback is installed at table `0x20026e38 + 4` as Thumb pointer
`0x42ba01` for revision 34 / trim 2 and revision 35 / trim 1. Its stock body is
`[0x42ba00, 0x42bd8c)`, 908 bytes, SHA-256
`1a5659a51222d91d03686766dd6caf89fcb4a813088e80095f61d554cc575450`. The
locked image SHA-256 is
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

The callback contract is `(uint8_t stimulus, uint8_t on, uint32_t *args)` in r0,
r1, and r2. Ghidra supplies the fixed stock signature; the public Apollo510 SPOT
header corroborates stimulus, boolean, and argument-pointer roles. The callback
checks clock readiness at `0x40021108` and profile marker at `0x20026ba0`, then
saves/restores interrupt state while applying SPOT state and power updates.

## Verified descendants

`children_native.c` now contains source reconstructions for four lower leaves.
Their locked extents and hashes are:

- Temperature range `0x42ad40..0x42adb8`, 120 bytes, SHA-256
  `89f71050cf7850205a7a5ef9ccfb09dfadaadd5a6046355844d800589b65607d`.
- State transition effect `0x42b014..0x42b068`, 84 bytes, SHA-256
  `b3da01a94a3c08eb7eb0d7d344b6760d929296878e2dfbf9c4770373aedd3d88`.
- Buck/deep-sleep scan `0x42aef0..0x42b010`, 288 bytes, SHA-256
  `7a54959ea8247c505df0f3139ce607b4d1fabb5d0015054b89bd44b5d79cc31b`.
- State decoder `0x42b6b8..0x42b9ba`, 770 bytes, SHA-256
  `74f4304f6e3aa59022a29eb5e5f5479c77072b33355825b7c9409897001bb9d1`.

`child-comparison-decoder.json` records 4,834 source-only-versus-original
instruction fixtures. All tests pass. Temperature, transition-effect, and
scanner tests visit all 492 bytes. The scanner reads the fifth input byte at
`+16`, checks the stock words at `0x400204d8`, `0x40008800`, and the active
bitmap `0x40008010`, and iterates all 16 channel words at
`0x40008200 + i*0x20`. It preserves the four-word input and updates result
byte `0x200271c0`. Its predicate `0x41f3f0..0x41f424` is independently
authenticated and compared in the SPOT-handler suite; its 52-byte extent/hash
is recorded in the scanner receipt. The direct harness rejects both one-byte-
short and one-byte-long extent digests for each leaf and the predicate.

Decoder tests visit 740/770 bytes; the exact 30 unvisited
addresses are in that JSON. The remaining gaps cover the special major-code
16–19 cases and unmatched secondary-code error returns. The major decoder first
masks values with literal `0x00f00fff`, which removes the bits needed by the
special 16–19 comparisons; the secondary default requires an unmatched encoded
value, while accepted major encodings and the following masks bound its state
fields to the listed cases. These bytes remain explicitly unvisited in the
receipt rather than being counted as covered.

The decoder input window and outputs are grounded from the original callback
instructions and checked by `verify_evidence.py`. The caller allocates 32 local
bytes and calls `0x42b6b8` with r0=`sp+4`, r1=`sp`, and r2=`sp+24`. The child
reads:

- input `+16` / caller `sp+20`: temperature category copied from `0x200271ba`;
- input `+17` / caller `sp+21`: state byte copied from `0x200271bb` or the
  requested transition;
- input `+18` / caller `sp+22`: auxiliary category computed by the wrapper, or
  read from the argument for SYSTEM stimulus.

The decoder also reads configuration word `0x434164` (zero in the locked image),
MMIO word `0x40021000`, and mode byte `0x2002708c`. Standalone vectors seed those
inputs explicitly, including alternate config words for branch exploration;
they do not claim those alternate values occur on hardware. The source wrapper
passes a 19-byte aligned structure with the same offsets. A comparison fixture
observed the stock `+16..+18` bytes as `00 01 00` for the state-0-to-1 case,
matching the disassembly’s local stores and the source buffer.

`comparison-native-decoder.json` is the integrated callback comparison with
the four verified descendants. It passes 44/44 fixtures and visits 798/908
callback bytes. Scanner fixtures cover the fast gates, predicate modes, every
channel slot, active/inactive channels, and category boundaries. The stock
callback executes original scanner and predicate instructions; the source
callback runs only the compiled C reconstruction. `comparison-wrapper-cuts-current.json`
records the same 44 fixtures while keeping all child calls cut; it passes and
visits 886/908 bytes. Earlier receipts are preserved in `comparison.json`,
`comparison-wrapper-cuts.json`, and `child-comparison.json`.

The current callback harness also integrates the native transition:
`comparison-native-transition.json` passes 44/44 fixtures, with the stock side
executing the original transition and the source side calling compiled native
code. Its transition record includes the four stock arguments and returned
minor value. The older decoder-only and all-cut receipts remain intact.

`transition-comparison-corrected.json` separately executes the 1,032-byte transition
against the compiled implementation for 30 targeted cases. Its initial receipt
had one incorrect low-trim destination, corrected after a separate 51-case
counterexample showed that the stock routine stores this field at `0x200270ac`
(not `0x200270a4`). The current implementation and tests use the grounded stock
address. The original `transition-comparison.json` is retained as the pre-fix
receipt; `transition-comparison-corrected.json` is authoritative. The evidence
verifier no longer attributes this Apollo510 SRAM table to the NationalChip
GX8002. All results,
ordered MMIO writes, seeded profile/rank state, and ROM-wait cycle inputs match;
858 transition bytes were visited. The exact 174 unvisited addresses remain in
that receipt. The ten nested routines are mapped to the existing clock manager
and source-native trim helpers. Stock clock status returns are ignored by the
caller; the source runs the reconstructed clock manager. Address `0x40` is the
observed void ROM cycle-wait service; both delay conversion paths execute and
their cycle counts are compared.

## Remaining frontier and validation

The callback's direct child closure now executes natively, with this bounded
coverage frontier:

- State transition `0x42b294..0x42b69c`, 1032 bytes, SHA-256
  `0393f03222d8b7e8c67ed0e7ffbba640f8030dac259a909ec7dbb20846325c2b`; calls
  `0x41cc48`, `0x41cc92`, `0x41ccd6`, `0x41d1c0`, `0x41e1e8`, `0x41e22e`,
  `0x42adb8`, `0x42ae24`, `0x42ae6c`, and `0x42b06c`. Their behavior is
  exercised through the transition fixtures; transition-byte gaps remain
  explicit and are not counted as covered.

Run `make verify` in this directory. It authenticates the locked image, exact
callback and descendant extents/hashes, literal pool, revision routing, the
832-case runtime route comparison, the decoder stack contract, and direct
transition extent checks. The source machine runs only compiled
C/provider/critical-save ELF code; it never loads locked executable bytes. The
stock machine runs the actual locked callback and descendant bodies; the
transition child is no longer intercepted. The source ELF uses Cortex-M33 baseline instructions for
the configured Unicorn model; Apollo510 is Cortex-M55 and accepts that subset.
No hardware behavior, full callback closure, complete firmware source, or
byte-identical rebuild is claimed.
