# G2 page-manager dependency boundary

Status: complete, corpus-independent raw-image closure over the authenticated
G2 2.2.6.10 Apollo payload. This is analysis only and performs no device or
flash operation.

## Result

`framework\page_manager\page_manager.c` occupies `[0x0045EC7C,0x0045FEAC)`:
45 functions / 4,510 executable bytes plus 146 noncode bytes in four
interleaved literal pools, for 4,656 physical bytes. Ghidra found 36 of the
functions; source-order recovery adds nine, including the path-logging
registration pair `0x0045ECCA` (page-lifecycle registration with EasyLogger
records) and `0x0045F910` (a 354-byte transition driver), the callback veneer
trio `0x0045ECAE`/`0x0045ECB6`/`0x0045ECBE`, three further registered
handlers `0x0045ED4E`/`0x0045ED90`/`0x0045EE34`, and the record getter
`0x0045FE04`. Three functions reference the retained path cells `0x0045F684`
and `0x0045FE94` (7 raw references).

The preceding boundary is the closed `framework\sync\sync_framework.c` object
ending exactly at `0x0045EC7C` (g2-sync-framework closure
`[0x0045A578,0x0045EC7C)`), cross-pinned in the analyzer. The following
boundary at `0x0045FEAC` is an unanchored sub-cluster (tiny `abs` helper, two
4-byte null stubs, eight page callbacks registered in the const descriptor
table at `0x00755FE4`..`0x007560E0`, and the 216-call getter pair plus kernel
wrappers through `0x00460178`) whose literal-pool cell `0x00460118` is shared
with `0x00460178`+ code that also uses the `menu_page.c` pool at `0x0046061C`.
That sub-cluster shares no `BL` edge with this object in either direction, so
it is explicitly not claimed; it is a `menu_page.c`-side head candidate for
the owner of that object.

## Function inventory

Forty-five linked functions: the kernel quad-call wrapper `0x0045EC7C`, six
registration-table callbacks (`0x0045ECAE`..`0x0045EE34`, five of them stored
in the pool registration table `0x0045F690`..`0x0045F6A4` and one at
`0x0045FA74`), the 566-byte registrar `0x0045EF24`, the three anchored
functions `0x0045F15A`/`0x0045F3C8`/`0x45FE32`, a dense page-stack helper
band (`0x0045F58C`..`0x0045F8FC`) of getters, validators, and LVGL-backed
operations, the restored transition driver `0x0045F910`, and the record/table
helper band `0x0045FAA8`..`0x0045FE32`.

## Dependency result

The 199 direct body calls divide into 60 internal and 139 external calls:

| Provider | Calls | Provenance |
|---|---:|---|
| LVGL | 96 | selected 9.3-compatible commit `344c7c318047b7348e1be8572a9fd4260c251cfa`; object position/tree/event/animation/display/palette primitives |
| EasyLogger | 27 | selected source-equivalent commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| closed first-party | 7 | display-thread entry `0x0044228A` and sync_framework internals `0x0045BBB6`/`0x0045BBD2` |
| TLSF-backed heap wrappers | 5 | production-owned wrappers over selected TLSF `deff9ab509341f264addbd3c8ada533678591905` |
| IAR DLIB | 4 | aligned copy/fill and the bounded fail-stop seam `0x0044B0AE` |

There is no direct CMSIS-FreeRTOS or FreeRTOS-kernel edge in this object; all
locking goes through the LVGL-adjacent kernel wrapper `0x0045EC7C`, whose four
targets (`0x0044120E`/`0x0044121C`/`0x0044122A`/`0x00441238`) sit inside the
admitted LVGL-linked tranche. No reusable third-party body is embedded.

The twelve indirect calls (`0x0045ECF2`, `0x0045ED76`, `0x0045EE0E`,
`0x0045EE22`, `0x0045EEFE`, `0x0045EF12`, `0x0045F1FC`, `0x0045F482`,
`0x0045F5E6`, `0x0045FA38`, `0x0045FA52`, `0x0045FA6E`) are page-descriptor
member dispatches (`blx rN` after loading a callback field from a registered
page record); they are bounded to records installed by the registration path.

## Ingress and noncode closure

The object has 112 direct `BL` entry sites, seven stored Thumb entry pointers
(six registration-table cells `0x0045F690`..`0x0045F6A4` plus `0x0045FA74`,
all inside its own pools), zero wide-branch entries, zero strict-interior
`BL` targets, and zero noncode `BL` targets. Thirteen raw instruction-aligned
32-bit windows spell interior addresses of `0x0045ECCA`, `0x0045F876`, and
`0x0045F910`; two sit inside FreeRTOS-kernel code bytes and the rest inside
packed 16-bit data records, so none is promoted as a stored pointer.

Noncode is 146 bytes in four pools: `[0x0045F3C2,0x0045F3C8)` (6),
`[0x0045F676,0x0045F6A8)` (50; holds the path cell `0x0045F684` and the
registration table), `[0x0045FA72,0x0045FAA8)` (54; holds `0x0045FA74`),
and `[0x0045FE88,0x0045FEAC)` (36; holds the path cell `0x0045FE94`).

## Discriminator evidence and limitations

No new version or commit discriminator appears; LVGL, EasyLogger, and the
TLSF-backed heap wrappers match their already selected sources. The private
G2 producing commit remains binary-unobservable. The excluded tail
sub-cluster `[0x0045FEAC,0x00460178)` is documented above; if the
`menu_page.c` owner later proves page_manager ownership of part of it, this
closure's trailing 16-byte boundary pin will fail closed instead of absorbing
the change silently.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_page_manager.py
python3 -m unittest openCFW.tests.test_analyze_g2_page_manager
```

The analyzer pins every function body, the complete physical interval with
all four literal pools, all call and ingress topology, both object boundaries
against the closed sync-framework neighbor and the excluded tail, the two
retained-path cells, provider commits, and production-overlay exclusion.
