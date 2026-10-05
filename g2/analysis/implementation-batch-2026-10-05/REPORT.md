# Implemented foundation components — October 5

The user explicitly authorized this bounded implementation using the shortcut
findings. It adds a reusable C touch-wrapper component and a local-resource
preservation pipeline. It does not declare the whole-image pseudocode freeze or
source-build gates passed; shared campaign state and official providers stay
unchanged. No commit, flashing, staging or deployment command was issued.

## Source and build integration

`g2/components/foundation/touch_scb/touch_scb.c` and `.h` implement the verified
RX status mask (`0x1ff`), count clamp, single downstream callback (including
zero count) and returned actual count. The checked adapter adds explicit pointer,
callback, byte/halfword width and capacity errors without changing the faithful
unchecked API. These are newly reconstructed callback interfaces, not copied
Infineon implementation or a complete target SCB driver.

`make -C g2 foundation-object` builds an actual Cortex-M0+ freestanding object
using clang. `foundation-test` and the existing `core-test` register both new
test modules. No target linker/startup/IRQ/provider integration is added. A real
hardware provider must still implement FIFO behavior, match the supplied element
width to device configuration, and serialize status/read/configuration changes;
capacity checks alone cannot enforce those hardware contracts.

`g2/tools/preserve_l8_resources.py` plus a hash-pinned resource map implement
optional `resource-export`, `resource-verify` and `resource-repack` Make targets.
Six proven descriptor/pixel identities become exact raw L8 and standalone PGM
files with provenance. The tool rejects missing/tampered private input, malformed
geometry/pointers/overlap, altered pixels/PGM, and existing outputs. Repack requires
the original payload template, reconstructs it exactly and never overwrites it.
No official provider is silently substituted. PGM is an inspection format,
not the target firmware encoding; only original pixel bytes are accepted.

The actual optional Make path exported/verified/repacked six assets containing
28,872 unique pixel bytes. The output equals all 3,523,396 original Apollo payload
bytes and hashes to `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
That equality proves lossless resource preservation with the original template,
not a source-generated firmware image. Raw vendor data stays in ignored build
output; root MIT does not grant its redistribution rights.

## Validation and review

Final foundation checks: **9 tests passed**, including host C compilation,
freestanding ARMv6-M object compilation and resource roundtrip/rejection cases.
Existing packaging checks: **7 tests passed**. Eight actual original-wrapper
emulation cases (six prior plus held-out equality and UINT32_MAX request) have
119 byte-checked trace events; C results match them. The FIFO callee is intercepted
at entry, so no hardware register/data-transfer, interrupt, concurrency or timing
claim follows. Original FWPK wrapper offset conversion remains explicit: function
runtime `0x9250`, decoded offset `0x5F50`, official payload offset `0x5F70`.

Independent code review found no critical defect. The host-pointer narrowing and
undersized test dummy were corrected before final validation. Export has a
documented recoverability edge: filesystem failure during transfer can leave a
partial newly-created output directory; verification rejects it and a retry
requires a new destination. Existing output is preserved. The checked adapter
reads status before rejecting inadequate capacity, so a device provider must
account for status-read effects.

The final aggregate rerun completed all **25 core modules**: **165 test-method
invocations, 159 passed, 0 failed, 0 errors, 6 skipped methods**, plus **1 class-setup
skip** outside that method count. There are **0 unrun modules**. This is a passing
aggregate with explicit skips, not validation of the skipped functionality.

The earlier image-generator failures were resolved by initializing only official
MIT-licensed LVGL at the unchanged gitlink
`344c7c318047b7348e1be8572a9fd4260c251cfa`. All six affected image-generator methods,
including seven format subtests and the bitfield-layout compile probe, now pass.
No unrelated submodule was initialized and no tests were changed to pass.

The previous font interruption was an unbounded npm registry lookup, not a font
assertion. Bounded npm settings (5-second fetch timeout, zero retries) return
`ENOTFOUND registry.npmjs.org`; the existing font end-to-end skip remains. Two
negative font tests pass on that earlier dependency error, so their intended
local branches are not independently verified. Other existing skips cover four
reviewed-CFW-image audits, a missing authenticated corpus class and unavailable
protoc. Exact final outcomes are in `aggregate-validation.json`, previous failures
in `aggregate-validation-before-lvgl.json`, and source/license/access checks in
`dependency-validation.json`. No alternative registry, denied-route bypass,
license acceptance or permission change was used.

`validation.json` records commands/results/limits, `source-manifest.json` hashes
the implemented files, and `review.json`/`review.md` preserve the independent
review. Packer, reference manifest, workflow state and original payload hashes
were checked unchanged. Concurrent staged work was preserved without alteration.

The next implementation dependency is a verified target FIFO provider and its
configuration/lifetime contracts, followed by explicit firmware linker integration
when appropriate. Whole-payload source reconstruction, original compiler byte
matching, other image formats and absent external NOR resources remain open.
