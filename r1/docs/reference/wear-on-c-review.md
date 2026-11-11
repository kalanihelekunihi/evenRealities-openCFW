# R1 optical and motion wear-on decision in C

The [pure C wear-decision review](wear-decisions-pure-c-review.md) supersedes the remaining assembly boundaries described in this original admission. Both decision units now use the strict GCC C route, with the existing C conversion provider shared by wear-off.

`native_wear_on_decision.c` supplies stock `0x3d268` with C control/state/logging
logic and a small signaling-FP comparison boundary. The
[review receipt](wear-on-c-review.json) binds REA bytes, production hashes,
comparisons, rejected defects, qualification and the locked hybrid.

With an optical stream and nonzero active count, it calls the existing C range
helper. A nonzero previous-history word and unsigned range below 100000 log the
range and return. Otherwise a fresh unchecked last-history word must exceed
`0x8a1790` to set mode 1. Each enabled log path rereads that last word after mode
queries, including when a provider changes active count to zero. Without usable
optical history, axis variances are visited in order and any ordered value above
2000 sets mode 1. NaNs do not trigger the transition at any position. No new RAM
is owned, and the range helper is reused without another implementation.

The first C probe used quiet `VCMP`, losing the invalid-operation FPSCR bit for a
quiet NaN. The target compiler explicitly ignores `FENV_ACCESS`. The final helper
therefore retains `VCMPE` plus an FPSCR read, decoding ordered greater-than in C.
My initial interpretation that the final unordered branch transitions was wrong;
the stock signed BLE returns for unordered comparisons too. The final implementation
and matrix follow that verified behavior. Floating-point context is initialized
before setting FPSCR, as established by the range followup.

Direct verification passes 7,011 paired cases using actual C range, covering optical
threshold/range equality, zero/full-word history, unchecked counts through 255,
changing log modes, provider mutations of active count/history/mode, variance
threshold neighbors, quiet/signaling NaNs at every axis position, infinities,
subnormals, FZ/DN, preset flags, interrupt masks and null statistics arguments.
Another 1,624 pairs execute actual C motion coordination, statistics, on-decision
and range together. Remaining off/clear/multicast/log providers are modeled.
Public state, provider arguments, logical faults and FPSCR are compared, with
preserved registers/SP checked on normal returns and interrupt masks checked.
Void R0, fault PC, caller-clobbered registers, APSR and private stack are excluded.
Six compiled defects are rejected: quiet compare, range equality, optical equality,
missing mode store, wrong structured tag and stale logged history. Physical and
concurrent behavior remain unverified.

All 648 units compile and both relocatable compositions pass without duplicate
strong symbols. All 647 earlier sources and objects are unchanged. The on-decision
import is resolved without new imports, leaving application/bootloader imports at
172/34. Manifest validation passes. The body does not qualify as exact. The source
plan remains at 4,345 source-built bytes; a fresh hybrid matches the locked
application with 641,815 executable pull-through and 248 resource bytes. Complete
source-only linking and byte identity from C remain unfinished.
