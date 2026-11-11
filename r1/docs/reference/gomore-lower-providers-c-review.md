# R1 runtime validation and ordered output copy in C

`native_gomore_lower_providers.c` implements validation `0x967c8` (76 bytes)
and output copy `0x59d9c` (192 bytes). The [receipt](gomore-lower-providers-c-review.json)
binds REA bytes/pseudocode, compiled objects, native/C/oracle replay, startup
proofs, qualification and composition. No inline assembly is added.

Validation preserves the native precedence: the version-dependent timestamp
check can produce -1006, absent context without force returns -1, and signed
UTC-offset mismatch overrides the earlier status with -1008. A forced null
context is still dereferenced rather than guarded. The stock version predicate
at `0x72ace` is **literally a zero-return leaf**. Production reuses the existing
`gomore_primitives_return_zero` C implementation. The direct fixture executes
that leaf for **1,307 validation cases**; **1,334 nonzero predicate overrides**
are explicitly counterfactual tests of the retained unreachable timestamp branch,
not claims that the shipped predicate returns nonzero.

Output copy captures the context pointer once and performs the native sequence
of float-bit, word, halfword and byte transfers. It does not snapshot the source
or widen small stores. Overlapping source/destination ranges therefore retain
native read-after-write behavior, even when the destination overwrites the
global context pointer. Floating loads/stores preserve raw NaN/zero bits and
FPSCR. The function's void R0 is excluded; caller-clobbered state is not an ABI
result contract.

The observed sensor-workspace owner expands from **52 to 172 bytes** before
integrating output writes through packet byte 167 and the lifecycle's observed
read at byte 168. Existing input/sample offsets are unchanged. The added tail
represents the observed output prefix, not a claim that the entire native
workspace has been reconstructed. A separate 12-byte runtime configuration at
`0x20007c50` starts with UTC offset -1. Native startup RW/ZI handlers plus an
independent decoder match **184 workspace/configuration bytes**, a net addition
of 132 bytes. The expanded owner's instruction/relocation sections are unchanged.

**3,253 direct native/C/oracle cases** pass: 2,641 validation and 612 copy cases,
including **1,129 expected faults**. Coverage includes force/context combinations,
error precedence, timestamp/cutoff boundaries, signed offsets, callback mutations,
partial writes, raw FP encodings, unaligned addresses in the emulator's normal
access mode and overlapping/global-pointer destinations. Nine compiled defects
are rejected, including widened stores, cached bytes and reloading the captured
copy context.

Integration passes another **864 sensor-update cases** and **512 actual idle
callback cases** with C validation and copying executing as real callees. Final
memory/results are independently checked, and complete native/C traces match.
Lower host-input, logging, clock/health and reinitialization remain modeled.
The reused zero/no-op C bodies are isolated for fixtures because the production
vendor object has monolithic text; their instruction bytes are checked against
that production object. No production duplicate is introduced.

All **678 units** compile with no duplicate strong symbols. All **677 prior
source files** are unchanged; **676 prior objects** are unchanged. Only the
existing workspace owner's storage grows. Application imports fall from 167 to
**165**, bootloader imports remain **34**, and no new native import is exposed.
Host-input update, logging, output lifecycle and context initialization remain
source reconstruction dependencies.

Both new functions fail instruction qualification. The canonical plan remains
**4,369 source-built bytes**; the fresh hybrid matches the locked application
through executable pull-through. Full source-only linking, whole-image placement,
byte identity, physical alignment traps, first-use FP and concurrent/physical
hardware operation remain unproven.

The subsequent [host-input review](gomore-host-input-c-review.md) replaces the
modeled host boundary with a direct C candidate. Its direct replay is separate
from this historical integration fixture; the caller stack-layout difference
remains open.
