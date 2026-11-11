# R1 subscriber multicast control in C

The dispatcher at `0x8b028` now uses C for short-payload caching, allocation,
thread selection, direct callbacks, queued routing and release. REA observed
its contiguous 202-byte stock body through `0x8b0f1`; literals at `0x8b0f4`
and `0x8b0f8` identify the root table and two route records. Analysis is bound
to the locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

Stock behavior includes details that must survive reconstruction:

- An absent initial root returns zero. The selector has no bounds guard;
  address calculation wraps as an unsigned machine word.
- Payloads of at most four bytes clear the cached word before movement and
  reload the root slot between these operations. Thread identity is sampled
  after caching and before allocation. The list head is captured before the
  allocator runs.
- Allocation and publication size is the low 16 bits of `length + 8`, while
  the copied payload length remains the full input word. The allocated record
  stores the list head, a 16-bit length, and payload at offset six.
- Current-thread callbacks receive the original payload. Other subscribers
  match routes by thread-cell address, rather than the cell's current value.
  Each known route publishes once, and subsequent next pointers are read live.
- Failed allocation still allows direct callbacks. Publication return values
  do not change traversal or the success result. The original temporary record
  is released after dispatch; publication owns its separate queued copy.

Two small assembly adapters remain: an eight-byte entry adapter reproduces
stock's restoration of the original inputs into result R1/R2/R3, and a two-byte
`BX R2` gateway preserves the opaque callback's R0/R1/R2 inputs. Replacing these
with ordinary C calls would lose their observed machine contracts. The
shared route declaration moved to `native_subscriber.h`; registration object
bytes and every other object remain unchanged. No data owner was added.

The [machine-readable receipt](subscriber-multicast-c-review.json) records:

- 6,997 paired stock/C cases covering selectors, mapped overflow aliases,
  short caches, zero callbacks, route deduplication, allocation failure,
  size wrapping, overlapping RAM copies and callback/allocator/lock/publication
  mutations. Checks include shared structural access order, final bytes,
  native null-root faults, return registers R0–R3, saved registers, SP and masks.
- 192 paired integration cases execute the actual C publisher, enqueue and
  consumer together with the dispatcher, mutex wrappers, CMSIS thread getter,
  task getter and memory movement. They check queued descriptor contents,
  wakeups after successful and failed sends, release ownership, and subsequent
  consumer callbacks for each successfully queued copy.
- Two deliberately incorrect variants, repeated route publication and stale
  next-pointer traversal, are rejected. All 575 R1 units compile with zero
  failures or duplicate strong symbols; imports remain 175 application and
  34 bootloader. `make sources-check` passes.

All five qualification variants compile; none produces a selected exact
region. The canonical plan remains unchanged. The fresh hybrid application
equals stock with 3,881 source-built bytes, 642,279 binary pull-through bytes,
248 resource bytes, and source completeness explicitly false.

Allocator, mutex, queue, flags and opaque callback effects are modeled.
Movement internals, private stack residue and the publisher's uninitialized
leading queue word are excluded; defined queue fields and copy results are
checked. Huge successful copies and arbitrary allocation extents are not
covered. Physical hardware operation, real scheduling, a complete source
executable link and a byte-identical full source rebuild remain unproven.
G2 gates were not advanced, and the overall goal remains active.
