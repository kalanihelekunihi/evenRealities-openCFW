# Goodix goodix_mem integrator-glue correlation

Snapshot: 2026-08-13.

## Closure

The Goodix GH3X2X SDK memory-pool manager (`goodix_mem`/`GdMem`, common DSP support library;
R1 carries config tag `gh3x2x-v2.23_7ecd2a`) declares
`extern void Gh3x2xPoolIsNotEnough(void)` as an integrator-supplied callback and clears its pool
through an integrator byte-fill. Those two bodies are R1 product glue, not Goodix provider code.
All allocator internals and Goodix consumer call-site glue are routed to the
`goodix_gh3x2x_candidate` licensed-provider gate by
[`SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md`](../boundaries/SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md);
this record covers only the two integrator-authored bodies.

| Body | Extent | Evidence |
| --- | --- | --- |
| `0x0002E952` fatal handler | `0x0002E952..<0x0002E964` + `0x00092670..<0x000926AA` (scatter-loaded, 76 executable bytes), SHA-256 `ca349eab17fd792348a0b4a99d260adb2f2e9c65bfb85aacf80fec4d0bad5369` | logs `sensor_algo_mem_fatal, info1: %u`, flushes the log, then a terminal loop; it is the integrator-supplied `Gh3x2xPoolIsNotEnough` |
| `0x00092B60` byte-fill | 12 bytes (ledger-pinned) | plain zero-fill loop; reached through a two-byte thunk whose sole caller is `goodix_mem_init` pool clearing |

Both are `r1_product_specific` / `clean_room_behavior_only` in the ownership ledger.

## Clean-room contract

- `r1_goodix_pool_fill(destination, length)` (`src/r1_goodix.c`): NULL-safe zero-fill. The
  recovered body is a byte-fill; the clean-room equivalent is an explicit zero loop (the
  freestanding Cortex-M4 build has no C library headers), so the pool-clearing seam keeps an
  explicit R1 name without duplicating a toolchain primitive.
- `r1_goodix_pool_not_enough(ops, info1)`: records the redacted diagnostic code through the
  `record` sink first, then invokes the platform `halt` hook, which is not expected to return on
  target. The portable implementation contains no busy loop; the stock terminal loop is preserved
  as a platform-owned halt so host tests can observe ordering and return normally.

Security properties: `info1` is a vendor diagnostic code, not sensitive data, and is passed
through unmodified to the integrator sink; no keys, health data, or identities are logged. NULL
operations structures and NULL sinks degrade to a no-op rather than a fault.

Host coverage: `test_goodix_mem_integrator_glue` in `tests/test_openr1.c` pins the NULL no-op,
zero-length no-op, exact fill span, record-before-halt ordering, single halt invocation, and
`info1` passthrough.

## Provider boundary

The Goodix pool manager itself — `GdMemInit`/`Malloc`/`Free`/`Realloc`/`GetFreeSize`, the
`goodix_mem_*` wrappers, and the Goodix consumer call-site glue — remains
`vendor_source_required_not_redistributable`: the module ships binary-only under a restrictive
license (use limited to Goodix ICs, no reverse engineering of binary forms). Nothing here
reimplements allocator behavior; these two seams are the only integrator-authored bodies, and the
pool fatal path is never reachable in openR1 until a licensed Goodix provider is integrated.

## Reproducible evidence

```sh
cd r1 && python3 tools/evidence/summarize_r1_sensor_algorithm_heap.py
```

The summarizer authenticates the application image, the executable extents and SHA-256 pins, the
`SENSOR_ALGORITHM_HEAP_ROUTING` per-entry dispositions, and the integrator-supplied split recorded
above.
