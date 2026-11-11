# Newlib reentrant allocation on the canonical native heap

`runtime/newlib_heap_adapter.c` supplies _malloc_r, _free_r, _calloc_r and
_realloc_r as ordinary C adapters to the existing participating native
pvPortMalloc/vPortFree implementation. This closes the two current formatter
imports _malloc_r and _free_r; the other APIs support the same ownership
contract for subsequent source integration. No second heap or allocator
implementation is introduced, and ordinary native allocations keep their
existing layout.

Only allocations made through these newlib APIs carry a private, maximally
aligned size header. Reallocation copies the smaller of the recorded old
size and the requested new size, then frees the old allocation. Equal-size
reallocation keeps the pointer. Zero-size allocation returns NULL; realloc to
zero frees its old block. Calloc checks multiplication overflow and clears
exactly the requested product. Arithmetic-invalid requests return NULL and
set ENOMEM when a reentrant context is supplied. Null free and null reentrant
contexts are supported. These APIs accept their own live allocations; mixing
raw pvPortMalloc pointers into _free_r/_realloc_r or freeing their shifted
user pointers through vPortFree is outside the contract.

The canonical native heap has a fatal ordinary-exhaustion policy, which this
adapter retains. It is not a recoverable malloc implementation on that path.
The tests observe the actual native failure write at 0xffffffff with BASEPRI
64 in emulation. Preflight failures preserve the old realloc allocation. A
separate hypothetical nullable-backend test verifies defensive NULL handling;
it does not suggest that the normal native allocator returns NULL on OOM.

The final probe executes the normal C adapter, actual native heap initialize/
allocate/free/coalescing code and actual memcpy/memset. Scheduler suspend and
resume are modeled with caller-clobber poisoning. Across 648 calls and 22
scenarios, it checks boundary sizes, eight-byte alignment, exact copy/clear
lengths, zero and overflow cases, successful growth/shrink/same-size realloc,
old-block preservation, shared coexistence with raw native allocations and
full free-space recovery. A seeded 512-operation live allocation sequence
checks all retained payloads after every operation and recovers all 51184
usable bytes. Saved core registers, SP and interrupt masks are checked on
returning calls. No stock code is mapped.

Six compiled defects are detected: bad size metadata, wrong calloc fill,
realloc overcopy, freeing on failed realloc, omitted overflow preflight and
allocating a zero-size request. A clean final baseline is rerun afterward.
Physical concurrency, actual scheduler suspension, whole-program memory
placement, malformed metadata/pointers and complete formatter execution are
not established. The adapter uses more heap space per newlib allocation for
its size/alignment header and can temporarily hold old and replacement blocks.

R1 compiles 789 units (707 application, 82 bootloader), without failures or
duplicate strong symbols. Application imports fall from 103 to 101 with none
added. All 786 prior nongenerated object hashes remain unchanged; the two
generated bootloader objects retain allocated bytes and relocations despite
metadata changes. Bootloader linker metadata imports remain 22 and strict
source bootloader linking succeeds. Global source checking retains the
unrelated unlisted G2 resident_rom_thumb_set.S failure. Full application linking
remains unfinished; no source-plan qualification or stock byte-identity claim
is made for this license-free runtime adapter.
