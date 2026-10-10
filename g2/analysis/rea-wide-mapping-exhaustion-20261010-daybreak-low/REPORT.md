# REA wide-mapping and snapshot exhaustion, 2026-10-10

Status: bounded private P2 result. A whole-payload authenticated mapping does
overcome the earlier narrow-view empty-callee limitation and makes REA useful
for pseudocode, direct call edges, incoming xrefs, string recovery, CFG, and
low-confidence ABI hypotheses. It does not add an independent ISA or execution
oracle, prove indirect targets, or make decompiler types suitable for canonical
admission without the existing original-byte validation workflow.

## Scope and preservation

This pass used the existing private analysis ELF at
`../shortcut-arm-tools-20261009-agent3/main-analysis-only.elf`. Its loadable
`.text` maps all 3,523,396 original Apollo-main bytes at `0x00437fe0`; the ELF
SHA-256 is
`36c9b79de3b961d36ad343a1402a112298603111cbe1d5875e1b471694159d1a`.
The producing probe already verifies the mapped bytes against official payload
SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
The authored ELF section and one Thumb symbol are analysis metadata, not stock
ELF provenance or a claim that every mapped byte is executable.

REA used provider `ghidra` 12.1.4 in its documented
`ephemeral-source-immutable` mode. No shared Ghidra project, installed
processor, canonical coverage ledger, firmware source, authenticated input,
or workflow state was edited. The only retained REA state is the private
snapshot in this directory. `g2/workflow/state.json` remained
`P2_EXECUTING`; G2 through G6 remained `not_run`.

## What the wider mapping changed

The earlier bounded FlashDB REA view contained 482 bytes of function text and
reported two procedures. The whole-payload mapping reported 7,341 procedures
and 17,010 strings across the mapped 3,523,396-byte segment. This is a material
tool result: direct branch destinations and literal/string targets that fell
outside the narrow ELF are now present in the provider database.

For `0x0054116e` (`SVC_FlashDBBlobRead` by embedded source string), REA now
returned:

- useful pseudocode with four register arguments, `param_1 & 0xff`,
  `param_4 & 0xffff`, the `0x8ac` table stride, and the call to `0x0054454a`;
- five resolved callees: `0x0043ce9e`, `0x0043d0ce`, `0x0043d574`,
  `0x004490cc`, and `0x0054454a`;
- nine direct incoming call xrefs at `0x004d9578`, `0x004d965e`,
  `0x004d981c`, `0x004d9956`, `0x004d99e8`, `0x005105fc`,
  `0x005106ae`, `0x00510852`, and `0x00510948`; and
- embedded module, file, function, and failure-format strings that were numeric
  literals in the narrow view.

Evidence IDs are `ev_faa3d102516cc14393c9e6bb657cc9c2c945e4be17c8f0ba9c664eb344b82fba`
for the complete function dossier,
`ev_c186e1d98a2f3e5d6f4efcd2c2cedd04e452716e66f3808d9140904475b04caf`
for direct callees, and
`ev_95dd59e78735de8bac856ad41416ae0d0b93c9051025c5c8fa3b25bb16251ace`
for name xrefs.

The same mapping produced useful pseudocode for the existing bounded TLSF
targets `0x004cff6c`, `0x004cff9a`, `0x004cffc2`, and `0x004d0524`. It retained
the instruction-validated geometry: 32 second-level bins, 24 first-level rows,
second-level bitmap base `+0x14`, free-list base `+0x74`, row stride `0x80`,
and the assertion call at `0x004d09b4`. For `0x004cffc2`, resolved callees are
`0x004cfd56` and `0x004d09b4`. Batch pseudocode evidence is
`ev_a51e3f62593b9c2774786b517a3aa2e9b11f04b4e46184d9283cb291cf4a46e5`.

These are useful presentation and review accelerators. The facts above remain
accepted here only where they agree with the retained GNU force-Thumb listings
and original-byte Unicorn results in the two predecessor analysis directories.

## ABI value and limits

REA's function dossiers expose parameter storage, calling convention, CFG,
high p-code, call edges, and memory effects. They are useful for proposing C
interfaces. For example, the TLSF initializer is shown as one r0 parameter and
void return; search is shown as control pointer plus two index pointers; and
the FlashDB wrapper is shown with four register arguments. The wrapper's
downstream body at `0x0054454a` also exposes two indirect callbacks from object
offsets `+0x1c` and `+0x20` and the lower call interface into `0x005444f4`.

The decompiler labels its recovered signatures and calling convention as
low-confidence/default-source observations. One concrete warning is its
`undefined8` presentation for `0x0054454a`, which conflicts with the directly
observed r0 return consumed by the caller and illustrates why REA types cannot
be promoted without instruction and caller checks. Targetless indirect calls
remain unresolved by design.

## Snapshot replay and stopping boundary

The private snapshot is 2,557,175 bytes, SHA-256
`5f72b041765e7725737f4c03326b46e61a2c67aeba10518af8d875b71ec34688`,
and contains 11 evidence records, five primitive bindings, and three workflow
bindings. Reopening the exact ELF with that snapshot reproduced the same
callee and xref evidence IDs and returned the same pseudocode for
`0x0054116e` and `0x004cffc2`. This proves exact-target snapshot reuse for this
profile; it does not turn cached decompiler output into independent evidence.

The useful REA-specific branch is exhausted for the currently available
Apollo mapping: wider authenticated mappings solve missing direct context, and
snapshots make those queries reusable. Further REA queries can accelerate a
named P2 review, but generic whole-image querying will only restate Ghidra's
default analysis. New semantic confidence requires original-byte decoding or
execution, a validated source comparator, first-party types, an independently
reviewed P2 record, or a genuinely new authenticated artifact. No canonical
admission or gate change is claimed.

