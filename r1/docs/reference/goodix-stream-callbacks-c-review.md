# R1 Goodix stream result callbacks and callback table in C

`application/goodix/native_stream_callbacks.c` adds 16 native C entry points in
one manifest unit: eight callback setters and eight stream-result sinks. This
reconstructs previously unresolved bodies, rather than adding another copy of
an existing implementation. The new 240-byte result-cache owner is placed at
`0x2001a1bc` and the 32-byte callback-table owner at `0x20007b8c` in the probes.
Final firmware placement remains a separate gate.

The setters at `0x6a2a0..0x6a31b` retain a previous slot for a zero argument and
otherwise store the full callback word and return one. The sinks implement:

- ADT and raw-HR append callbacks (`0x89e30`, `0x8a01c`): bounded five-/30-word
  arrays, byte count reread before increment, and the native unchanged sample
  return when full.
- Gain and gray triples (`0x89e50`, `0x89e8c`): all three potentially unaligned
  input words are read before any output write; negative signed words clamp to
  zero. Outputs are cache +204/+192, and R0 returns the cache address.
- Four-word HR and six-word aging descriptors (`0x89ec8`, `0x89ed8`): ordered
  full-word copies including fifth/sixth AAPCS stack arguments; R0 retains the
  first argument.
- Six-word SpO2 descriptor (`0x8a03c`): its fourth word and R0 are the sign extension
  of argument four's low byte, preserving e.g. `0x80 -> 0xffffff80`.
- Wear/living update (`0x8a054`): low data byte at +189 precedes the ready byte
  at +188; return value is one.

REA/Ghidra confirms the gain, HR and SpO2 bodies. Its default database lacks the
sampled setter entry `0x6a2e0`; that error is retained without coverage credit.
Direct Thumb disassembly and execution of the locked application provide the
local oracle for all 16 entries. These observations do not establish corpus
coverage or whole-source readiness.

The normal C object passes 9,096 paired stock/C emulator cases without function
stubs. They compare byte/word access order and values, returned R0, saved
registers, successful-return SP, interrupt masks and memory guards. Cases include
null callback installation, full/out-of-range counters, signed extremes,
unaligned and cache-aliased triple inputs, all four descriptor arguments plus
two stack arguments, signed byte boundaries and null input faults. XPSR/IT state
resets before each invocation. Two negative controls (unsigned SpO2 status and
an off-by-one raw-HR capacity test) are rejected. Caller argument-stack overlap
with cache, asynchronous mutation, private frames and caller-clobbered registers/
flags remain outside the evidence.

A separate check executes the locked RW decompressor and ZI clearer, validates
the authenticated scatter-table entries and whole-region guards, and compares
an independent RW decoder. Both source owners match the 272 native zero bytes:
the callback table lies in expanded RW, while the cache lies in ZI. Source-object
sizes, alignment, writable/non-executable sections and absence of owner relocations
are checked. This does not prove execution of complete firmware startup.

All 574 R1 units compile (500 application, 74 bootloader), with no failures or
duplicate strong symbols. Imports remain 176 application and 34 bootloader.
Every prior object retains its hash; only one manifest unit is added and the
remaining manifest semantics are unchanged. Five official qualification profiles
compile, but no region qualifies. The source plan remains unchanged, and a fresh
hybrid application still equals locked stock: 646,408 total bytes, with 3,881
source-built, 642,279 binary pull-through and 248 resource bytes. These are
stored-byte provenance counts, not executable-C coverage or admission of this
new C into the hybrid. Source completeness remains false.

## Registration follow-up

The [subsequent provider and registration review](goodix-stream-provider-c-review.md)
implements this boundary. The paragraph below records this review's earlier build.

The sensor task's call at `0x925a4` resolves the outstanding
`r1_native_stream_register` boundary to stock `0x89eec`. That routine initializes
Goodix, clears this cache, installs these eight result callbacks, then creates
and enables eight stream objects. Its provider table at `0x9a59c` names three
additional provider operations that require their own review. This turn does not
invent those operations or mark registration complete. The callback/context
module supplies concrete dependencies for that remaining hardware path; complete
registration, stream operations and physical sensor results are still unproven.
No G2 implementation or workflow gate changed.

See [goodix-stream-callbacks-c-review.json](goodix-stream-callbacks-c-review.json)
for current hashes, startup receipts, test paths and qualification results.
