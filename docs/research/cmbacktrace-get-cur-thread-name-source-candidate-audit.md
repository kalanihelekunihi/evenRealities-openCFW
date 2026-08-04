# CmBacktrace current-thread-name source-candidate audit

## Result

The official G2 helper at `[0x00593AF6, 0x00593AFE)` has completed its
Production promotion. The stock entry is now a single `B.W` to the bounded,
MIT-licensed `open_cfw_cmbacktrace_get_cur_thread_name` source leaf. That leaf
tail-branches to a separate source-owned adapter that exactly preserves the
recovered G2 behavior: a volatile current-TCB load at `0x20074A20`, followed
by addition of the task-name offset `0x34`. Consequently a null TCB preserves
the observed null-to-`0x34` result instead of being sanitized.

The earlier independently named candidate and candidate seam remain excluded
from every production overlay, manifest, and Makefile registration. The
authenticated CmBacktrace snapshot is likewise a compatibility oracle and is
not compiled into production. No artifact from this promotion has been used
on hardware.

The placements and aggregate artifact pins recorded below are the frozen
CmBacktrace-only promotion phase.  The later FreeRTOS+CLI console promotion
compacted the current Apple adapter/helper to `0x007B25F0` / `0x007B2600` and
the exact-root Linux adapter/helper to `0x007B2D0C` / `0x007B2D1C`; current
aggregate artifact pins are maintained in `docs/source-coverage.md` and the
canonical build reports.

## Authenticated upstream oracle and license

The oracle is extracted at test time from the vendored, offline-verifiable
CmBacktrace source rather than from a hand-written behavioral substitute:

| Item | Pin |
|---|---|
| Selected upstream commit | `73714489f9d8af130aacb515586b397b604a5768` |
| Selected tree | `541c20dbeb1165f9b2862e2b84cdc63b3d7c718f` |
| Declared upstream version | `1.4.2` development state; not an official version tag |
| License | MIT |
| Source | 26,436 bytes / `6e444224af3ef223067849b88f61281ec0661e3f38425e84758bf12be057e01c` |
| Extracted `get_cur_thread_name` slice | offset 8,261; 974 bytes / `fc81b35576ed317335f04c411907037dfaed7490dd0e90a2ca72b7deba8dceca` |

The selected commit is the newest authenticated, unmodified upstream state in
the proven G2-compatible interval from
`4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c` through
`73714489f9d8af130aacb515586b397b604a5768`.  This is an OpenCFW
compatibility-baseline choice.  It is not evidence that Even used that exact
checkout; the vendor may have used another commit in the interval or a
behaviorally compatible fork.

The extracted function is compiled with the authenticated FreeRTOS selector.
Its selected branch is exactly `return vTaskName();`.  The candidate carries
the full upstream MIT notice, and the vendored snapshot retains the upstream
MIT license.  The test first authenticates the complete source and the exact
extracted slice, then compiles the slice as the differential oracle.  Any
source, extraction-boundary, configuration, provenance, or verifier mismatch
fails closed before the oracle or candidate is exercised.

## Official boundary and dependency

The 32-byte OTA preamble is removed before address translation.  The resulting
application SHA-256 is
`19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

| Range | Size | Bytes / SHA-256 |
|---|---:|---|
| Candidate boundary `[0x00593AF6, 0x00593AFE)` | 8 | `80b5c2f699fa02bd` / `75f860b4a8f7d60464eeb5216946dbefe0875c65fb0c7a6641abdd9f9daa979b` |
| Preceding window `[0x00593AEE, 0x00593AF6)` | 8 | `9bfa80002060f1bd` / `e54578c8ef0d67d4eb13235c926437812c0fa1bdea88e04bdff8a9cfdc01739b` |
| Following window `[0x00593AFE, 0x00593B06)` | 8 | `2de9f84305000e00` / `8dda716ee93857cdfdc9faf824123a7c6ccd461fb72c60bbc0bee4be38fd7161` |
| G2 `vTaskName` adapter `[0x0045602E, 0x00456036)` | 8 | `0b48006834307047` / `a4150246c7816b7ffab201b6ae3bc6da8c6147e9a5541a921733369dd1e6c09b` |

The official helper's only outgoing call is the BL at `0x00593AF8` to
`0x0045602E`.  The adapter loads the literal slot at `0x0045605C`, whose value
is `0x20074A20`, loads the current TCB pointer, and adds the recovered task-name
offset `0x34`.  A whole-application scan finds the helper's BL as the adapter's
only direct BL caller.

## Complete ingress proof

The halfword-aligned whole-application scan found exactly four BL ingresses to
the helper entry:

| Call site | Encoding |
|---|---|
| `0x0059457E` | `fff7bafa` |
| `0x00594586` | `fff7b6fa` |
| `0x0059459E` | `fff7aafa` |
| `0x005945A6` | `fff7a6fa` |

All four are within the recovered `cm_backtrace_fault` caller region.  Their
address-list digest is
`082fc78b557ca674f0bf367869ea98c44f0b85aaff047caf1f0a3f4f62d5bfed`;
their address-plus-encoding record digest is
`7f677fa382b59698fb8a8728783ffcbe4626160d8f0c7bbc28c0c4bc9ba8d618`.
The common `[0x0059455C, 0x005945AC)` caller window is 80 bytes with SHA-256
`ec739a3bf1d609c09f128391dcbcb14b5772e3dec9462dc62a7c7c834e4b3d0b`.

The same scan proves there were no direct B.W ingresses, no external wide
conditional or narrow branch to the entry or any interior halfword, and no
stored canonical or Thumb pointer to the entry or any interior byte. Production
therefore preserves all four BL callers unchanged and replaces only the single
entry. The assembled image has exactly six relevant wide edges: those four
BLs, the stock-entry `B.W` to the new helper, and the new helper's `B.W` to its
new adapter. There is no remaining ingress to the old adapter at `0x0045602E`,
no interior branch, no conditional/narrow branch, and no stored canonical or
Thumb pointer to either new range or the two-byte alignment gap.

## Host differential and target object closure

Host tests compare production, the candidate, and the authenticated extracted
upstream source slice for null, empty, ordinary, `IDLE`, and 40-byte task-name
data. They agree for every non-null current TCB. The production adapter also
pins the recovered G2 null-to-`0x34` behavior directly.

Apple clang 21.0.0 and Homebrew clang 22.1.8 produce the same target object
under the reviewed Thumb-2 flags:

The Linux qualification was run in `opencfw-linux-llvm:22.1.8` with the
repository mounted and the test executed at the exact qualification root
`/Users/kalani/Repo/SybilSightABCD/openCFW`.  Its result was not inferred from
an object built under `/workspace` or from the Apple object.

| Property | Apple | Linux |
|---|---|---|
| Object | 1,004 bytes / `29bcaab263166fec8765c937acb907158963e5e03ff3f7d8f18161a2faaf589a` | same |
| Function section | 4 bytes, alignment 4, `fff7febf` | same |
| Function SHA-256 | `90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f` | same |
| Text relocation | offset 0, type 30 (`R_ARM_THM_JUMP24`), candidate seam | same |
| `.ARM.exidx` | `0000000001000000` / `01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d` | same |

There is exactly one executable function section, exactly one undefined symbol,
and exactly one text relocation.  The relocation is a tail branch to the
external candidate seam.  Two builds in each reviewed profile are byte-for-byte
identical.

## Production promotion result

The exact source closure is two deliberately separate leaves:

| Leaf | Target-object contract | Apple placement | exact-root Linux placement |
|---|---|---|---|
| G2 current-task-name adapter | 14 bytes, `44f62020c2f20700006834307047`, no undefined symbols or relocations | `0x007B25F4` | `0x007B2D10` |
| CmBacktrace helper | 4 unrelocated bytes, `fff7febf`, one `R_ARM_THM_JUMP24` to the adapter | `0x007B2604` | `0x007B2D20` |

Both profiles resolve the helper to `fff7f6bf`; the adapter is unchanged.
The two-byte zero alignment interval is `[0x007B2602,0x007B2604)` on Apple
and `[0x007B2D1E,0x007B2D20)` on Linux. The complete eight-byte stock range is
replaced by one profile-specific `B.W` plus two Thumb NOPs; the preceding and
following authenticated windows remain byte-identical.

| Profile | Overlay | Component | Package |
|---|---|---|---|
| Apple Clang 21.0.0 | 123,620 / `923b7774901565fe513290e23719eef52fc42566c8d49b6aeea4e1e2050fff09` | 3,647,016 / `df1c954ec9eed002669ee6c9f3bf3893dca8d1dbf28234f0f2c2858d7d257335` | 4,425,470 / `8663f87ee132fcfd80709bd32517331663f2c984c8909694eef419064567feab` |
| exact-root Linux Clang 22.1.8 | 125,440 / `d577a1faefb80857c9cf1aba83e3ae59cf90ee9747b208b8a187cd7a11bdb4ae` | 3,648,836 / `c1c6c563167c2451cb896e482dfaa58da075d6fea8ebc147dcb68dd74247da51` | 4,427,290 / `03d082df4a74448bcdfed86f4fea7d09454a03e87c9deb8ab178b444a3546222` |

The canonical manifest now tiles 881 regions exactly. It records 83 source
regions / 123,763 bytes, 37 alignment regions / 75 bytes, 574 generated entry
replacement regions / 85,282 bytes, 177 official regions / 3,437,722 bytes,
and the unchanged exact-load, exact-replacement, and container categories.
Hardware use remains disabled pending separate device-level review.
