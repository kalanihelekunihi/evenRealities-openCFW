# G2 EasyLogger asynchronous sink audit

## Result

Apollo main's function at `0x0044AA80` is a 24-byte G2-specific submission
wrapper, not pristine EasyLogger `elog_async_output`. Its exact AAPCS entry is:

```c
void g2_elog_async_submit(const char *buffer, uint32_t length, uint8_t level);
```

It calls a private record builder as `(buffer, length, 0, level)` and then
unconditionally sets event bit `0x01`. The smallest safe source-replacement
boundary is therefore the wrapper alone:

```text
[0x0044AA80, 0x0044AA98)
```

That replacement is redirect-safe: the complete installed payload has one
direct caller, no external branch to an interior instruction, and no stored
entry or interior pointer. The first increment must retain typed seams to the
G2 record builder at `0x00448D4E` and CMSIS event-flags wrapper at
`0x004495E4`. Substituting authenticated upstream `elog_async_output` at this
entry would corrupt the argument order and change observable behavior.

This is a read-only static result. No hardware was accessed, and this report
does not authorize flashing.

## Evidence set

The official Apollo-main OTA wrapper has a 32-byte transport preamble. All
runtime addresses and range hashes below use the installed bytes after that
preamble, loaded at `0x00438000`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed payload | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Authenticated `third_party/easylogger/src/elog_async.c` | 10,713 | `2a3d496f9e7e2a7b0135c0ffbecbbf367b484134cf20909853338a8f919b8e6c` |

The authenticated EasyLogger snapshot is official commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, with MIT license and verified
provenance recorded in `third_party/easylogger/PROVENANCE.json`.
`third_party/easylogger/verify_snapshot.py` passes offline.

Apollo main also retains this build path at `0x006DA73C`:

```text
D:\01_workspace\s200_ap510b_iar_git\third_party\EasyLogger-master\easylogger\src\elog_async_api.c
```

No `elog_async_api.c` was found in the authenticated official EasyLogger
history covered by the version audit. The G2 queue glue must consequently be
treated as a downstream/private implementation, not unequivocally
MIT-licensed upstream source.

## Exact sink boundary and ABI

The preceding function ends at `0x0044AA80`; the next function starts at
`0x0044AA98`. The complete body is:

```text
0044AA80  push    {r7,lr}
0044AA82  mov     r3,r2
0044AA84  uxtb    r3,r3
0044AA86  movs    r2,#0
0044AA88  bl      0x00448D4E
0044AA8C  movs    r1,#1
0044AA8E  ldr     r0,[pc,#0x74]    ; literal -> 0x20074570
0044AA90  ldr     r0,[r0]
0044AA92  bl      0x004495E4
0044AA96  pop     {r0,pc}
```

| Function | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| G2 EasyLogger async sink | `[0x0044AA80,0x0044AA98)` | 24 | `787d13cfe59fad83061379298387393fa94266c9b31420e7f67e8e07d63f7356` |
| G2 level-aware record builder | `[0x00448D4E,0x00448DD2)` | 132 | `9d95b63bc62e11910e39344ddea65213798d75caa4b91d5ce9cf033d09509e17` |

The sole caller at `0x0043D968` supplies:

```text
r0 = shared formatted log buffer
r1 = formatted length
r2 = level, explicitly truncated to eight bits
```

The wrapper truncates `r2` again, moves it to the builder's fourth argument,
and supplies zero as the third argument. The inferred private builder ABI is:

```c
uint32_t g2_async_record_build(
    const char *buffer,
    uint32_t length,
    uint8_t metadata,
    uint8_t level);
```

The builder returns zero on every path, including successful enqueue. The
sink ignores that value. It also ignores the event-set result and calls the
event wrapper even if the builder rejected the input, allocation failed, or
enqueue failed.

The sink's ordered direct-call tuple string is:

```text
0044AA88->00448D4E,0044AA92->004495E4
```

Its SHA-256 is
`68a27df3a03a37d0dda83a08720a6d8c6c169daa814a10c7426fde35282930fd`.

## Record builder behavior

The builder at `0x00448D4E` performs these operations in order:

1. reject when the ready byte at `0x20074FC0` is zero, `buffer` is null, or
   `length` is zero;
2. if the low byte of `metadata` is zero, substitute the default byte at
   `0x20004546`;
3. clamp every length of 256 or more to 255;
4. allocate one fixed record through `0x00448A0C`;
5. copy the payload to record offset `+0x0D`, then append a zero byte;
6. store the clamped length at `+0x08`, zero-extended metadata at `+0x0A`,
   and the level byte at `+0x0C`;
7. enqueue through `0x00448AF0`;
8. on enqueue failure, recycle the record through `0x00448A8E` and emit
   `"error!!!!!!elog_async_ext_output: enqueue_log failed\n"` through
   `0x004733EE`.

Its ordered direct-call tuple string is:

```text
00448D84->00448A0C,00448D9C->00439BE4,00448DB4->00448AF0,00448DBE->00448A8E,00448DC4->004733EE
```

Its SHA-256 is
`640a313de58123598d8e2aa04664eb062c22535b5402514844f5b1d818c2887e`.

## Queue record layout

The fixed record stride is `0x110` bytes:

```c
struct g2_async_record {
    uint32_t next;          /* +0x000, atomic intrusive link */
    uint32_t state;         /* +0x004: 0 free, 1 allocated, 2 enqueued */
    uint16_t length;        /* +0x008, maximum 255 */
    uint16_t metadata;      /* +0x00A, builder writes an 8-bit value */
    uint8_t  level;         /* +0x00C */
    char     payload[256];  /* +0x00D, data plus required terminator */
    uint8_t  padding[3];    /* +0x10D */
};                          /* 0x110 bytes */
```

The pool begins at `0x202D3FC8` and covers 256 strides through
`0x202E4FC8`. Initialization links blocks 0 through 254 into the free list;
block 255 at `0x202E4EB8` is the initial queue dummy. This gives 255
allocatable records while retaining one moving dummy record.

The dequeue routine is a dummy-node queue. It copies `length`, `metadata`,
and `payload[length + 1]` from the next node into the old dummy, advances
the queue head, and returns the old dummy to the consumer. It does **not**
copy offset `+0x0C`. The submitted level therefore remains in the queued
node but is stale in the record returned to the current drain routine. The
stock consumer never reads it; the file callback receives only
`(payload, length)`. A source recreation must preserve this fact until a
separate compatibility decision and hardware oracle justify changing it.

## Queue implementation and globals

The enqueue and dequeue instruction flow matches a Michael-Scott-style
linked queue: atomic head/tail loads, validation reloads, next-pointer CAS,
and tail helping. The implementation uses `LDREX`/`STREX` plus `DMB`.
Allocation/recycle use a separate atomic free-list head.

The allocation and recycle loops stop when their counters reach 1,001,
allowing at most 1,000 CAS attempts. Enqueue and dequeue stop at 10,001,
allowing at most 10,000 CAS attempts. Statistics, including cumulative and
maximum attempt counts and the shared retry-limit count, live in the
48-byte block at `0x2007342C`.

| Address | Role |
|---:|---|
| `0x20004546` | default metadata byte; initialized to `0x01` |
| `0x2007342C` | 48-byte queue statistics |
| `0x20073B90` | enabled byte and callback pointer pairs |
| `0x20074138` | queue head |
| `0x2007413C` | queue tail |
| `0x20074570` | CMSIS event-flags handle |
| `0x20074574` | record free-list head |
| `0x20074FC0` | async queue ready byte |
| `0x202D3FC8` | fixed record-pool base |

The directly relevant queue and atomic bodies are pinned below.

| Role | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| atomic store wrapper | `[0x00448930,0x00448938)` | 8 | `31549b25a562ad9bb17f62fd20e4ed474cab10acda78d9a78f40374150dfd96b` |
| atomic load wrapper | `[0x00448938,0x00448940)` | 8 | `36801dc170e6d188ad67099920b8687395943ac4206649d4c4d9dba048f598f4` |
| atomic compare-exchange wrapper | `[0x00448940,0x0044895E)` | 30 | `e2ef1add5fc30b2ca5348d2cb29e5d8866e5c8b7fd4318ee27d4bc0fe37cc20b` |
| pool/free-list initialization | `[0x0044895E,0x004489E8)` | 138 | `68db4f01f775e26ee30f1fd42f6f87f6846796a1577fd6d4908ac1ce9414a9da` |
| queue reset | `[0x004489E8,0x00448A0C)` | 36 | `97ece75427abf834ff648cc4c51214a1a8f08f92614cb956e821c2f2d4fac6a5` |
| record allocate | `[0x00448A0C,0x00448A8E)` | 130 | `8fe9888ed7114728cbfd66f1190f62ddd09baa798cfa6ab03f0216ced8c148fa` |
| record recycle | `[0x00448A8E,0x00448AF0)` | 98 | `a694515d5f6c3389699ab4beceb8f675dfb604cf214ddf949ad429ed03e1502e` |
| enqueue | `[0x00448AF0,0x00448B96)` | 166 | `d38c8f35778486058d045b6b7ad9f9b6a6d8c5242f3c36828f72ea4270bc4c8e` |
| dequeue | `[0x00448B96,0x00448C74)` | 222 | `2ffb54da31890c2f13a19dd824b32416834fdc1de9ba30aefaa728157f80d89d` |
| async state initialization | `[0x00448C74,0x00448CAA)` | 54 | `cf885aafebce26a3b9c0333b549c2d4aac5418706060d45c4b9ca5dd72f3832d` |

## Event and consumer path

Main setup calls the following sequence:

```text
0x005BFA2C -> 0x00448F44  create event flags and worker thread
0x005BFA30 -> 0x00448C74  initialize queue/pool/statistics
0x005BFA38 -> 0x00448CAC  enable callback 0x005BF965
0x005BFA40 -> 0x00448CB8  disable secondary callback 0x005BF973
0x005BFA46 -> 0x00448CC4  set default metadata to 0x01
```

The event/thread initializer stores the event handle at `0x20074570` and
creates thread entry `0x00448E8F`. Its copied CMSIS thread attributes name
the thread `"elog_async_handler_thread"`, request a `0x800`-byte stack, and
use numeric priority `0x17`.

The worker waits for mask `0x0F` with option `0x02` and timeout
`0xFFFFFFFF`. Bit `0x01`, set by the sink, calls the drain at `0x00448DD2`
and is then explicitly cleared. The drain dequeues at most 256 records per
wake. Because only 255 records can be allocated, one wake can exhaust the
entire queue even when event-bit notifications coalesce.

Bit 0 of the default metadata enables the configured callback. The setup
callback pointer `0x005BF965` resolves to the function at `0x005BF964`,
which receives `(payload, length)` and forwards the bytes to its retained
storage path. The level byte is not part of that callback ABI.

| Role | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| record drain | `[0x00448DD2,0x00448E2A)` | 88 | `43ac9598579abc817bc013e3f65ad69639f72f7bf03cbe6ca3bdd8596e5612e7` |
| event worker | `[0x00448E8E,0x00448F3C)` | 174 | `85d2ceaa34ffcbc26f644ad3ca331e5720f9cca5a3b84191cedffda9b019aeec` |
| event/thread initialization | `[0x00448F44,0x00448F78)` | 52 | `fd00bc4276ff3b9a0ebdf1f5b48dac48433f61741a3c169b694aa88642496b81` |
| CMSIS event-flags set wrapper | `[0x004495E4,0x00449642)` | 94 | `11de6c596381befd11300bd6383f97b334847c3eafc74a7392bfe956629acce7` |
| CMSIS event-flags clear wrapper | `[0x00449642,0x00449694)` | 82 | `40de3905b1832d076c51eed224d82c791e472d36de1ec4307b57cd518e54e647` |
| CMSIS event-flags wait wrapper | `[0x0044969C,0x0044971C)` | 128 | `55efe563c27f16d40c0488e9a86351c934313b894a1428c89ddde96194ea8a08` |

The queue lifecycle, record consumer, and event-worker/thread orchestration
are now each represented by separate production-excluded, dual-profile
clean-room candidates. This closes local semantic opacity without attributing
the G2-specific file to upstream EasyLogger or admitting its first-party
persistence fanout into production.

## Difference from authenticated upstream

Authenticated upstream declares:

```c
void elog_async_output(uint8_t level, const char *log, size_t size);
```

It uses a private byte ring buffer. When async mode is enabled, levels at or
above its configured threshold are placed into that ring and notice is sent
only if at least one byte was accepted. Other cases call
`elog_port_output` synchronously.

The G2 entry instead has `(buffer, length, level)` order, always attempts a
fixed-record submission, clamps each message to 255 bytes, attaches private
metadata, and sets an RTOS event regardless of submission success. It has no
upstream ring-buffer or synchronous-fallback behavior at this boundary.

The official upstream source remains valuable for the public EasyLogger
core and for API-level tests, but it cannot replace this G2 sink or determine
the private record ABI. The appropriate provenance classification for a new
wrapper is a clean-room G2 port adaptation informed by observed ABI and
behavior, not a claim that the wrapper itself came from upstream MIT source.

## Whole-image topology

The complete installed payload was scanned at every halfword for Thumb
`BL`, `B.W`, narrow conditional/unconditional branches, `CBZ`, and `CBNZ`.
Every byte offset was scanned for 32-bit even and odd/Thumb addresses.

| Entry | Direct `BL` callers | `B.W` or narrow callers | External interior branches | Stored entry/interior pointers |
|---:|---|---|---|---|
| `0x0044AA80` | `0x0043D968` | none | none | none |
| `0x00448D4E` | `0x0044AA88` | none | none | none |

Encoding each one-element caller list as uppercase eight-digit hexadecimal
without `0x` gives:

| Entry | Caller-list SHA-256 |
|---:|---|
| `0x0044AA80` | `afc2b1614e0bc5e95e1f2434f0ee0ce30a0a654400cdb40392af4fa5b8a32899` |
| `0x00448D4E` | `2670d4a2ca18ae826c3a359f9826321f58b9101850ab0ccb681f185f810ee769` |

There is no alternate entry, callback-table pointer, veneer, or
mid-function branch that has to move with either function.

## Recommended source boundary

For the first increment, source-own only the 24-byte sink and preserve this
behavioral skeleton:

```c
void open_cfw_g2_easylogger_async_submit(
    const char *buffer,
    uint32_t length,
    uint8_t level)
{
    (void)retained_g2_record_build(buffer, length, 0U, (uint8_t)level);
    (void)retained_os_event_flags_set(
        *(void * volatile *)0x20074570U, 0x01U);
}
```

The actual implementation should express the retained entries and globals
through the overlay's typed linker/seam mechanism rather than embedding
unreviewed function-pointer casts. Its fail-closed patch pin is:

```json
{
  "runtime_address": 4500096,
  "expected_size": 24,
  "expected_sha256": "787d13cfe59fad83061379298387393fa94266c9b31420e7f67e8e07d63f7356",
  "branch": "b_w",
  "target_function": "open_cfw_g2_easylogger_async_submit"
}
```

This step does not require caller rewriting because the entry ABI remains
unchanged.

The next coherent boundary is the builder at
`[0x00448D4E,0x00448DD2)`, while retaining allocator, enqueue, recycle,
copy, and diagnostic seams. That increment requires an oracle for every
reject/failure path, exact clamp and termination behavior, default-metadata
substitution, the always-zero return, and the fact that notification remains
the wrapper's unconditional responsibility.

Do not replace the queue cluster wholesale until concurrency tests cover
free-list exhaustion, CAS retry limits, FIFO ordering, dummy-node rotation,
255 simultaneous records, event coalescing, callback enable/disable, and
the stock omission of `level` during dequeue copying.

## Validation

All hashes asserted in the range tables were recomputed from the installed
payload in one pass. A minimal reproduction for the critical boundary is:

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
    (0x0044AA80, 0x0044AA98):
        "787d13cfe59fad83061379298387393fa94266c9b31420e7f67e8e07d63f7356",
    (0x00448D4E, 0x00448DD2):
        "9d95b63bc62e11910e39344ddea65213798d75caa4b91d5ce9cf033d09509e17",
}

for (start, end), digest in expected.items():
    body = payload[start - base:end - base]
    assert len(body) == end - start
    assert sha256(body).hexdigest() == digest
print("G2 EasyLogger async sink pins: OK")
PY

python3 third_party/easylogger/verify_snapshot.py
```

Required source-replacement tests are:

1. exact stock range and topology pins before patching;
2. AAPCS register-order tests for `(buffer, length, level)` and the builder's
   `(buffer, length, metadata, level)` call;
3. level truncation and constant-zero metadata;
4. unconditional event set after ready/null/zero-length, allocator, and
   enqueue-failure paths;
5. builder-oracle cases at lengths 0, 1, 254, 255, 256, and greater;
6. default versus explicit metadata and exact record offsets;
7. queue-capacity, FIFO, dummy-node, callback, and event-coalescing tests;
8. a target-side concurrency oracle before replacing any atomic queue body.

## Historical stock-compatible production integration

The audited stock-compatible path is now production-integrated as three
strict relocated leaves. The builder redirects `[0x00448D4E,0x00448DD2)`,
the G2 submit wrapper redirects `[0x0044AA80,0x0044AA98)`, and the upstream-
derived formatter redirects `[0x0043D574,0x0043D976)`. The manifest preserves
the exact stock splits and owns the appended closures below.

| Leaf | Apple clang 21.0.0 | exact-root Linux clang 22.1.8 |
|---|---|---|
| stock-compatible builder | `[0x007B14C8,0x007B15E2)` | `[0x007B1C1C,0x007B1D30)` |
| G2 submit wrapper | `[0x007B15E4,0x007B1602)` | `[0x007B1D30,0x007B1D4E)` |
| formatter text + read-only data | `[0x007B1604,0x007B1CF6)` | `[0x007B1D50,0x007B2346)` |

At this historical checkpoint the production builder retained the observed
enqueue-failure double-recycle path and the single-owner file was only an
alternative. The current corrected production decision is recorded below.

Every production leaf uses the strict relocation contract. The extractor
authenticates Clang's exact selected-function 8-byte `.ARM.exidx` CANTUNWIND
companion, including its local-section `R_ARM_PREL31` relocation, then
deliberately discards that metadata rather than appending it as executable
closure. Personality/data/non-CANTUNWIND and cross-function bindings are
rejected.

The Apple overlay/component/package are 121,298/3,644,694/4,423,148 bytes,
with SHA-256 `02bfc227db4ad32c51303ea0dc49f908b277b78db1f2e5d7a5108559d863b249`,
`eecf209bf4df5f61252099b16fb0a17f4493ec5db3c29eb266d07e6cf64d956b`,
and `2b1008c2fc533f1257ee58bd6d0c08b449d2e12bc57d918f101586ba1d3e3d29`.
The exact-root Linux artifacts are 123,170/3,646,566/4,425,020 bytes, with
SHA-256 `36479ef84126bc0075a2bcfa93c86591376eb4f18eb32983f84865f9d51e72e9`,
`43d02017caa63a2bbe96e7dda056fa61009abcdb2913a12b2298dde131eb0a9c`,
and `12386dc6f165053c3a308b4ec64bf2df90becf2b793a2404830a598b62b7a33d`.
Both profiles reproduced byte-identically in two builds. No hardware was
connected, flashed, reset, or executed.

## Corrected single-owner production promotion

The stock-compatible integration above is retained as historical audit
evidence. Production now selects
`runtime_easylogger_async_record_build_single_owner.c` and symbol
`open_cfw_g2_easylogger_async_record_build_single_owner` for the same complete
official span `[0x00448D4E,0x00448DD2)`. This is the explicit compatibility
policy decision anticipated by the earlier audit: enqueue is a consuming
operation, so its failure path owns recycling and the caller must not recycle
the record again. The stock-compatible double-recycle builder remains an
unselected host/audit oracle.

The source preserves all normal-path behavior and the stock ABI. Apple and
Linux each resolve exactly nine relocations covering the ready/default-
metadata globals, allocation, enqueue, two local read-only-data references,
and diagnostic output. Neither object has an undefined recycler symbol or a
recycler relocation. The submit wrapper's sole builder call now resolves to
the single-owner symbol; its event-set ordering and the official caller
topology remain unchanged.

The artifact sizes and hashes below are phase-local historical pins for the
single-owner-builder milestone. They predate the production EasyLogger
hexdump and FreeRTOS+CLI promotions and therefore are not the final combined
openCFW artifact identities. The current combined pins are authoritative in
`manifests/g2-2.2.6.10-core-source.json`.

| Profile | Builder text / relocated SHA-256 | Closure / SHA-256 | Overlay / component / package |
|---|---|---|---|
| Apple clang 21.0.0 | 216 / `1901adae035b9051d3ebbc7607919968a4e14bd5155d7582848855bb6f91f84b` | 270 / `06f9b921bc267febdb7355dabe776b562a4adcbf8219ef6560801212e2592036` | 121,706 / 3,645,102 / 4,423,556 |
| exact-root Linux clang 22.1.8 | 210 / `8b9b5681b55441c56d70118e7cd4ff500edf286e29608fe480638a704c86f709` | 264 / `0c567c5f1423e1d4580288fb4075ea200f3eb2efe0ff7ad4f6ea5791aa6f855c` | 123,558 / 3,646,954 / 4,425,408 |

The phase-local artifact SHA-256 triples are Apple
`03dd692b55204fc36f67469ece0175e981b6281123a1b20b3db592ee2dd0b44c`,
`ae123c6a119bfebd0420898aef590a9ba1fd7f7dc7da00b3d347f6573bba43ec`,
`7cf86c7311b4684eb6d2fdd4f832989317c858733f8438dc01ee649fcd1cf250`;
and Linux
`f2c33def6131981c1a283968bc02bd55cde32536f4f33a7fa3cbf905d42693fc`,
`5ff7dd5894b74573971912371f22d0b463c32552ea1037441e1de992a6a8d3b9`,
`fe49c0d9830327a0fdd0e7815a147bb6b810e27b9a9277b3bbfe9021de247a75`.
No hardware was operated.
