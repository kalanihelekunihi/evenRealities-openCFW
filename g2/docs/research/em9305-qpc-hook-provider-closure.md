# EM9305 QP/C named hook-provider closure

Status: software-only, named fail-closed boundary; not production-routed

Candidate license: MIT

Hardware validation: blocked by unavailable physical evidence

## Result

Two first-party QP/C hook shells now have narrower provider identities. The
software-only WSF provider has a clean-room implementation; the UART and
voltage-monitor providers remain physical-platform boundaries:

| Stock hook | Bytes | Exact provider evidence | Readiness decision |
|---|---:|---|---|
| `QF_onResumeInternalHook` at `0x00311150` | 4 | tail branch to `PalUartResume` at `0x00310798` | typed named external boundary |
| `QK_onIdleInternalHook` at `0x00311620` | 20 | calls `wsfOsRunIdleTasks`, then `VoltMon_DoMeasurement(0)`, then an exact no-op target | typed named external boundary |

The hook ranges remain part of the existing 22-span / 1,854-byte typed
external class. Naming a provider from an authenticated binary archive does
not itself make exact source available or establish redistribution authority.
The clean-room WSF implementation is admitted from authenticated behavior,
not from the private archive body. Retained-byte totals remain unchanged until
production image routing is implemented.

## Authenticated archive identity

The analyzer pins the EM/Packetcraft controller comparison report, its source
archive identity, and the stock EM9305 image. The archive was built with the
MetaWare T-2022.09 build 004 / LLVM 14.0.6 toolchain at `-Os`.

The report gives one unique normalized stock match for each named provider:

- `PalUartResume`: 66 bytes from `pal_uart.c.obj`, 34 compared bytes and 32
  relocation-masked bytes, stock body SHA-256
  `23bcfb3077b378b2decc8d547be03076e80f063f7d1ee73a7e9d963a54935261`;
- `wsfOsRunIdleTasks`: 58 bytes from `wsf_os.c.obj`, 54 compared bytes and 4
  relocation-masked bytes, stock body SHA-256
  `fd62056a4f17372fc978f7b17fefe03de7588d015413e78a3e298dd232b6cd38`;
- `VoltMon_DoMeasurement`: 104 bytes from `pml_volt_monitor.c.obj`, 80
  compared bytes and 24 relocation-masked bytes, stock body SHA-256
  `5607dec62c9b662938b071e0d5f2deb0ac728650d4939d3b60b070b7af39a88e`.

The authenticated later archive carries proprietary notices and does not
supply redistribution authority for OpenCFW. The public Packetcraft r20.05c
snapshot at commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` is not proven to
be the exact G2 checkout. Its Apache-2.0 bare-metal WSF loop nevertheless
independently confirms the public mechanism of invoking registered idle checks
and reducing their activity results.

## Clean-room WSF idle provider

The 58-byte stock body at `0x00333D7C` authenticates a compact state layout at
`0x00806060`: three callback pointers at offsets 0, 4, and 8, a callback count
at offset 12, and a pending byte at offset 13. When pending is clear it returns
zero. Otherwise it invokes each non-null registered callback in order, ORs bit
zero of each result, stores the final bit back to the pending byte, and returns
that bit.

The MIT implementation and bounded registration API are in:

- `components/shared/em9305/runtime_wsf_idle_tasks.c`
- `components/shared/em9305/runtime_wsf_idle_tasks.h`

It rejects corrupt counts above the authenticated three-entry capacity and
has no MMIO, absolute addresses, allocation, or undefined runtime imports.

## Clean-room adapter

The MIT adapter is isolated in:

- `components/shared/em9305/runtime_qpc_hook_provider_candidate.c`
- `components/shared/em9305/runtime_qpc_hook_provider_candidate.h`

It accepts explicit callbacks instead of referencing absolute stock addresses.
The resume boundary requires `pal_uart_resume`. The idle boundary preflights
the WSF and voltage-monitor callbacks, preserves the authenticated order, and
passes zero to `VoltMon_DoMeasurement`. It intentionally ignores both callback
returns because the authenticated stock hook performs both calls
unconditionally; the WSF return is an activity bit, not an error status.

Both later idle edges are now bounded exactly:

- `0x003100EC` branches to `0x003119A8`, whose delay slot sets `r0 = 0`
  before tail-branching to the uniquely matched `VoltMon_DoMeasurement` body at
  `0x00313AE4`;
- `0x00310728` sets `r0 = 16` before tail-branching to `0x003101E8`, whose
  complete four-byte body is `j_s [blink]; nop_s`. The clean-room model
  therefore needs no third external provider and performs no state change for
  this final edge.

## Reproduction

```sh
python3 tools/analyze_em9305_qpc_hook_provider_candidate.py --json
python3 -m unittest -v tests.test_em9305_qpc_hook_provider_candidate tests.test_em9305_wsf_idle_tasks
python3 -m unittest -v tests.test_em9305_source_readiness
```

The focused suite compiles both candidates freestanding with warnings as
errors, requires no undefined runtime imports, exercises every missing-provider
path, checks bounded registration, one-bit reduction, exact idle ordering and
its zero argument, mutates the
archive match to prove the analyzer fails closed, and verifies machine-readable
output. No production overlay, package, firmware image, or hardware state is
changed.

## Remaining blockers

1. Implement the hardware-specific `PalUartResume` and
   `VoltMon_DoMeasurement` providers only from authorized platform evidence.
2. Prove the exact ARC ABI, power-state ordering, placement, and all
   direct/interior callers before image routing.
3. Keep production routing disabled until those gates close. Future UART
   resume, WSF concurrency, power-manager ordering, and cold-boot
   checks remain physical acceptance requirements when hardware qualification
   is authorized; they are currently blocked by unavailable physical evidence.
