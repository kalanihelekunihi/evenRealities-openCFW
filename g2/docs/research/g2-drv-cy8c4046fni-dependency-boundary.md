# G2 CY8C4046FNI touch-driver dependency boundary

Status: complete, corpus-independent raw-image closure over the authenticated
G2 2.2.6.10 Apollo payload. This is analysis only and performs no device or
flash operation.

## Result

`driver\touch\drv_cy8c4046fni.c` occupies `[0x0055B2EC,0x0055BA70)`: 23
functions / 1,754 executable bytes plus a 170-byte trailing literal pool, for
1,924 physical bytes. Ghidra found 20 of the functions; source-order recovery
adds the ops-table callbacks `0x0055B31C` and `0x0055B32E` (admitted by the
stored pointers at `0x0055B9F8`/`0x0055B9FC` inside the object's own pool)
and the read helper `0x0055B676` (direct `BL` from `0x00502F08`). Seven
functions reference the retained path cell `0x0055B9D0` (12 raw references).

The preceding boundary is deliberate: the 72-byte leaf at `0x0055B2A4` is an
IAR DLIB-style float-normalize helper (CLZ/rotate/ADC sequence, no stack
frame, no calls) reached only from two `dashboard_ext.c` functions
(`0x005026BC` and `0x00502790`); no touch-driver function calls it, and the
closed `pb_service_health.c` interval `[0x0055A558,0x0055B2A4)` stops before
it. It is therefore left unowned and this object starts at `0x0055B2EC`, the
first entry of the driver's pool-stored callback table. The following
boundary is the unanchored next object at `0x0055BA70`.

## Function inventory

Twenty-three linked functions: four pool-registered ops callbacks
(`0x0055B2EC`, `0x0055B304`, restored `0x0055B31C`/`0x0055B32E`) wrapping the
closed HAL I2C provider, five bus-ops dispatch veneers (`0x0055B340`,
`0x0055B35A`, `0x0055B374`, `0x0055B38E`, `0x0055B3A8`) that call through a
per-device ops struct, the register composer `0x0055B3EA`, the seven anchored
functions (`0x0055B400`, `0x0055B530`, `0x0055B5E4`, `0x0055B730`,
`0x0055B78A`, `0x0055B840`, `0x0055B92A`) covering controller init/reset with
`osDelay` settling, report reads, and gesture extraction, plus the public
entry helpers `0x0055B5CA`, `0x0055B64A`, `0x0055B66A`, restored
`0x0055B676`, `0x0055B6A8`, and `0x0055B6DC` (nine inbound calls from input,
gesture, dashboard, and LVGL-side consumers).

## Dependency result

The 87 direct body calls divide into 10 internal and 77 external calls:

| Provider | Calls | Provenance |
|---|---:|---|
| EasyLogger | 60 | selected source-equivalent commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| IAR DLIB | 9 | `memcpy`/`memset`; EWARM 9.20+ floor, 9.60.2 leading candidate |
| closed HAL I2C | 4 | closed `driver\hal\src\hal_i2c.c` transfer functions |
| CMSIS-FreeRTOS | 2 | exact `osDelay` seam at `0x00449376` (v10.5.1 commits `d213f261b5be6bb29a7cce8b84071706b72f4d53` / `def7d2df2b0506d3d249334974f51e427c17a41c` / `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`) |
| bounded first-party | 2 | board cache/invalidate seam `0x0053A5BE` around data extraction |

The nine indirect calls (`0x0055B356`, `0x0055B370`, `0x0055B38A`,
`0x0055B3A4`, `0x0055B3D2`, `0x0055B452`, `0x0055B45E`, `0x0055B55A`,
`0x0055B6C4`) are bus-ops dispatches: each loads a transfer function pointer
from the device ops struct (`ldr rN,[rX]` then `blx rN`) and is bounded to
ops tables installed by this driver's init path.

## Cypress provenance evidence

`CY8C4046FNI` is a Cypress/Infineon PSoC 4 CapSense controller. A web survey
finds only the ModusToolbox CAPSENSE middleware and PSoC-side PDL/middleware
sources (which run on the PSoC itself or configure its on-chip CSD hardware);
no public Cypress or Infineon host-side I2C touch-controller driver matching
this register-level client exists. The linked body is therefore treated as
Even Realities first-party private source; there is no third-party body to
admit and no version discriminator beyond the already selected providers.

## Ingress and noncode closure

The object has 50 direct `BL` entry sites, four stored Thumb entry pointers
(the callback table `0x0055B9F0`..`0x0055B9FC` inside its own pool), zero
wide-branch entries, zero strict-interior targets, zero noncode `BL` targets,
and zero raw interior word collisions. The trailing 170-byte pool
`[0x0055B9C6,0x0055BA70)` holds the retained-path cell `0x0055B9D0`, the
four-entry callback table, and register/format literals.

## Discriminator evidence and limitations

No new version or commit discriminator appears. The private G2 producing
commit remains binary-unobservable. The unowned DLIB leaf at `0x0055B2A4` is
documented above; if a future closure attributes it, this object's leading
16-byte boundary pin will fail closed rather than absorb the change.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_drv_cy8c4046fni.py
python3 -m unittest openCFW.tests.test_analyze_g2_drv_cy8c4046fni
```

The analyzer pins every function body, the complete physical interval and
literal pool, all call and ingress topology, both object boundaries against
the closed health-service neighbor and the unowned leaf, retained-path
references, provider commits, and production-overlay exclusion.
