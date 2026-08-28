# G2 Apollo510 MSPI HAL triplet candidate

Status: software-only candidate; not production-routed

Hardware activity: none

Upstream license: BSD-3-Clause

## Result

The retained Apollo-main MSPI cluster has three bounded larger bodies that
correspond structurally and topologically to the authenticated AmbiqSuite
5.1.0 `am_hal_mspi.c` translation unit:

| Stock range | Bytes | Candidate upstream function | Direct call sites |
|---|---:|---|---:|
| `[0x004C099C,0x004C0E1E)` | 1,154 | `am_hal_mspi_device_configure` | 6 |
| `[0x004C0F78,0x004C2098)` | 4,384 envelope / 4,372 Ghidra body | `am_hal_mspi_control` | 8 |
| `[0x004C240E,0x004C26D6)` | 712 | `am_hal_mspi_interrupt_service` | 3 |

This promotes the existing medium-confidence peripheral-cluster attribution
to a bounded integration candidate. It does not yet claim production source
ownership. The unmodified upstream translation unit remains the provider;
OpenCFW adds only a small BSD-3-Clause request-ABI adapter for opaque stock
callers.

The source candidate and header are:

- `components/shared/ambiqsuite/runtime_apollo510_mspi_stock_abi_candidate.c`
- `components/shared/ambiqsuite/runtime_apollo510_mspi_stock_abi_candidate.h`

Ambiq's complete BSD terms remain in
`third_party/ambiqsuite-apollo510/LICENSE`. No Ambiq implementation was copied
into the adapter.

## Recovered request translation

The G2 binary masks the control request to its low byte and accepts a stock
request ceiling of 40 before dispatch. Its enum is not the public 5.1.0 enum.
The complete recovered mapping is:

| G2 stock ordinal | AmbiqSuite 5.1.0 ordinal | Rule |
|---:|---:|---|
| `0..9` | `0..9` | identity |
| `10,11` | none | removed stock SDR250 disable/enable controls |
| `12..23` | `10..21` | subtract two |
| `24` | `22` | PIO-mixed configuration |
| `25` | `24` | clock configuration |
| `26` | `23` | device configuration; public order is swapped |
| `27..39` | `25..37` | subtract two |
| `40` | none | stock sentinel/default-invalid request |

Public requests 38 and 39 (`SCRAMBLE_CONFIG` and `SET_DATA_LATENCY`) were
added after the last stock request and have no stock-side input.

All eight direct calls to the stock control body use only four request values:

| Stock request | Calls | Public request | Meaning |
|---:|---:|---:|---|
| `16` | 2 | `14` | timing-scan set |
| `18` | 1 | `16` | XIP configuration |
| `21` | 1 | `19` | XIP enable |
| `24` | 4 | `22` | PIO-mixed configuration |

Consequently, every request currently observed at the opaque-call boundary
has a public 5.1.0 equivalent. Requests 10, 11, 40, and all invalid low-byte
values fail closed with status 6 and do not call the upstream provider.
High bytes are deliberately ignored to preserve the stock ABI. New
source-owned callers must use the named public 5.1.0 enum directly and must
not pass through this compatibility adapter.

## Reproduction

The read-only analyzer authenticates the official image, the three harvested
decompilation bundles, the upstream source and license, exact stock bounds and
hashes, all 17 direct call sites, public enum order, the adapter table, and the
requests used by the eight control calls:

```sh
python3 tools/analyze_g2_apollo510_mspi_triplet_candidate.py --json
```

Focused tests execute all 256 low-byte inputs, high-byte aliases, the four
observed dispatches, unsupported-request behavior, null seams, table-mutation
rejection, JSON output, and a freestanding Cortex-M55 compile:

```sh
python3 -m unittest -v tests.test_apollo510_mspi_triplet_candidate
```

The complete authenticated `am_hal_mspi.c` translation unit also compiles for
Cortex-M55 with API validation enabled. With the current Clang configuration,
the three upstream function sections are 564, 3,192, and 552 bytes. The full
object has 20 external HAL/CMDQ/clock/power/delay/interrupt references; section
GC reachability for the rooted triplet remains to be closed explicitly.

## Remaining integration blockers

1. Root the three upstream functions plus adapter under section GC and resolve
   only their actually reached CMDQ, clock-manager, delay, power, and interrupt
   dependencies.
2. Prove every private handle field reached by these larger bodies against the
   stock handle layout. The first-eight-byte handle prefix is already proven,
   but it is insufficient for these functions.
3. Choose an explicit policy for the unused stock-only SDR250 requests 10 and
   11: retain fail-closed behavior, implement a separately reviewed adapter,
   or prove they are unreachable after all opaque callers are replaced.
4. Authenticate target link placement, relocations, overlay space, and all
   incoming redirects before production admission.
5. Defer live MSPI, display, XIP, and interrupt qualification to the planned
   pre-release hardware-validation phase.

No production manifest, overlay, build orchestration, firmware image, package,
signature, device, or flasher was changed by this candidate increment.
