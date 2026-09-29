# Methodology

Both devices are reconstructed the same way. The rule is that every claim is
backed by an artifact a reader can re-derive. A claim without such backing is
recorded as an open question, not filled with a plausible guess.

## The goal and its three separate proofs

For each device, the goal is C source that the original toolchain compiles and
links into images byte-identical to the locked official artifacts:

- G2: EVENOTA `s200_v2.2.6.10`, see [`../g2/workflow/target.json`](../g2/workflow/target.json).
- R1: application `2.2.6.0009`, its bootloader and UICR, see
  [`../r1/blobs/official/2.2.6.0009/PROVENANCE.md`](../r1/blobs/official/2.2.6.0009/PROVENANCE.md).

Three proofs are kept apart:

1. **Pseudocode coverage.** Every executable byte of every payload has
   reviewed pseudocode, and every non-code byte is accounted for.
2. **Source completeness.** Every byte comes from C, assembly, or a data
   source generated from a declared asset.
3. **Byte equality.** The rebuilt images and container hash to the locked
   identities.

None of the following counts toward proofs 2 or 3: a retained binary blob, an
opcode array, a stock-byte overlay, a trap, or a "behaviourally equivalent"
rewrite. A retained-byte repack (`make g2-build`) proves only the container
format. Compilable C with different bytes proves neither semantics nor
equality. The phases that lead to all three proofs are in
[`roadmap.md`](roadmap.md). The G2 gates are in
[`../g2/workflow/PROCEDURE.md`](../g2/workflow/PROCEDURE.md).

## Upstream first

No attributable upstream code is re-implemented. The order of preference:

1. **Official upstream source at the exact revision.** It is pinned as a Git
   submodule under `third-party/upstream/`, or as an archive in
   `third-party/fetched/` when no Git repository exists. Identify the version
   by evidence: embedded version strings, source paths, function-level
   matching (FunctionID/BSim), and configuration constants. Record whether the
   pin is exact or the best compatible choice within a proven interval.
2. **Recovered configuration and patches** applied to that upstream (for
   example `lv_conf.h`, `sdk_config.h`, and vendor deltas). These live in the
   device's `config-recovered/`, each with its evidence.
3. **Project-authored C,** only for code with no attributable upstream. It
   must still compile to identical bytes.

Pinning each upstream at its exact commit keeps it updatable. Once a
byte-identical build exists, moving a submodule forward shows exactly what an
upstream fix changes in the firmware.

## Binary-only vendor code

Some vendor code has no public source: GoMore health algorithms, Goodix
algorithm libraries, NemaGFX, Packetcraft/EM link layer, parts of AmbiqSuite.
There are two ways to reach byte identity for it:

- link the vendor's original object archives, where they are legitimately
  available (for example from an SDK download); or
- produce byte-matched C through the same decompile-and-match loop as
  project code.

Both are recorded explicitly per function. Nothing is fabricated where the
evidence runs out.

## Evidence and verification

- Versioned G2/R1 firmware mirrors are tracked with checksums. Other
  local-only inputs remain ignored; tools check required inputs by SHA-256
  before use. See `LICENSE` and `NOTICE` for licensing terms.
- Decompiler output is raw evidence until an independent reviewer accepts
  it. Accepted pseudocode is frozen with a manifest before any C work
  depends on it.
- Similarity scores are candidate signals, not attribution. Attribution needs
  distinctive constants, full semantics, source diagnostics, or corroborating
  call topology.
- Gates fail closed. A mismatch is investigated, never re-pinned away.
- Facts are cited to repository paths or public sources, with a confidence
  level. The consolidated references (`docs/hardware/`, `g2/docs/reference/`,
  `r1/docs/`) carry these citations.
