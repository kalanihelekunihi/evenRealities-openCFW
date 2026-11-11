# R1 variadic GoMore logger in C

`native_gomore_log.c` supplies stock `0x823d8` and owns twelve observed
configuration bytes at `0x20007cec`. The [receipt](gomore-log-c-review.json)
binds REA, production source/object, replay, startup, defect controls,
consolidation, qualification and normal composition. No inline assembly is added.

The logger clears 256 bytes before gate checks, uses native low-byte register
shift semantics, loads masks at their native widths, and reloads callback after
formatting. The C frame preserves the message at entry SP minus 292 and variadic
arguments at entry SP minus four. It retains the four-byte adjacent sentinel and
stock CRLF behavior for formatter returns below 248, including lengths 246/247.
Compiler-private saved-register/frame aliases and void R0 are excluded.

The production object passes **4,390 native/C cases**, each with independent gate
and message expectations. This covers masks, wide shift counts, enable/callback
states, truncation boundaries and callback replacement. Formatter/callback are
modeled there; stock clear/strcat execute. Five independently compiled defects
are rejected, including cached callback, missing shift masking, altered sentinel,
changed suffix bound and returning before the unconditional clear.

A separate **72-case replay executes the actual stock formatter** with integers,
strings, pointers, aligned doubles, dynamic width/precision, FP special values
and long literal/truncation cases. Stock clear/strcat also execute; callback is
modeled. Buffer and vararg pointers are compared numerically without normalization.
This validates logger interaction with that formatter, not a fully C formatter
graph or a complete source-only host call chain.

Native RW startup execution and an independent compressed-data decoder agree
that all twelve configuration bytes are zero; surrounding region guards remain
unchanged. The compiled configuration section contains exactly those twelve
zero bytes. The source owner has not entered the qualified image plan.

The former generic log utility is named `gomore_primitives_log_u32_checked`,
including its declaration and callers. Its checked single-u32 behavior remains
unchanged and no longer claims stock entry ownership. The resampler declaration
now correctly gives the logger a void return. That declaration changed its
object, so all **1,072 resampler replay cases** were rerun successfully.

The normal build compiles **684 units** (610 application, 74 bootloader), with
**164 application and 34 bootloader unresolved imports**. All **681 preceding
units outside the generic owner and resampler** retain identical source/object
hashes. The logger import is resolved without new imports. Source checks and
relocatable composition pass without new failures or duplicate strong symbols.

Qualification selects no new replacement and the canonical source plan remains
unchanged. Hybrid raw equality still includes executable stock pull-through.
Physical device execution, complete source-only linking, whole-chain stack/frame
alias equality and byte-identical source reconstruction remain unproven.
Reproduction artifacts are under `build/goal-r1-gomore-log-c/`; the production
report is `build/sources-goal-r1-gomore-log-c/report.json`.

The subsequent [object-representation correction](gomore-log-object-c-review.md)
keeps suffix access within the containing C object without changing any emitted
object bytes, and repeats all 4,462 logger replay cases.
