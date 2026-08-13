# EasyLogger G2 asynchronous queue source-candidate audit

## Result

`runtime_easylogger_async_queue_candidate.c` is a production-excluded,
clean-room recreation of the complete conclusively recovered G2 downstream
EasyLogger queue lifecycle:

```text
pool initialize   [0x0044895E,0x004489E8)  138 bytes
dummy reset       [0x004489E8,0x00448A0C)   36 bytes
record allocate  [0x00448A0C,0x00448A8E)  130 bytes
record recycle   [0x00448A8E,0x00448AF0)   98 bytes
record enqueue   [0x00448AF0,0x00448B96)  166 bytes
record dequeue   [0x00448B96,0x00448C74)  222 bytes
state initialize [0x00448C74,0x00448CAA)   54 bytes
```

The candidate implements the fixed `0x110` record ABI, exact 256-record pool,
Treiber free-list pop and push, and both Michael–Scott dummy-queue operations.
It source-owns the three
typed atomic adapters, retains explicit seams for their authenticated inner
store/load/strong-compare-exchange primitives, and retains the exact writable
globals. Enqueue's
retry-exhaustion path calls the source-local recycler, so a nonnull record is
consumed on **every** enqueue return: success transfers it to the queue and
failure attempts one recycle before returning zero.

The candidate is not named by `overlay.json`, the core-source manifest, or
the Makefile. It therefore cannot change a flashable artifact. This audit is
a software-only result; no hardware was connected, flashed, reset, or run.

## Provenance boundary

The authenticated EasyLogger snapshot is official commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, under the MIT license. Its
upstream asynchronous implementation is a byte ring buffer and does not
contain this fixed-record allocator or lock-free queue. The installed image
retains the downstream path `easylogger/src/elog_async_api.c`, which is not
present in the authenticated upstream history covered by the EasyLogger
version audit.

These three functions are consequently classified as project clean-room
source informed by authenticated observed behavior, not copied or inferred
upstream EasyLogger source. The upstream snapshot remains applicable to the
public EasyLogger core, but it cannot establish the private G2 queue ABI.

## Authenticated stock boundaries

The official OTA has a 32-byte transport preamble. Installed Apollo-main
bytes are loaded at `0x00438000`. Every range below is hashed from that
installed payload.

| Function | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| inner store primitive | `[0x004488EC,0x004488F4)` | 8 | `e5f5e62dc71878f964110f3a656adbc03cd55c51f0aaa0542b6ead80f99430e8` |
| inner load primitive | `[0x004488F4,0x004488FC)` | 8 | `e0af382433dcd2fe57b105589adcbeb5b7862f9c9cbc16ce06cf1c73f6e61c2e` |
| inner strong compare/exchange primitive | `[0x004488FC,0x00448930)` | 52 | `432307baa22caece864fb4e876f4ad6020f286a27e1cfebabd8df3bf71311de2` |
| atomic store wrapper | `[0x00448930,0x00448938)` | 8 | `31549b25a562ad9bb17f62fd20e4ed474cab10acda78d9a78f40374150dfd96b` |
| atomic load wrapper | `[0x00448938,0x00448940)` | 8 | `36801dc170e6d188ad67099920b8687395943ac4206649d4c4d9dba048f598f4` |
| atomic compare/exchange wrapper | `[0x00448940,0x0044895E)` | 30 | `e2ef1add5fc30b2ca5348d2cb29e5d8866e5c8b7fd4318ee27d4bc0fe37cc20b` |
| record allocate | `[0x00448A0C,0x00448A8E)` | 130 | `8fe9888ed7114728cbfd66f1190f62ddd09baa798cfa6ab03f0216ced8c148fa` |
| record recycle | `[0x00448A8E,0x00448AF0)` | 98 | `a694515d5f6c3389699ab4beceb8f675dfb604cf214ddf949ad429ed03e1502e` |
| enqueue | `[0x00448AF0,0x00448B96)` | 166 | `d38c8f35778486058d045b6b7ad9f9b6a6d8c5242f3c36828f72ea4270bc4c8e` |
| dequeue | `[0x00448B96,0x00448C74)` | 222 | `2ffb54da31890c2f13a19dd824b32416834fdc1de9ba30aefaa728157f80d89d` |
| async state initialization | `[0x00448C74,0x00448CAA)` | 54 | `cf885aafebce26a3b9c0333b549c2d4aac5418706060d45c4b9ca5dd72f3832d` |
| pool/free-list initialization | `[0x0044895E,0x004489E8)` | 138 | `68db4f01f775e26ee30f1fd42f6f87f6846796a1577fd6d4908ac1ce9414a9da` |
| queue dummy reset | `[0x004489E8,0x00448A0C)` | 36 | `97ece75427abf834ff648cc4c51214a1a8f08f92614cb956e821c2f2d4fac6a5` |

Whole-image decoding authenticates these exact direct callers:

| Entry | Direct `BL` callers | Caller-list SHA-256 |
|---:|---|---|
| `0x00448A0C` | `0x00448D02`, `0x00448D84` | `3da233fa29c40fd4c264b558f9dee54283b36349054d65a7c7d373aaf56e909c` |
| `0x00448A8E` | `0x00448B6C`, `0x00448D38`, `0x00448DBE`, `0x00448E06` | `e63c6bd159c05e8714f207aab3147544aa9209a3850ee6b93dfb9f28b078608d` |
| `0x00448AF0` | `0x00448D2E`, `0x00448DB4` | `698fba2e8df984ccc5b94b1f2e92dd1aabf083f76e1fbc3a0909b2b746d9f2df` |
| `0x0044895E` | `0x00448C84` | `c28398907c2837030307a3d55105851779dba978e94825b5e827c60de0ac351d` |
| `0x004489E8` | `0x00448C88` | `ac85eb28a9ce105208163da561f07b40799b118a1267c11a9189abbc46e99383` |
| `0x00448B96` | `0x00448E1C` | `27b52d08b84f7bc14729ae2a0a15b960f62904c770eff47a21bee2f3ba241530` |
| `0x00448C74` | `0x005BFA30` | `0d1553b2fcfc3a684d8b94610e3d47d4bb79b31c37b090e95c13569ebd6c110e` |

For all three spans, exhaustive scans find no `B.W`, narrow branch, or
conditional branch to the entry; no external branch to an interior
halfword; and no byte-granular stored even or Thumb pointer to the entry or
interior. This authenticates the source-candidate boundaries without yet
authorizing redirects.

## Fixed record and statistics ABIs

The candidate header expresses and statically checks every observed field:

```c
struct open_cfw_easylogger_async_queue_record {
    uint32_t next;          /* +0x000, atomic intrusive link */
    uint32_t state;         /* +0x004: 0 free, 1 allocated, 2 enqueued */
    uint16_t length;        /* +0x008 */
    uint16_t metadata;      /* +0x00A */
    uint8_t  level;         /* +0x00C */
    uint8_t  payload[256];  /* +0x00D */
    uint8_t  padding[3];    /* +0x10D */
};                          /* 0x110 bytes */
```

The recovered statistics object is exactly 48 bytes:

| Offset | Candidate name | Observed updates |
|---:|---|---|
| `+0x04` | `failed_operation_count` | empty allocation and allocate/enqueue retry exhaustion |
| `+0x0C` | `allocate_retry_total` | successful allocation adds `attempts - 1` |
| `+0x10` | `allocate_attempt_maximum` | maximum successful allocation attempt count |
| `+0x14` | `recycle_retry_total` | successful recycle adds `attempts - 1` |
| `+0x18` | `recycle_attempt_maximum` | maximum successful recycle attempt count |
| `+0x1C` | `enqueue_retry_total` | successful enqueue adds `attempts - 1` |
| `+0x20` | `enqueue_attempt_maximum` | maximum successful enqueue attempt count |
| `+0x2C` | `retry_limit_count` | allocation, recycle, or enqueue retry exhaustion |

Offset `+0x00` is the drain's cumulative processed-record counter. Offsets
`+0x24` and `+0x28` are dequeue retry-total and attempt-maximum counters.
Offset `+0x08` remains deliberately reserved because the closed queue and
consumer lifecycle does not establish its meaning.

The candidate retains these writable seams:

| Literal | Runtime object | Candidate symbol |
|---:|---:|---|
| `0x00448FB0` | free-list head `0x20074574` | `open_cfw_retained_easylogger_async_free_head` |
| `0x00448FBC` | statistics `0x2007342C` | `open_cfw_retained_easylogger_async_queue_statistics` |
| `0x00448FC0` | queue tail `0x2007413C` | `open_cfw_retained_easylogger_async_queue_tail` |

The retained primitive seams remain fixed at `0x004488EC`, `0x004488F4`, and
`0x004488FC`; source adapters model the typed wrappers at `0x00448930`,
`0x00448938`, and `0x00448940`. Exhaustive direct-call topology proves that
the official typed wrappers call only their matching inner primitive. It also
preserves a subtle stock distinction: state stores in allocate, recycle, and
enqueue call the inner store directly at `0x00448A7E`, `0x00448A9C`, and
`0x00448B02`, while intrusive `next` stores call the typed store adapter at
`0x00448A86`, `0x00448AB0`, and `0x00448B0A`.

The inner compare/exchange uses `LDREX`/`STREX`, retries `STREX` failure
internally, executes `DMB`, and fails only when the observed value differs
from expected. It is therefore a **strong** compare/exchange: it never fails
spuriously and updates the caller's expected word on mismatch. The source
adapter preserves that contract and its byte-sized Boolean result.

The statistics fields are declared volatile and all candidate updates go
through compiler-visible volatile loads and stores. This is a compatibility
measure for the observed ordinary `LDR`/arithmetic/`STR` target behavior, not
an atomicity claim: interrupt or concurrent writers can still lose updates.
The complete Apple and Linux target function bytes and relocations pin that
code generation and ensure no compiler atomic-runtime dependency appears.

## Recovered algorithms

### Treiber allocation

Allocation repeatedly loads the free-list head and returns null immediately
when it is zero. For a nonzero head, it loads `head->next` and attempts to
replace the free head with that next token. A successful pop records
`attempts - 1`, updates the maximum with the full attempt count, stores state
one, clears `next`, and returns the record.

The loop performs at most 1,000 compare/exchange calls. Its next iteration
increments the attempt counter to 1,001 and fails before another CAS,
incrementing both `retry_limit_count` and `failed_operation_count`.

### Treiber recycle

Null recycle is a no-op. A nonnull recycle stores state zero, then repeatedly
loads the free head, stores that value into `record->next`, and attempts to
replace the head with the record token. Success records the retry total and
maximum with the same convention as allocation.

After 1,000 failed compare/exchanges, the 1,001st loop iteration stores the
latest free head into the record and exits before CAS. It increments only
`retry_limit_count`. The record remains state zero but is not reachable from
the free head: this is the observed recycler-leak behavior, preserved and
called out as a promotion blocker.

### Michael–Scott enqueue

Null enqueue returns zero without state, global, statistic, or atomic-wrapper
access. A nonnull call first stores state two and clears `record->next`, then:

1. loads the current tail and `tail->next`;
2. reloads the global tail and retries if the snapshot changed;
3. if `tail->next` is nonzero, helps advance the lagging tail and retries;
4. otherwise compares/exchanges `tail->next` from zero to the new record;
5. after a successful link, records retry statistics and makes a best-effort
   compare/exchange to advance the tail to the new record.

The loop permits 10,000 compare/exchange attempts. The 10,001st snapshot
fails before another CAS, increments `retry_limit_count` and
`failed_operation_count`, calls the source-local recycler once, and returns
zero. Thus callers must never recycle a nonnull argument after **either**
return value. This makes the ownership rule explicit and avoids perpetuating
the builder's separately audited double-recycle defect when this candidate
is eventually paired with the corrected single-owner builder.

### Pool, dummy reset, and one-shot initialization

Initialization fully zeroes records 0 through 253 and links each to its
successor. Records 254 and 255 preserve stock's narrower initialization: only
`state` and `next` are cleared. Record 254 terminates the 255-record free list;
record 255 becomes the queue dummy, leaving 255 allocatable records. The
one-shot wrapper returns immediately when the ready byte is already nonzero;
otherwise it builds the pool, resets head/tail to the dummy, zeroes all 48
statistics bytes, sets default metadata and ready to one, and returns zero.

### Michael–Scott dequeue and dummy rotation

Dequeue validates head snapshots, helps a lagging tail when head equals tail
but `next` is nonzero, and advances head with strong compare/exchange. Empty
queues return null. Retry iteration 10,001 increments the shared retry-limit
counter and returns null. Success copies `length`, `metadata`, and exactly
`length + 1` payload bytes from the next node into the old dummy, then returns
that old dummy. It intentionally does not copy `level`, matching stock and the
current consumer ABI.

## Deterministic host schedule oracle

`runtime_easylogger_async_queue_candidate_host.c` maps the real pool tokens
beginning at `0x202D3FC8` onto four native host records. Its retained inner
primitive implementations inject contention only by mutating the compared
word to a genuinely different competing value before invoking the strong
CAS. The competitor then transitions the word back after the failed CAS,
giving a deterministic ABA schedule without inventing spurious failure.
Tail-snapshot injection likewise alternates between two valid pool tokens.
The focused suite proves:

- first-attempt and contended allocation, empty free list, success on the
  1,000th permitted CAS, exactly 1,000 allocation CAS failures, the distinct
  state/next store paths, totals, maxima, and failures;
- first-attempt and contended recycle, null no-op, success on the 1,000th
  permitted CAS, exactly 1,000 recycle CAS failures, and the resulting
  unreachable state-zero record;
- first-attempt enqueue, contended lagging-tail help, a tail change between
  loads, link contention, contended best-effort final-tail advancement,
  success on the 10,000th permitted link CAS, totals, and maxima;
- tail-snapshot churn through all 10,000 permitted iterations, followed by
  exhaustion before a CAS on snapshot 10,001;
- exactly 10,000 enqueue CAS failures followed by one source-local recycle,
  plus nested exhaustion of all 1,000 recycler CAS attempts with exact
  ownership, failure, and retry-limit statistics;
- success and failure ownership, including no caller-owned nonnull return;
- null enqueue's complete lack of side effects; and
- exact 256-record pool construction, 255-record capacity, dummy reset,
  one-shot initialization, and preservation of the two partially initialized
  tail records;
- empty, first-attempt, tail-help, contended, and 10,000-attempt dequeue
  behavior, including dummy rotation, retry statistics, payload terminator,
  and the stock level-byte omission;
- all record/statistics sizes and offsets;
- strong-CAS success/mismatch expected-word semantics, primitive/adapter call
  counts, and zero bad token translations on every valid schedule; and
- the corrected level-less hexdump builder linked to the real candidate
  allocator and enqueue for both success and enqueue-exhaustion behavior.

The combined fixture statically checks the independently declared builder and
queue record sizes and payload offsets. A shared ABI header was not introduced
in this review-fix tranche because the authorized edit boundary excludes the
hexdump candidate C/H; that later refactor must change both candidates
atomically rather than silently making one include a header it does not own.

This is a schedule-injection oracle, not a claim that a single host process
proves ARM multi-core or interrupt-context lock-free behavior.

## Dual compiler closure pins

The freestanding candidate is built with the reviewed Thumb-v7E-M flags,
ROPI, function/data sections, no builtins, no unaligned access, and no unwind
tables. Both compiler profiles expose exactly six undefined symbols: the
three atomic wrappers, free head, queue tail, and statistics object. Enqueue's
recycler relocation resolves to the source-local function and is not an
undefined seam.

| Profile | Compiler | Object bytes | Object SHA-256 |
|---|---|---:|---|
| `apple-clang` | Apple clang 21.0.0 (`clang-2100.3.30.1`) | 7,092 | `9a7e470a573493c46be3399bef5bb02b345c8990a0a875269de923d643788fed` |
| `linux-clang` | Homebrew clang 22.1.8 | 7,044 | `b6c9cd26bc81e4aa978d293d0069d4e6ddd0b07a6cabbbc3f8afb652c239cdb6` |

| Function | Apple bytes / SHA-256 | Linux bytes / SHA-256 |
|---|---|---|
| store adapter | 4 / `90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f` | same |
| load adapter | 4 / `90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f` | same |
| strong-CAS adapter | 28 / `d87c46ceb9ec5d930445c480ca011d65a326bc48ac14cafe377a438fcc690fa0` | same |
| allocate | 138 / `22dcf80f2f61e2e23780ec9398843aa2987e3b6606b69735fc7ffd6043c22974` | same |
| recycle | 136 / `dd3c08bd50a4990a80232e21843b9c2ed79d7a7fe63e4a041188d89c3e1dca50` | 122 / `e7853b2cff962c465c6de5ca0f66f96504b680d4dc503599576276113f7e40ef` |
| enqueue | 220 / `9ead4766d3f2c035442afa4a19fcd8a27c0a673a747f8bed807c5f00f7087701` | same |
| pool initialize | 418 / `a4ba43045a9c57dbac5ee4aa3b5f80e91dc3f51cfe21df5b0bb9ebefb5744fb9` | same |
| dummy reset | 58 / `a8fb1df6a0003486b811a142e0277c5f4eac6b1d04943cbd7184ee90aaf1097b` | same |
| state initialize | 230 / `bc9ccc392fe2ccda2e0afc43a9d960bac330a3ca7252be6cf48bd274ab9134fe` | same |
| dequeue | 284 / `382af6a463906124ff0c6de89b2416405a97d6d3879ae7f196894638511f9f8f` | 284 / `e3cb0022d346dd7d800081223501fd652da2940b6bac5819878762c3bca70fcc` |

The test suite pins each relocation's offset, ELF type, and symbol separately
for both profiles, including every adapter-to-primitive edge and each direct
state-store primitive edge. Source-local recycler binding is required at
enqueue offset 204 in both objects. Mutation tests alter bytes independently
in all six authenticated primitive/adapter spans and alter the record payload
extent: byte changes break their digests, and the ABI change is rejected by
the header's compile-time assertions.

## Residual risks and promotion blockers

This tranche intentionally stops before production integration. The
following issues remain explicit:

1. **ABA:** the free-list and queue links are untagged 32-bit pointers. Static
   flow shows no generation counter or hazard-pointer scheme. Pool reuse can
   therefore present ABA schedules that the deterministic host oracle does
   not eliminate.
2. **Non-atomic statistics:** all eight observed counters remain volatile
   compatibility load/add/store words. This prevents the compiler from
   caching or deleting accesses across candidate operations but does not make
   read/modify/write atomic. Concurrent operations can lose updates.
3. **Recycler leak:** 1,000 failed recycle CAS operations leave the record in
   state zero but outside the free list. Enqueue still consumes ownership on
   failure even when this internal recycle exhausts.
4. **ISR and memory-order contract:** the retained inner primitives contain the
   target exclusives and barriers, but this candidate has not been executed
   under the G2's real task/ISR preemption patterns. ISR eligibility and
   priority masking assumptions remain unproven.
5. **Hardware stress:** target-side stress must cover free-list ABA pressure,
   allocator/recycler/enqueue contention, 255 live records, lagging-tail
   helping, retry exhaustion, event coalescing, and long-duration pool
   accounting before any redirect is enabled.
6. **Separate consumer/worker cluster:** queue initialization, reset, enqueue,
   and dequeue are closed here. Record drain/callback behavior and event
   worker/thread creation remain outside this candidate, but are now closed by
   their own dual-profile candidates with explicit CMSIS and first-party seams.

## Validation

Apple-clang focused validation:

```sh
python3 -m unittest -v \
  openCFW/tests/test_easylogger_async_queue_candidate.py
```

Reviewed Linux/Homebrew-clang validation:

```sh
docker exec -w /workspace/openCFW \
  -e OPENCFW_CLANG=/home/linuxbrew/.linuxbrew/bin/clang \
  -e OPENCFW_TOOLCHAIN_PROFILE=linux-clang \
  opencfw-linux-llvm \
  python3 -m unittest -v \
    tests/test_easylogger_async_queue_candidate.py
```

The suite runs 27 tests. It authenticates stock spans and complete topology,
exercises every recovered success/failure/retry/ownership path through the
host schedule oracle, pins both target objects and complete relocation sets,
checks narrow, unconditional-wide, and conditional-wide ingress, checks
production exclusion, and proves fail-closed stock-byte and ABI mutations.
