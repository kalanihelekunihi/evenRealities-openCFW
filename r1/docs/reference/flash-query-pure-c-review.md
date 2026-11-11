# FlashDB count-query C adapter

`r1/src/application/runtime/native_flashdb_query_count.c` replaces the
handwritten assembly entry at stock 0x63cb4 with an ordinary four-argument C
function. Its eight-byte context is fully initialized: the requested status is
truncated to one byte and the count starts at zero. There is no incoming stack
seed to retain. The canonical counter callback now has the iterator's bool
function type; it still returns full R0=0. There is no incompatible callback
cast, second implementation or new assembly wrapper.

The initialized path forwards the signed time bounds, callback and context to
the existing iterator, then returns the context count. Any nonzero initialized
byte is accepted. The uninitialized path emits the same three diagnostics,
including the newline, and returns zero. The path helper retains whole-byte
file-mode handling and wrapping partition-plus-four arithmetic; live database
name loads remain ordered around diagnostics.

Fresh REA bytes from 0x63cb4 cover code, literals and diagnostic strings and
match the preserved raw application. The focused normal-object probe passes
**1740 paired cases (3480 executions)**: 360 query cases, 1280 counter cases
and 100 path cases. The callback tests retain unaligned and aliased status/count
accesses and unsigned count wrap. The query tests execute the actual C counter
and path with a modeled iterator and printf.

A second probe links the actual iterator and traversal leaves. It passes
**2016 paired cases (4032 executions)** across signed forward/reverse bounds,
status values and initialization states. Half exercise actual iterator traversal;
half exercise the uninitialized query path. A separate count oracle checks
inclusive time bounds and nonempty matching records. Sector/TSL read providers
supply a single closed sector with fully populated metadata and an erased tail
sentinel; printf and lock callbacks are modeled. Lower-read and lock traces match,
and source execution is prohibited from entering stock instruction addresses.
This is not a physical flash or partial-read proof for the whole iterator.

Five compiled defect controls are detected: nonzero initial count, incorrect
requested status, checking only initialized bit zero, reversing the time bounds
and stopping iteration after the first callback. The final build compiles all
**800 units (718 application, 82 bootloader)** without failures or duplicate
strong symbols. Imports remain 96 application and 22 bootloader linker metadata.
All 797 other nongenerated object hashes are unchanged. Generated boot objects
retain identical allocated bytes and relocations. The canonical path and counter
helper bodies remain byte-identical despite the callback type correction.
Strict GNU bootloader linking and the R1 manifest check pass. The global source
check retains the unrelated unlisted G2 `resident_rom_thumb_set.S` file.
No source-plan selections are changed.

Private frame addresses and saved incidental R1/R2/R3 outputs are excluded.
The four repository assembly callers consume the count through R0, then call
no-argument offline-queue predicates; those predicates read their queue owners.
No arbitrary frame alias, fault, concurrency, asynchronous callback or whole
application final-link claim is made. The iterator itself still contains
assembly. Exact artifact and probe hashes are recorded in
[flash-query-pure-c-review.json](flash-query-pure-c-review.json).
