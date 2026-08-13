# IAR DLIB and compiler-runtime census

Scope: official G2 `2.2.6.10` Apollo-main image and current openCFW overlay.
Status: bounded code-unit census fully source-recreated and production
integrated; exact IAR release remains unproven.

## Result

The image definitively came from an IAR-oriented project tree: retained source
paths use `D:\01_workspace\s200_ap510b_iar_git\...`. No IAR, ICCARM, EWARM,
or DLIB release string is present in the authenticated image, so the project
path proves the toolchain family but not a release number or library variant.

The image contains three independent application build banners at
`0x0078A3AC`, `0x0078B594`, and `0x0078B984`: all say `Jul  6 2026`, with
times `21:37:47`, `21:37:52`, and `21:37:30`. The nearby
`2025-04-28T13:29:15Z`/`c205a2` pair is embedded component-version metadata,
not the application build timestamp. The three July 2026 banners are the
stronger temporal bound and are now fail-closed analyzer inputs.

IAR's official release history makes EWARM 9.x temporally plausible, and IAR
published the 9.60 line in September 2024. IAR 9.70 was also available before
the authenticated July 2026 build. A separate Apollo510/AmbiqSuite 5.3 build
environment nevertheless names EWARM/ICCARM 9.60.2 specifically, showing that
the newer compiler was not automatically selected for Apollo510. That makes
9.60.2 the leading compatibility candidate, followed by 9.60.3, 9.70.x, and
9.50.x for archive comparison. This ranking is supporting evidence, not proof
that the AmbiqSuite 5.1.0-derived firmware used 9.60.2. The current honest
classification remains `EWARM 9.x likely; exact release unknown`.

The current 9.60 information center identifies 9.60.3 as the maintained
product-package documentation and separately states that 9.60.2 was the first
public 9.60 release. This confirms that 9.60.2 and 9.60.3 are distinct archive
comparison points; it does not supply a library-byte discriminator. The Ambiq
environment's explicit 9.60.2 selection therefore remains the reason to test
9.60.2 first rather than silently treating all 9.60 updates as equivalent.

IAR's public release history first lists formal Cortex-M55 support in EWARM
9.20. If the unrecovered project selected the named Cortex-M55 processor
variant, 9.20 is therefore a practical lower bound; a generic Armv8-M target
would weaken that inference. The public 9.40, 9.50, and 9.60 release entries
do not disclose a `sqrtf`, errno, or general DLIB-math correction that can
separate those releases.

## Inferred library configuration

IAR documents math archives as
`m{arch}_{mode}{endian}[fp][rwpi][abi][pacbti].a` and runtime-support archives
as `rt{arch}_{mode}{endian}[rwpi][abi][pacbti].a`. The recovered code is
32-bit Thumb, little-endian, and uses VFP. It also uses absolute errno pointer
literals, which excludes both RWPI and the `7Mx` no-literal-pool variant.
The strongest current archive-family inference is consequently:

- math: `m7M_tl{v|s}.a`, with full-VFP versus single-precision-only still
  unresolved;
- non-floating runtime: `rt7M_tl.a`; and
- DLIB C library: `dl7M_tl{n|f}.a`, with Normal versus Full unresolved.

These are documented filename-family constraints, not authenticated archive
identities or an exact release pin.

## Authenticated runtime boundary

| Runtime unit | Stock/source span | Bytes | Current state |
|---|---:|---:|---|
| `__aeabi_memmove` | `[0x00439710,0x004397A6)` | 150 | Fully bounded, source-recreated, and production-redirected |
| `sqrtf` | `[0x004397A8,0x004397C4)` | 28 | Fully bounded, source-recreated, target-qualified, and production-redirected |
| `__aeabi_memcpy` | `[0x00439BE4,0x00439C8A)` | 166 | Fully bounded, source-recreated, and production-redirected as disjoint public/interior spans |
| domain-error setter | `[0x00439CA4,0x00439CB2)` | 14 | Fully bounded, source-recreated, and production-redirected; preserves result registers while storing `EDOM` (33) |
| range-error setter | `[0x00439CB2,0x00439CC4)` | 18 | Fully bounded, source-recreated, and production-redirected; preserves result registers while storing `ERANGE` (34) |
| errno-address accessor | `[0x00439CC4,0x00439CD0)` | 12 | Fully bounded, source-recreated, and production-redirected; returns shared errno address `0x20074F14` |
| errno literals/alignment | `[0x00439CD0,0x00439CE0)` | 16 | Fully classified retained data; words `0, 0x20074F14, 0x20074F14, 0` |
| `frexpf` | `[0x0059D244,0x0059D258)` | 20 | Exact clean-room recreation and canonical Apple production redirect |
| internal binary32 decomposition helper | `[0x0059D258,0x0059D28C)` | 52 | Exact clean-room recreation and canonical Apple production redirect |
| `ldexpf` | `[0x0059D28C,0x0059D350)` | 196 | Exact clean-room recreation and canonical Apple production redirect; ERANGE tail preserved |
| `__aeabi_uldivmod` core | `[0x007A73C0,0x007A745A)` | 154 | Fully recreated/source compiled |
| `__aeabi_ldivmod` core | `[0x007A745C,0x007A74D6)` | 122 | Fully recreated/source compiled |
| unsigned four-register wrapper | `[0x007A74D8,0x007A74EC)` | 20 | Fully recreated/source compiled |
| signed four-register wrapper | `[0x007A74EC,0x007A7500)` | 20 | Fully recreated/source compiled |

The two memory providers use the void-EABI calling convention observed by the
firmware and are still required by the promoted LZ4 closure. Floating-point
source replacements intentionally use Apollo510 VFP instructions and do not
introduce `__aeabi_f2d` or `__aeabi_d2f` dependencies.

A clean-room source module now covers the public memcpy entry, its aligned
interior entry, and memmove. The three relocation-free target sections passed
6,000 deterministic randomized Unicorn vectors on Lorelei. Aligned and
mismatched-alignment instruction-count proxies are within about 5.2% of stock,
and all three disjoint stock spans are production-redirected in both reviewed
toolchain profiles. See the
[memory-provider source candidate audit](iar-runtime-memory-source-candidate.md).

A second selector-isolated clean-room module covers `sqrtf`, both errno
setters, and the errno-address accessor. Apple Clang 21 and Linux Clang 22.1.8
produce identical section pins. Lorelei Unicorn matched 4,000 float bit
patterns plus 1,500 randomized errno-helper executions against the
authenticated stock functions. All four leaves are installed through guarded
redirects and independently recorded Apple/Linux placement profiles. See the
[math/errno integration audit](iar-runtime-math-errno-source-candidate.md).

The added `sqrtf` body uses `VCMPE.F32`, `VSQRT.F32`, and a negative-input
tail to the domain-error setter. It has 68 direct callers. The errno setters
have ten direct or tail-call ingresses between them, and the address accessor
has 29 direct callers. `__aeabi_memcpy` has 790 calls at its public entry and
597 calls at aligned interior entry `0x00439C04`; `__aeabi_memmove` has 12
calls and one non-linking tail to memcpy. Exact caller-address digests are
enforced by `tools/analyze_g2_iar_runtime.py`.

## Lorelei/Rizin census method

A local raw-Thumb scan found 35 call targets in the early island. Lorelei then
decompiled them as 16 isolated Ghidra 12.1.2/JDK 21 shards in one SSH batch.
This separated neighboring application/DSP entropy-coder functions from the
six confirmed retained runtime code units above. Rizin independently decoded
the exact VFP, copy, errno-store, return, and literal boundaries. The remote
project/log directory is disposable evidence transport, not provenance; the
tracked analyzer reproduces all accepted byte hashes and ingress digests from
the authenticated local image.

## Completion estimate and next discriminator

| Work item | Complete |
|---|---:|
| Toolchain-family identification | 100% |
| Confirmed-unit function boundaries/ABIs | 100% (13 of 13 code units) |
| Broader compiler/DLIB runtime identification | 40–50% |
| Confirmed runtime units source-recreated | 100% (13 of 13 code units) |
| Confirmed runtime units production-integrated | 100% canonical Apple (13 of 13); Linux profile recording pending for the newest three |
| Retained executable code units in bounded census | 0% (0 of 13 code units) |
| Retained memory-provider entries with qualified source candidates | 100% (3 of 3 callable entries) |
| Newly censused float-exponent tranche production-integrated | 100% canonical Apple (3 of 3 code units) |
| Exact EWARM/ICCARM release | 20% |
| DLIB configuration/model identification | 30% |

The next efficient step is byte comparison of these compact, strongly
fingerprinted spans against legally available EWARM runtime libraries or
map/listing outputs, in priority order 9.60.2, 9.60.3, 9.70.x, then 9.50.x.
Neither the local workstation nor Lorelei currently has matching `m7M_tl*.a`,
`rt7M_tl*.a`, `dl7M_tl*.a`, `iccarm`, or `ilinkarm` artifacts installed, so
no archive-byte comparison has yet been possible. `sqrtf` plus the errno
helpers are the best release discriminator; clean-room recreation does not
remove the independent value of identifying the historical archive. The
generic EABI memory routines are more likely to be stable across releases.
Version claims must remain
probabilistic until a release-specific code-generation or library fingerprint
discriminates the candidates.

## Reproduction

```sh
python3 tools/analyze_g2_iar_runtime.py --json
python3 -m unittest -v tests.test_analyze_g2_iar_runtime
```

## Sources

- IAR Embedded Workbench for Arm release history:
  <https://updates.iar.com/filestore/standard/001/002/168/arm/doc/infocenter/iccarm_history.ENU.html>
- IAR Build Tools for Arm 9.60 product update (release date September 3,
  2024): <https://updates.iar.com/?product=BXARM&version=9.60>
- IAR 9.60.3 information center and 9.60-series release notes:
  <https://updates.iar.com/FileStore/STANDARD/001/003/381/arm/doc/infocenter/ewarm.ENU.html>
- Apollo510/AmbiqSuite 5.3 comparison environment naming ICCARM 9.60.2:
  <https://doc.embedded-wizard.de/getting-started-apollo510-evb?v=14.00>
- IAR product updates showing EWARM 9.70 availability before the authenticated
  July 2026 firmware build: <https://updates.iar.com/?product=EWARM-LE>
- IAR 9.60 development guide, DLIB/math/runtime archive naming:
  <https://updates.iar.com/FileStore/STANDARD/001/003/381/arm/doc/EWARM_DevelopmentGuide.ENU.pdf>
- IAR 9.60 information center, release history including Cortex-M55 support:
  <https://updates.iar.com/FileStore/STANDARD/001/003/381/arm/doc/infocenter/ewarm.ENU.html>
