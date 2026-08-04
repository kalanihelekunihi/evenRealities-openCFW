# G2 EasyLogger asynchronous record-builder audit

## Result

The private Apollo-main function at `0x00448D4E` is the smallest mechanical
source-replacement boundary after the G2 submission wrapper. It is one
132-byte function with one direct caller, no alternate entry, no external
branch to an interior instruction, and no stored entry or interior pointer:

```text
[0x00448D4E, 0x00448DD2)
SHA-256 9d95b63bc62e11910e39344ddea65213798d75caa4b91d5ce9cf033d09509e17
```

It can be recreated without replacing the lock-free queue, provided the
source preserves the fixed `0x110`-byte record ABI and retains explicit
allocator, enqueue, recycler, and diagnostic seams. The stock copy call may
be replaced by a local byte loop or a reviewed freestanding `memcpy`.

There is, however, one blocking ownership decision before such a candidate
should be activated. On its only reachable failure with a nonnull record,
the retained enqueue function recycles the record before returning zero.
The stock builder then recycles that same record a second time. Static
instruction flow therefore shows a double insertion into the free list,
normally creating a self-linked free-list head. A builder-only source
replacement must deliberately choose either:

1. exact stock compatibility, including the double-recycle defect; or
2. corrected ownership, where failed enqueue owns/recycles the record and
   the builder emits the diagnostic without recycling it again.

The second policy is the safer implementation, but it is a conscious
behavioral divergence and should be gated by a target concurrency oracle.
No hardware was accessed during this audit.

## Evidence set

The official Apollo-main OTA wrapper contains a 32-byte transport preamble.
Runtime addresses below use the 3,523,364-byte installed payload loaded at
`0x00438000`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed Apollo-main payload | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Authenticated `third_party/easylogger/src/elog_async.c` | 10,713 | `2a3d496f9e7e2a7b0135c0ffbecbbf367b484134cf20909853338a8f919b8e6c` |

The local EasyLogger snapshot is authenticated official commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, under MIT license.
`third_party/easylogger/verify_snapshot.py` passes offline.

Apollo main retains the path
`third_party\EasyLogger-master\easylogger\src\elog_async_api.c` at
`0x006DA73C`. That filename is absent from the authenticated official
EasyLogger history covered by the repository's version audit. The record
builder and queue are consequently treated as downstream/private G2 code,
not as unequivocally MIT-licensed upstream source.

## Exact boundary and ABI

The preceding function is a separate level-less builder ending at
`0x00448D4E`. The consumer drain begins at `0x00448DD2`.

| Function | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| level-less sibling builder | `[0x00448CCC,0x00448D4E)` | 130 | `91ae986d5deaa816a662a842ecd71217c0deb0dff552ebbe04e382f16e8ebc55` |
| level-aware builder | `[0x00448D4E,0x00448DD2)` | 132 | `9d95b63bc62e11910e39344ddea65213798d75caa4b91d5ce9cf033d09509e17` |
| following consumer drain | `[0x00448DD2,0x00448E2A)` | 88 | `43ac9598579abc817bc013e3f65ad69639f72f7bf03cbe6ca3bdd8596e5612e7` |

The inferred AAPCS entry is:

```c
uint32_t g2_async_record_build(
    const char *buffer,       /* r0 */
    uint32_t length,          /* r1 */
    uint32_t metadata,        /* r2, low byte used */
    uint32_t level);          /* r3, low byte stored */
```

The submission wrapper at `0x0044AA80` calls it at `0x0044AA88` with:

```text
r0 = formatted log buffer
r1 = formatted length
r2 = 0
r3 = level truncated to eight bits
```

The builder itself truncates metadata to eight bits. It stores the fourth
argument with a byte store. Its return register is explicitly zero on every
exit, including successful enqueue. The sole caller immediately prepares
the event-flags call and never tests the result.

The adjacent level-less builder at `0x00448CCC` is a distinct entry with its
own caller at `0x0044AA7A`. It does not write record offset `+0x0C`.
Replacing the level-aware builder does not require redirecting or modifying
that sibling.

## Recovered behavior

The complete builder flow is:

1. read the ready byte at `0x20074FC0`;
2. return zero silently if not ready, `buffer == NULL`, or `length == 0`;
3. truncate metadata to eight bits and, if it is zero, substitute the byte
   at `0x20004546`;
4. clamp every input length of 256 or greater to 255;
5. allocate a record through `0x00448A0C`, returning zero silently if none
   is available;
6. copy exactly the clamped number of bytes to record offset `+0x0D`;
7. append `'\0'` at `payload[length]`;
8. write the 16-bit length at `+0x08`;
9. write zero-extended 8-bit metadata as a 16-bit value at `+0x0A`;
10. write the low level byte at `+0x0C`;
11. call enqueue at `0x00448AF0`;
12. on nonzero enqueue result, return zero;
13. on zero enqueue result, call recycler `0x00448A8E`, emit
    `"error!!!!!!elog_async_ext_output: enqueue_log failed\n"` through
    `0x004733EE`, and return zero.

The ordered direct-call tuple string is:

```text
00448D84->00448A0C,00448D9C->00439BE4,00448DB4->00448AF0,00448DBE->00448A8E,00448DC4->004733EE
```

Its SHA-256 is
`640a313de58123598d8e2aa04664eb062c22535b5402514844f5b1d818c2887e`.

## Fixed record ABI

The builder's writable record view is:

```c
struct g2_async_record {
    uint32_t next;          /* +0x000, owned by free list / queue */
    uint32_t state;         /* +0x004: 0 free, 1 allocated, 2 enqueued */
    uint16_t length;        /* +0x008 */
    uint16_t metadata;      /* +0x00A */
    uint8_t  level;         /* +0x00C */
    char     payload[256];  /* +0x00D through +0x10C */
    uint8_t  padding[3];    /* +0x10D through +0x10F */
};                          /* stride 0x110 */
```

The maximum copied payload is 255 bytes, leaving the final payload byte for
the terminator. The builder never reads or writes `next`, `state`, or tail
padding; allocator and enqueue own the first eight bytes.

The record pool begins at `0x202D3FC8` and spans 256 strides through
`0x202E4FC8`. Blocks 0 through 254 form the free-list population. Block 255
at `0x202E4EB8` is the initial queue dummy, yielding 255 allocatable records.

The queue's dummy-node dequeue copies `length`, `metadata`, and
`payload[length + 1]` into the old dummy before returning it. It does not
copy `level`. The current consumer never reads `level`, so the field is
stored by the builder but is not delivered to the configured callback.

Source should use `sizeof` and `offsetof` assertions for the stride and all
five observed fields. It should not import a host compiler's atomic or
packing assumptions into `next` and `state`; those remain opaque to a
builder-only replacement.

## Direct and transitive dependencies

| Dependency | Range/address | Builder contract |
|---|---:|---|
| ready byte | `0x20074FC0` | nonzero permits submission |
| default metadata byte | `0x20004546` | substitutes for low-byte zero |
| record allocator | `[0x00448A0C,0x00448A8E)` | returns a record in state 1 or null |
| byte copy | `[0x00439BE4,0x00439C8A)` | `memcpy(destination, source, length)` |
| enqueue | `[0x00448AF0,0x00448B96)` | returns one on success, zero on failure |
| recycler | `[0x00448A8E,0x00448AF0)` | returns a record to the free list |
| diagnostic output | `[0x004733EE,0x0047341A)` | variadic retained print seam |
| error string | `0x0071E990` | enqueue-failure diagnostic |

| Dependency | Bytes | SHA-256 |
|---|---:|---|
| record allocator | 130 | `8fe9888ed7114728cbfd66f1190f62ddd09baa798cfa6ab03f0216ced8c148fa` |
| byte copy | 166 | `8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd` |
| enqueue | 166 | `d38c8f35778486058d045b6b7ad9f9b6a6d8c5242f3c36828f72ea4270bc4c8e` |
| recycler | 98 | `a694515d5f6c3389699ab4beceb8f675dfb604cf214ddf949ad429ed03e1502e` |
| diagnostic output | 44 | `995b43fde13c4f3fe3f3c59069fd1b3afc4fdc595a84ed2488c1cb2420b30762` |

The allocator and recycler transitively depend on free-list head
`0x20074574`, lock-free atomic helpers, and statistics at `0x2007342C`.
Enqueue depends on queue tail `0x2007413C`, record `next/state`, the same
atomic helpers and statistics, and recycler `0x00448A8E`. A builder-only
replacement must not manipulate those transitive internals.

## Enqueue failure ownership defect

The builder's apparent recycler call cannot be treated as an ordinary
"enqueue leaves ownership with caller on failure" rule.

For a nonnull builder record, the retained enqueue has only one zero-return
path:

```text
00448B30  compare attempt counter with 0x2711 (10,001)
00448B36  branch to retry-limit failure
00448B5A  increment shared retry-limit statistic
00448B64  increment enqueue/drop statistic
00448B6A  r0 = record
00448B6C  call 0x00448A8E              ; recycle record
00448B70  r0 = 0
00448B72  return
```

The null-input zero return at `0x00448AF8` is unreachable from this builder
after successful allocation.

The builder then executes:

```text
00448DB4  call 0x00448AF0              ; enqueue
00448DB8  compare result with zero
00448DBC  r0 = record
00448DBE  call 0x00448A8E              ; recycle same record again
00448DC2  load diagnostic string
00448DC4  call 0x004733EE
```

With no intervening allocator, the first recycle makes the record the
free-list head. The second recycle loads that same record as the current
head, writes the record's `next` pointer to itself, and successfully leaves
the free-list head unchanged. The next allocation can return the record
while leaving it as the free-list head; a following allocation can then
return the same record again. If another thread intervenes, duplicate
ownership remains possible through a different ordering.

This is not a theoretical API ambiguity: both recycler calls and both
control-flow edges are present in the stock bytes. What cannot be measured
without target execution is whether the 10,000-CAS exhaustion is reachable
under real scheduling and contention.

For a source candidate retaining stock enqueue, define its ownership seam
explicitly:

```c
/*
 * Returns 1 after queue ownership transfer.
 * Returns 0 after the retained function has already recycled the record.
 */
uint32_t retained_enqueue_consumes_on_failure(struct g2_async_record *);
```

Then the safer builder failure path emits the diagnostic but does not call
recycler. If exact defect compatibility is required, that second recycle
must be an explicit, separately tested compatibility option rather than an
accidental assumption.

## Upstream and standard-library reuse

### EasyLogger

Authenticated upstream `elog_async.c` has no fixed-record builder. It uses a
byte ring buffer and exposes:

```c
void elog_async_output(uint8_t level, const char *log, size_t size);
```

Its enable/threshold, partial-write, synchronous-fallback, and notification
behavior differ from this G2 function. No upstream EasyLogger function can
replace the builder or determine its metadata and record ABI.

### C byte copy

The call at `0x00448D9C` has the ordinary non-overlapping
`memcpy(destination, source, length)` contract. This part can be replaced
unequivocally by:

- a private byte loop inside the builder, avoiding another seam; or
- a reviewed freestanding `memcpy` already guaranteed by the final target
  link.

Reusing upstream EasyLogger's calls to `memcpy` does not confer upstream
provenance on the G2 record algorithm. A local loop is the smallest and most
auditable initial choice.

### CMSIS and C atomics

The builder itself calls no CMSIS queue primitive. CMSIS event flags belong
to the already separated submission wrapper. Replacing this queue with
`osMessageQueue`, a FreeRTOS queue, or C11 atomics would change allocation,
capacity, retry, statistics, dummy-node, failure-ownership, and possibly
ISR-context behavior. None is a drop-in substitution at the builder
boundary.

C11 atomics may become useful only when the allocator/enqueue/recycler
cluster is source-owned as one concurrency boundary and its memory-order
requirements have target tests.

## Whole-image caller and pointer topology

The 3,523,364-byte installed payload was scanned at every halfword for
Thumb-2 `BL` and `B.W`, every halfword for narrow unconditional/conditional
branches and `CBZ`/`CBNZ`, and every byte offset for possible 32-bit even
and odd/Thumb addresses.

| Topology item | Result |
|---|---|
| Direct `BL` sites to `0x00448D4E` | `0x0044AA88` |
| Direct `B.W` sites to entry | none |
| Narrow branch sites to entry | none |
| External wide branches into `(0x00448D4E,0x00448DD2)` | none |
| External narrow branches into the interior | none |
| Stored even/odd entry or interior pointer | none |

Encoding the sole caller as uppercase eight-digit hexadecimal without `0x`
gives SHA-256
`2670d4a2ca18ae826c3a359f9826321f58b9101850ab0ccb681f185f810ee769`.

The caller is the already source-owned candidate wrapper boundary
`[0x0044AA80,0x0044AA98)`, whose stock SHA-256 is
`787d13cfe59fad83061379298387393fa94266c9b31420e7f67e8e07d63f7356`.
It ignores the builder return and unconditionally notifies event bit one.

The builder is therefore redirect-safe without caller rewriting, pointer
table relocation, or an interior trampoline.

## Recommended next source boundary

Use one source entry corresponding only to:

```text
[0x00448D4E,0x00448DD2)
```

Its explicit seams should be:

```text
ready byte
default metadata byte
retained record allocator
retained enqueue with documented failure ownership
retained diagnostic output
```

Use a local byte loop instead of retaining the stock copy call. Do not
expose the recycler to the normal corrected builder path because retained
enqueue already recycles on its only reachable failure. If a stock-defect
compatibility mode is required, expose the second recycler call under a
named policy.

The candidate should preserve:

- null, zero-length, unready, and allocation-failure silent exits;
- metadata low-byte substitution;
- clamp-to-255 rather than partial records or rejection;
- exact terminator, length, metadata, and level offsets;
- zero return on every path;
- diagnostic only after enqueue returns zero;
- no event notification inside the builder.

The wrapper remains responsible for unconditional notification.

The next larger concurrency boundary, if builder-only ownership cannot be
accepted, is allocator + recycler + enqueue as one reviewed queue-producer
cluster. Do not absorb dequeue or the consumer merely to source-own the
builder; their ABI is already separable.

## Isolated source candidates

Two non-integrated translation units now encode the ownership decision
explicitly:

| Candidate | Source | Source SHA-256 |
|---|---|---|
| exact stock compatibility | `components/apollo_main/core_overlay/runtime_easylogger_async_record_build_stock.c` | `32ab04ce6d5f92ff818826312a4dd3d2b8f28296a0891b2d66ed57f992e670a2` |
| corrected single owner | `components/apollo_main/core_overlay/runtime_easylogger_async_record_build_single_owner.c` | `99186110989409fda677b4b02d84a66272990393cdb623410fe573749c4eb290` |

Both are clean-room GPL-3.0-only G2 glue. Neither copies or compiles
upstream EasyLogger `elog_async.c`. Both use a private byte loop instead of
claiming the G2 builder is authenticated upstream code.

They share the recovered public behavior:

- ready/null/zero-length/allocation rejection;
- low-byte metadata defaulting;
- 255-byte clamp and terminator;
- exact record field offsets;
- low-byte level storage;
- zero return on every path;
- retained enqueue and diagnostic seams.

Only the stock-compatible candidate declares and calls the retained
recycler after enqueue returns zero. The corrected candidate's target object
has no recycler symbol or relocation, making accidental reintroduction of
the second recycle detectable at build time.

These candidates are intentionally absent from `overlay.json` and all
firmware manifests. They are test artifacts, not flashable integration.

### Target objects

Both candidates were compiled with the overlay's reviewed
`thumbv7em-none-eabi`, Thumb, `-O2`, freestanding, ROPI flags.

| Candidate | `.text` bytes | `.text` SHA-256 | `.rodata` bytes | `.rodata` SHA-256 |
|---|---:|---|---:|---|
| stock compatibility | 228 | `dce01b3325dc6e08acc71c5497238460f679058d75d5b1e99d0df9e5fb5cb00a` | 54 | `2a8285b704dd7e2cc111a09f750d509f79794fca0aba7ec1513414df4fd9bad3` |
| corrected single owner | 216 | `498d64ad69021489f1a166af5903ac3cdd2edf97dc5f83e16d608b55711a303d` | 54 | `2a8285b704dd7e2cc111a09f750d509f79794fca0aba7ec1513414df4fd9bad3` |

The 54-byte read-only object is exactly the enqueue-error string including
its terminator.

The exact `.text` relocation sets are:

```text
stock compatibility
  006 type 47  retained ready byte
  010 type 48  retained ready byte
  038 type 47  retained default-metadata byte
  042 type 48  retained default-metadata byte
  056 type 10  retained allocator
  190 type 10  retained enqueue
  204 type 10  retained recycler
  208 type 49  local error string
  212 type 50  local error string
  218 type 10  retained diagnostic

corrected single owner
  006 type 47  retained ready byte
  010 type 48  retained ready byte
  038 type 47  retained default-metadata byte
  042 type 48  retained default-metadata byte
  056 type 10  retained allocator
  184 type 10  retained enqueue
  196 type 49  local error string
  200 type 50  local error string
  206 type 10  retained diagnostic
```

Type 10 is the Thumb call relocation. Types 47/48 and 49/50 are the paired
target data-address relocations emitted under the reviewed ROPI build. No
stock function or RAM address is hidden as an absolute literal in either
source candidate.

## Deterministic retry-exhaustion oracle

`tests/fixtures/runtime_easylogger_async_record_build_host.c` supplies the
same retained seams to two independently compiled host libraries. Its
enqueue oracle models the audited retry contract:

1. set record state to enqueued;
2. attempt compare/exchange from counter 1 through 10,000;
3. optionally succeed on an exact configured attempt;
4. after 10,000 failures, increment retry/drop counters;
5. recycle the record once inside enqueue;
6. return zero.

The recycler uses a synthetic 32-bit record token, so the exact free-list
consequence is observable on a 64-bit host without truncating a host
pointer.

`tests/test_runtime_easylogger_async_record_build.py` builds both candidate
libraries and forces `success_attempt = 0`. The observed distinction is:

| Observation | Stock-compatible candidate | Corrected candidate |
|---|---:|---:|
| enqueue attempts | 10,000 | 10,000 |
| enqueue retry-limit count | 1 | 1 |
| enqueue drop count | 1 | 1 |
| total recycler calls | 2 | 1 |
| record `next` after failure | record token, self-link | zero |
| diagnostic calls | 1 | 1 |
| event order | allocate, enqueue, recycle, recycle, diagnostic | allocate, enqueue, recycle, diagnostic |

The same oracle also proves that success on attempt 10,000 performs no
recycle and no diagnostic. Normal-path output is identical between the two
candidates.

## Acceptance gates

A source candidate should not be integrated until focused tests cover:

1. exact body hash, adjacent boundaries, sole caller, and negative
   entry/interior/stored-pointer topology;
2. target AAPCS arguments and explicit seam relocations;
3. ready false, null buffer, zero length, and allocation failure;
4. lengths 1, 254, 255, 256, and larger, including exact terminator;
5. default metadata zero substitution and explicit metadata truncation;
6. level truncation and exact `+0x0C` byte store;
7. record layout `sizeof`/`offsetof` assertions;
8. enqueue success with return zero and no recycler/diagnostic;
9. retained-enqueue failure with diagnostic and exactly the selected
   ownership policy;
10. allocator/enqueue concurrency and retry exhaustion on target before
    enabling corrected ownership in flashable output.

## Validation

All asserted range hashes were recomputed from the installed payload. The
critical pins can be reproduced with:

```sh
python3 - <<'PY'
from hashlib import sha256
from pathlib import Path

image = Path(
    "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
).read_bytes()
payload = image[32:]
base = 0x00438000

expected = {
    (0x00448D4E, 0x00448DD2):
        "9d95b63bc62e11910e39344ddea65213798d75caa4b91d5ce9cf033d09509e17",
    (0x00448A0C, 0x00448A8E):
        "8fe9888ed7114728cbfd66f1190f62ddd09baa798cfa6ab03f0216ced8c148fa",
    (0x00448A8E, 0x00448AF0):
        "a694515d5f6c3389699ab4beceb8f675dfb604cf214ddf949ad429ed03e1502e",
    (0x00448AF0, 0x00448B96):
        "d38c8f35778486058d045b6b7ad9f9b6a6d8c5242f3c36828f72ea4270bc4c8e",
}

for (start, end), expected_hash in expected.items():
    body = payload[start - base:end - base]
    assert len(body) == end - start
    assert sha256(body).hexdigest() == expected_hash
print("G2 EasyLogger async record-builder pins: OK")
PY

python3 third_party/easylogger/verify_snapshot.py
```

The isolated candidate suite is:

```sh
python3 -m unittest -v \
  tests.test_runtime_easylogger_async_record_build
```

It currently runs 13 focused tests covering both candidates, the
deterministic 10,000-attempt oracle, stock span and dependency pins, complete
caller/interior/pointer topology, record ABI, target text/rodata, and exact
relocations.
