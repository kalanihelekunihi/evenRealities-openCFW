# G2 health mutex and common-event object recovery

Status: read-only, fail-closed closure of stock 2.2.6.10
`app\gui\health\health.c`. No overlay, package, signer, flash, BLE,
filesystem, or hardware state is changed.

## Result

The one visible 94-byte path anchor was only `health_lock_storage`. Literal
references and a stored callback recover two functions that baseline Ghidra
missed: the 90-byte `health_data_mutex_init` immediately before the anchor and
the 302-byte `Health_common_data_handler` after the 18-byte unlock helper.

The complete object is `[0x004FFBD8,0x004FFE14)`: four functions / 504
instruction bytes plus a 68-byte terminal compiler pool, for 572 physical
bytes. Recursive Thumb recovery reaches all 209 instructions with no embedded
data island.

| Function | Stock interval | Bytes | Ingress |
|---|---:|---:|---|
| `health_data_mutex_init` | `[0x004FFBD8,0x004FFC32)` | 90 | one external and one internal BL |
| `health_lock_storage` | `[0x004FFC32,0x004FFC90)` | 94 | 27 external BL sites |
| health unlock helper | `[0x004FFC90,0x004FFCA2)` | 18 | 29 external BL sites |
| `Health_common_data_handler` | `[0x004FFCA2,0x004FFDD0)` | 302 | stored Thumb pointer `0x006A4544` |

The initializer lazily calls `osMutexNew`. Lock uses `osMutexAcquire` with
`osWaitForever` and returns true only on `osOK`; unlock conditionally calls
`osMutexRelease`. The callback handles common event 0 by passing the raw
payload to the first-party health protobuf provider and, when role/display
guards pass, posting the retained six-byte service-1 template. Event 5 rejects
empty data, accepts command byte 1, and logs other values. Other event IDs are
logged as unknown.

## Dependency and commit result

No third-party definition is embedded. The 33 external direct calls terminate
as follows:

| Boundary | Calls | Source state |
|---|---:|---|
| EasyLogger diagnostics | 25 | 2.2.99-equivalent core; selected `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| CMSIS-FreeRTOS mutex wrappers | 3 | exact v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`, production source-owned |
| G2 health protobuf provider | 1 | first-party schema/dispatch over admitted nanopb 0.4.7–0.4.9.1 |
| G2 role/display/message policy | 4 | private first-party providers |

This independently confirms that all mutex behavior required by the health
object already exists in the authenticated CMSIS-FreeRTOS source admission.
The health call into `0x0055A350` is a first-party generated-schema provider;
generic nanopb is downstream of that boundary and is not reimplemented here.
The object adds no dependency family or version discriminator. Its exact
private source and producing Even commit remain unavailable.

## Topology and boundary

Fifty-eight image-wide BL sites land on reviewed entries: the initializer's
internal call accounts for one and 57 are external. The common handler has the
sole stored Thumb pointer. There are zero strict-interior BL decodes and zero
unrecovered direct targets.

The object follows the quicklist unlock helper and its 160-byte pool. Its
68-byte terminal pool contains the mutex global, exact function/diagnostic
strings, one retained path pointer, and the six-byte response-template pointer.
The next code at `0x004FFE14` is a separately pooled page-state-sync
initializer, proving the end boundary.

The production overlay contains no health object. A future clean-room
replacement must recover the service-1 record semantics and health protobuf
schema, then validate mutex concurrency and role/display gating on target.

## Reproduction

```sh
make health-closure
```

This authenticates every function, pool, path and diagnostic string, call
edge, stored callback, adjacent boundary, provider commit, and aggregate
first-party frontier. It performs no hardware operation.
