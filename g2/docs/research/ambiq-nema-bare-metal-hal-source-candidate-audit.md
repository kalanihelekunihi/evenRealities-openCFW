# Ambiq Nema bare-metal HAL source-candidate audit

Status: complete bounded stock-function census and production-excluded
clean-room candidate; hardware admission remains open.

## Result

The G2 does not use either public Zephyr `nema_hal.c` as its generating port.
The stock image instead contains one contiguous 18-function, 614-byte
bare-metal/CMSIS-FreeRTOS cluster at `[0x00513F34,0x0051419A)`, SHA-256
`e669f4c7a13b2f2b15621c714cdfd42748ca8b1609f0d1013f453991c6ca88ce`.
The exact IRQ-28 vector points to `GPU_IRQHandler` at `0x00513F92`; the
register base is `0x40090000`. All individual bodies, 83 direct BL ingress
sites, the vector, constants, and complete span are checked offline by
`tools/analyze_g2_nema_hal.py`.

The cluster closes:

- interrupt stabilization, pending-bit clear, command-list ID publication,
  semaphore release, callback, and context-switch-pend behavior;
- `nema_sys_init`, including IRQ priority 4, a `1/0/type-3` semaphore, and a
  `0x1300`-byte ring (exactly 100 pending command lists);
- the 1,000 ms wait and fail-stop diagnostic;
- register read/write and last-command/submission state;
- render, assets, and CPU heap selection at `0x20000354`, `0x20000370`, and
  `0x20000338`;
- pool-aware allocation, 8/32-byte alignment, cache-policy rounding,
  destruction, clean/invalidate, range checking, and host allocation.

Simple header APIs that have no distinct body are compiler-inlined or
dead-stripped; they are not counted as unexplained functions.

## Public origin and commit boundary

Ambiq's official `ambiqhal_ambiq` history first places the relevant early
register-facing Zephyr port on the public package lineage at commit
`4e7d42766d5af90810c9cea5d774970c17d5ac14`. Its `nema_hal.c` Git blob is
`79acb73ca23bae39193a84fa7a0091ed92e45b23` (18,611 bytes; SHA-256
`4174286156d3bfa8f59e70784e2c425cc1af189b2d69c433c263f2c038bd6eb9`).
That source supplies strong API/algorithm ancestry but uses Zephyr semaphore,
heap, cache, and IRQ facilities.

The exact AmbiqSuite 5.1.0 package tree reproduced at commit `b853fded…`
contains the later GPU-driver Zephyr port, blob
`3db4d884dce154c3f4107688d8992184e67b88d5` (17,527 bytes; SHA-256
`053044dd8db3a84e57ff1c55200fdfefaef3e463361ea8de3fc238c40ed51cac`).
It is even less suitable as the stock generating source. The analyzer's
optional `--history-repo` mode authenticates both blobs and proves that
`4e7d4276…` is an ancestor of the package reproduction commit.

The correct provenance conclusion is therefore bounded: Ambiq/Think Silicon
own the Nema HAL API and algorithm ancestry, while the exact G2 bare-metal
FreeRTOS port source/commit remains private or unavailable. No public commit is
claimed as byte-generating source.

## Candidate and gates

`components/shared/lvgl/runtime_ambiq_nema_hal_candidate.c` expresses every
recovered effect through explicit heap, semaphore, cache, IRQ, and ring ports.
Focused host traces cover pool selection/alignment, range checks, exact system
initialization, and interrupt publication; Cortex-M55 compilation enforces the
16-byte Nema buffer ABI. It is deliberately not linked into production.

Remaining gates are atomic binding to the already source-owned heap/cache and
CMSIS-FreeRTOS primitives, board power/reset integration, and Apollo510 tests
for IRQ timing, cache coherency, ring wrap, retention, and rendered output.

## Reproduction

```sh
python3 tools/analyze_g2_nema_hal.py
python3 tools/analyze_g2_nema_hal.py --history-repo /path/to/ambiqhal_ambiq
python3 -m unittest -v tests.test_runtime_ambiq_nema_hal_candidate
```

All audit paths are read-only and perform no flash or device operation.
