# Generated hardware-unit qualification inputs

`qualify_sources.py` now compiles generated manifest units from their real
`build/generated/<device>/…` paths. It first matches frontier anchors against
the original `{gen}/…` identity, then retains that identity as `manifest_source`
in qualification records, compilation-unit records and selected-plan metadata.
The production firmware builder already regenerates these inputs before
compiling selected providers; that behavior is unchanged.

Previously, the generated FAL owner failed before preprocessing because the
qualifier tried to open a literal repository path containing `{gen}`. The
normal source build compiled it successfully, so this was a qualification
input-path failure rather than a C or hardware-policy failure.

[Machine-readable evidence](generated-qualification-review.json) records an
actual before/after run using the same native read-adapter and generated FAL
units across five optimization profiles each:

- Before: 5 of 10 attempts compiled; all five generated-input attempts failed.
- After: all 10 compiled. Frontier anchors and compiler flags are identical.
  The five ordinary-unit object hashes remain unchanged.
- Generated compilation receipts include the materialized C file and native
  partition header dependencies, and unit/result records preserve the manifest
  identity. Temporarily moving the generated file aside and rerunning candidate
  preparation recreated identical content; the original was preserved.

No region passes byte qualification in this fixture set. Matching, linking,
byte-equality checks and canonical-plan admission rules are unchanged. The
canonical plan remains at 3,881 source-built application bytes, 642,279 binary
pull-through bytes and 248 resource bytes. A fresh R1 hybrid equals locked
stock and still reports source completeness false. Python compilation,
`make sources-check` and whitespace checks pass.

No firmware C or manifest changes are part of this repair. It enables generated
hardware candidates to reach qualification; it does not prove source
completeness, hardware behavior or any new instruction match. No G2 workflow
gate advances, and the overall goal remains active.

Follow-up: the [write-frame review](flash-write-frame-review.md) exercises an actually selected generated GCC provider through the production firmware builder. Manifest GCC-wrapper candidates now retain their compiler path and SHA-256, which the builder requires. All four compared qualification objects remain unchanged.
