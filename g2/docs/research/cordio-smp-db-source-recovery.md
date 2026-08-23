# Cordio SMP pairing-database source recovery

Status date: 2026-08-23
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The linked `smp_db.c` translation unit is now closed to eleven functions and
2,952 code bytes inside `[0x00541E34,0x005429F2)`. The enclosing 3,006-byte
interval contains 54 bytes of alignment and literal data. Seven functions
retain the original source path; source order, direct callers, control-block
references, and exact semantics close four adjacent pathless bodies.

The remaining two upstream APIs, `SmpDbRemoveAllDevices` and
`SmpDbRemoveDevice`, have no stock body, caller, or stored pointer and are
classified dead-stripped rather than opaque. All eleven linked functions are
now production-routed through guarded redirects to a freestanding Apache-2.0
adapter that preserves the ten-record product ABI and r20 service event.

## Production integration

[`cordio_smp_db.c`](../../components/apollo_main/core_overlay/cordio_smp_db.c)
implements the complete linked surface as eleven independently compiled Thumb
leaves. The Apple profile adds 698 text bytes plus 14 alignment bytes and
replaces 2,952 guarded stock bytes. Relocations bind the already source-owned
zero-fill helper, authenticated WSF timer and DM address providers, and earlier
SMP database leaves; diagnostic-only trace calls are intentionally omitted
because they do not affect database state or externally visible behavior.

Five host contracts exercise initialization, record allocation/reuse, common
record fallback when all nine peer-specific slots are occupied, failure-count
timeouts, exponential backoff and maximum clamping, saturating timer service,
and pairing-failure refresh. The route analyzer pins every leaf, redirect,
source identity, G2 configuration, and hardware-evidence status.

No G2 or EM9305 hardware was accessed. Repeated-attempt timing under real WSF
scheduling, controller disconnect races, message interleaving, and peer
interoperability remain explicitly blocked by unavailable authorized physical
evidence; this is not a claim of on-device validation or overall completeness.

## Upstream and version pin

All thirteen definitions are byte-identical across AmbiqSuite R2.4.2/R2.5.1,
Packetcraft r19.02, and Packetcraft r20.05--r20.05c. The selected public source
is the Apache-2.0 r20.05c snapshot:

- commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`;
- Git blob `cbd056aaab32eab0838b2bd9bbaac872012ca06b`;
- source SHA-256
  `d73d33be7c3d64476b8edb763bb0f32f4a49b54e07a65d44cbfbc4b2deb76645`;
- tracked path `third_party/cordio/ble-host/sources/stack/smp/smp_db.c`.

The source body alone cannot distinguish releases. The compiled timer event
does: stock writes `SMP_DB_SERVICE_IND = 0x20`. Packetcraft r20 added
`SMP_MSG_INT_CLEANUP`, shifting that event from the r19/AmbiqSuite-2.5.1 value
`0x1F` to `0x20`. This independently reinforces the repository-wide r20.05+
lower bound.

Every retained diagnostic line marker—133, 167, 182, 228, 247, 270, 289,
and 333—agrees with the public file. The accurate classification is exact
Apache definitions plus r20 header ABI, product configuration, and expanded
vendor diagnostics; it is not an exact IAR object claim. Full identities are
in `tools/manifests/packetcraft-cordio-smp-db-provenance.tsv`.

## Stock function map

| Function | Stock interval | Bytes | Direct BL callers | Status |
|---|---:|---:|---:|---|
| `smpDbStartServiceTimer` | `0x541E34..0x541E50` | 28 | 2 | source-order helper closed |
| `smpDbRecordInUse` | `0x541E50..0x541E72` | 34 | 4 | source-order helper closed |
| `smpDbAddDevice` | `0x541E72..0x541FB8` | 326 | 1 | retained-path/source closure |
| `smpDbGetRecord` | `0x541FB8..0x542284` | 716 | 5 | lookup/add/fallback closure |
| `SmpDbInit` | `0x542288..0x5422C0` | 56 | 2 | 0x100-byte control-block init |
| `SmpDbGetPairingDisabledTime` | `0x5422C4..0x542418` | 340 | 1 | retained-path/source closure |
| `SmpDbSetFailureCount` | `0x542418..0x542570` | 344 | 1 | retained-path/source closure |
| `SmpDbGetFailureCount` | `0x54257C..0x5426C0` | 324 | 1 | retained-path/source closure |
| `SmpDbMaxAttemptReached` | `0x5426C0..0x54282A` | 362 | 1 | backoff/timer closure |
| `SmpDbPairingFailed` | `0x542838..0x54294C` | 276 | 5 | retained-path/source closure |
| `SmpDbService` | `0x542960..0x5429F2` | 146 | 1 | ten-record timer service |
| `SmpDbRemoveAllDevices` | no stock body | 0 | 0 | dead-stripped |
| `SmpDbRemoveDevice` | no stock body | 0 | 0 | dead-stripped |

Exact body/source hashes and all 24 BL sites are in
`tools/manifests/packetcraft-cordio-smp-db-function-map.tsv`. The linked bodies
concatenate to SHA-256
`a4713a22d25b1b8730a81fab7fb18e1c9db4d92f1e5db5ed7b0aa785bab7b23a`;
the enclosing interval hashes to
`c95c938f90cd5eb037d82d6346e2ebe63ae7d99b9962fbaa50f193e4c1f4e88c`.
No stored entry/interior pointers or exterior interior ingress were found.

## Memory layout and effective configuration

The 256-byte `smpDbCb` begins at `0x200708EC`:

```text
+0x00..+0xEF  ten records, 24 bytes each
+0xF0..+0xFF  16-byte wsfTimer_t

record +0x00  peer address[6]
       +0x06  address type
       +0x07  failure count
       +0x08  uint16 attempt multiplier
       +0x0C  uint32 lock time (ms)
       +0x10  uint32 exponent-decrement time (ms)
       +0x14  uint32 failure-count clear time (ms)

timer  +0xFA  message event = 0x20
       +0xFC  handler ID
       +0xFD  started flag
```

Stock therefore uses `SMP_DB_MAX_DEVICES=10`; every examined upstream header
defaults to three. This is a product/build override whose original definition
site remains unavailable, not an upstream release delta.

The configuration pointer at `0x200004B8` has two lifecycle states:

- boot `.data` initializer: `0x007759A4`, SHA-256
  `63afedc66e52e80b44aa4454ae9c03415c9082fef1f250ddbc4b0bf2460c2c18`,
  with 500-ms initial timeout, one maximum attempt, authentication 0;
- normal product runtime override: assigned to `0x00774D44` by the initializer
  called at `0x004B80AA`, SHA-256
  `7db420b72422b1d33d7bc86233f0a483fc1b506589168714a8d3e5503c793a3b`,
  with 3,000-ms initial timeout, three attempts, authentication 1.

Both use I/O capability 3, key lengths 7--16, 64,000-ms maximum/decrement
timeouts, and exponent 2. Keeping boot initialization separate from the later
product override prevents the two valid configurations from being conflated.

## Behavior closure

Record zero is the common fallback; specific peers occupy records 1--9.
Lookup normalizes the peer address type, compares address/type against in-use
records, allocates the first free specific record, and falls back to record
zero when full. A record is in use while failure count, lock time, or attempt
multiplier is nonzero.

Maximum-attempt handling exponentially increases the multiplier while the
configured timeout remains within the cap, sets the lock/decrement timers,
and starts the one-shot 1,000-ms service timer. `SmpDbService` performs
saturating decrements over all ten records, reduces the multiplier when its
timer expires, clears the failure count when its timer expires, and restarts
the one-shot timer when any record remains active.

## Lorelei result and reproducibility

The returned artifact is
`research/readiness/smp-db/`:

- 5,867 bytes, SHA-256
  `2e17c24aca5839ec194b16c1b392091232fac78b1970f7af225bafcd5e87d232`;
- 16 members and 15 inner payload hashes;
- two bounded ARM GCC profiles (`-Os`, `-O1`);
- eleven provider seams and zero unresolved symbols in both closure links;
- no firmware, source, decompilation, object, ELF, or cache bytes.

The Lorelei probe conservatively recorded the seven path-anchored functions /
2,688 bytes. The subsequent authenticated local/corpus closure expands that
to the complete eleven linked functions / 2,952 bytes; both numbers are kept
so the preserved artifact is represented exactly rather than rewritten.

Run from `openCFW`:

```sh
python3 tools/analyze_g2_cordio_smp_db.py --json
python3 tools/verify_research_corpus.py --json
```

The adjacent `atts_ccc.c`, `attc_disc.c`, and `dm_adv_leg.c` tranches are
closed separately. Production promotion for this module is complete offline;
the next unresolved Security unit is `smp_main.c`.
