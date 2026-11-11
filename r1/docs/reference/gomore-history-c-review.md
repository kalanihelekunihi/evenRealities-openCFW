# R1 packed history shifting and prefix marking in C

`native_gomore_history.c` supplies history shifting at `0x748d4` and its actual
prefix-marker callee at `0x57ce8`, both in ordinary C with no assembly or new RAM
globals. The [review receipt](gomore-history-c-review.json) binds REA stock bytes,
production source/object hashes, direct and combined replays, negative controls,
qualification and normal composition.

The shift takes a signed adjustment in R1. Nonpositive adjustments return the
original workspace pointer without accessing it. Positive adjustments shift the
existing bytes backwards, reload the live payload pointer for each iteration,
zero the inserted prefix, reload/update the count and invoke the marker. The
marker stops at an existing value 2, the signed length boundary, or after 21
nonzero bytes have been changed to 2. Zeros advance the index without increasing
the marked count. Wrapping count/index arithmetic, unchecked aliases and raw R0
returns follow stock; no capacity or pointer policy is invented.

This work corrects a prior consumer proof gap. The earlier consumer fixture
modeled history as a one-argument call, but disassembly shows stock forwards the
computed signed adjustment in R1. The consumer C prototype/call now forwards that
argument explicitly. The strengthened fixture compares both history arguments;
a compiled wrong-adjustment call is rejected. The original consumer receipt is
historical and does not establish this corrected dependency contract. The new
combined fixture executes the actual C consumer, history shift and marker, then
compares payload bytes as well as consumer output and FPSCR against stock.

Validation comprises 1,409 direct history/marker pairs, 1,537 strengthened consumer
pairs, 1,537 actual consumer/history/marker integration pairs, and 1,260 interval
predicate pairs: 5,743 total. Direct cases include zero/positive/negative signed
lengths and shifts, the 20/21/22 marking threshold, zero/marked/negative byte
patterns, logical null faults, payload aliases into workspace fields and wrapping
counts. Five compiled defects are rejected: early prefix stopping, skipping shift
one, missing prefix zeroing, wrong resulting length and wrong consumer adjustment.
The chain models table lookup, extraction, refinement, scoring and clearing;
it does not prove their behavior. R0, RAM, faults, callee-saved registers, SP,
masks and FPSCR are checked. Caller-clobbered registers, APSR and private stack
residue remain outside the comparison. The consumer's previously documented
raw-frame and signaling-comparison assembly boundaries remain.

All 629 units compile and both relocatable compositions succeed without duplicate
strong symbols. Of the previous 628 units, 627 objects remain identical and only
the corrected consumer changes. Application imports drop from 172 to 171;
bootloader imports remain 34. The remaining consumer-native providers are table
lookup `0x684b4`, extraction `0x68354`, refinement `0x81040` and the scoring wrapper
`0x68fbc`. Frontier bindings now include the newly observed prefix-marker entry.
Manifest checks pass. Neither history root passes byte qualification. The exact
source plan remains at 4,299 source-built bytes; a fresh hybrid application
matches the locked artifact, retaining 641,861 executable pull-through bytes and
248 resource bytes. Full source-only linking, hardware and concurrency validation
remain unfinished.

The subsequent [packed timeline reconstruction](gomore-timeline-c-review.md)
supplies extraction and its actual sample read/write helpers, leaving three lower
consumer providers unresolved. It also expands the actual C integration fixture.
