# R1 Goodix sensor-stream provider and registration in C

`application/goodix/native_stream_provider.c` implements the three operations
named by the stock provider table at `0x9a59c`, plus the sensor task's previously
unresolved `r1_native_stream_register` call. The operation table contains real C
function pointers, not addresses into retained executable code. A shared header
declares the preceding callback module. The new four-byte polling timestamp
owner at `0x20006d80` matches authenticated RW startup data.

The provider preserves these stock behaviors:

- Open (`0x8165c`) tests the full incoming context for zero before truncating to
  a byte. Low selectors 0..4 retain the repeated, short-circuit log-mode queries.
  Selector-specific cache clears precede reference-counted acquisition; the
  acquisition return propagates. A nonzero context `0x100` still invokes mode zero.
- Close (`0x815c0`) similarly tests the full context, then passes its low byte to
  the existing reference-counted release provider and returns its result.
- Read (`0x81744`) returns immediately for a null destination but otherwise
  samples the clock and performs the native absolute comparison
  `now >= previous + 500 || previous == 0`, with 32-bit wrapping addition.
  An elapsed-time subtraction would change wraparound behavior. Refresh clears
  the raw-HR and ADT arrays, opens I2C, processes interrupts, closes I2C and only
  then writes the originally sampled timestamp.
- Read preserves the native fixed formats: HR 4, SpO2 6, wear 2, HRV/aging 10,
  raw HR 124, ADT 24 and gain/gray 12 bytes. It ignores the supplied length.
  The HR word uses the native unsigned 41..219 test. Wear requires ready byte
  exactly one and clears it before reading the output halfword. All descriptor
  field copies retain interleaved volatile access for overlapping destinations.
  Raw and ADT bulk copies use the already reconstructed native **memory-move**
  boundary at `0x2775c`, preserving overlap rather than substituting memcpy.

Registration (`0x89eec`, called from sensor task `0x925a4`) initializes Goodix,
clears the 240-byte cache, installs the eight actual C result callbacks, then
creates/enables `hr`, `spo2`, `raw_hr`, `wear`, `gray`, `aging`, `hrv` and `adt`
objects with their native sizes and contexts. Failed creations do not stop later
registrations; the last flag-set return is retained. The eight callback setters
and the actual C object flag setter execute in the probes. The read operation's
C function-pointer type matches the existing generic sensor-operation interface.

Five sensor-task declarations now match their C definitions: motion interrupt,
stream initialization/registration and the two singleton constructors. Their
instruction object remains byte-for-byte unchanged. Memory primitive declarations
also use their actual pointer/size types; volatile views remain local to the
adapter's field accesses.

REA/Ghidra observes the read routine as 262 instruction bytes across a 272-byte
envelope, excluding its ten-byte jump table. Its default analysis lacks the
sampled open and registration entries; those errors are retained without
coverage credit. Direct Thumb disassembly and locked raw-image execution supply
the local oracle. The close entry has an independent stock function-pointer
anchor in the provider table and a supplemental frontier row. These observations
do not establish whole-corpus coverage.

## Execution evidence and limits

The final normal C object passes 4,088 paired stock/C emulator cases: 280 open,
280 close, 3,424 read, 32 registration and 72 complete registration-then-read runs.
The last group dispatches interrupts through the actual installed result callback
slots, then executes the C output formats. Callback-slot and provider-table words
are checked against actual native/source function symbols before address
normalization. Cases cover log-mode short circuits, whole-word/low-byte contexts,
acquire/release return values, the 500-tick equality and overflow cases, ignored
length, unaligned and aliased outputs, HR bounds, wear readiness, failed object
creation, ordered shared reads/writes, memory guards, R0, return SP, saved registers
and interrupt masks. Each invocation starts with clean XPSR/IT state. Two negative
controls (elapsed-time refresh and a new zero-length guard) are rejected.

Goodix initialization, acquisition/release, clock, I2C calls, interrupt dispatcher,
clear/move primitives, object creation and logging are modeled in this component
probe. The dispatcher invokes actual reconstructed callbacks, and actual C setters
and object flag updates execute. The full Goodix interrupt algorithm, actual
transport, allocation/constructor implementation, physical sensor output,
concurrency and arbitrary corrupt pointers are not exercised here. Private frames
and caller-clobbered register/flag outcomes are excluded.

The timestamp startup check executes native RW/ZI handlers, verifies scatter-table
identity and guards, and cross-checks an independent RW decoder. The new source
owner matches four native zero bytes with the expected alignment, writable section
and no owner relocations. It does not establish full firmware startup placement.

All 575 R1 units compile (501 application, 74 bootloader) without failures or
duplicate strong symbols. Application imports decrease from 176 to 175 by resolving
`r1_native_stream_register`; bootloader imports remain 34, with no added imports.
Only one manifest unit is added, and every prior object retains its hash. Five
qualification profiles compile, but no new region qualifies. The source plan
remains unchanged. A fresh hybrid still equals the complete locked 646,408-byte
application: 3,881 source-built bytes, 642,279 binary pull-through bytes and 248
resource bytes. These are stored-byte provenance counts, not executable-C
coverage, admission of these routines into the hybrid or full source completeness.
The build summary's stale P2 label was replaced by a reference to the authoritative
G2 state file; no G2 source or workflow gate changed.

Hashes and current build paths are in
[goodix-stream-provider-c-review.json](goodix-stream-provider-c-review.json).
