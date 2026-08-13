# G2 shared file-runtime closure

## Result

The retained `product\s200\app\config\redirect.c` path owns the complete G2
shared file, directory, synchronized heap, and runtime-initialization object at
`[0x00474550, 0x00474EB4)`. The physical object is 2,404 bytes with SHA-256
`594ee91b915f3aca5249480e694ffb053b17537b72fff3f1fca3e338cacbb3b7`:
2,266 executable bytes across eighteen functions and 138 bytes of alignment,
mode literals, and trailing pool data.

All eighteen functions are already exact production redirects to OpenCFW
source. This closure turns that implementation fact into a path-level,
provider-level dependency result: no utility function in this retained object
remains opaque, and no third-party definition is embedded. Its transitive
dependencies terminate at authenticated CMSIS-FreeRTOS, littlefs, TLSF, and
EasyLogger selections, bounded IAR string primitives, and bounded first-party
adapter/assertion seams.

The object adds no new version discriminator. Exact historical G2 generating
commits remain binary-unobservable, but every reusable algorithm needed at the
public file-runtime boundary is already source-owned.

## Reproduction

Run:

```sh
make file-runtime-closure
```

The analyzer authenticates the official G2 2.2.6.10 image, complete bodies and
physical object, M-profile Thumb control flow, all calls and ingress, retained
path topology, both neighboring object boundaries, provenance records, and
the exact production redirect target for every one of the eighteen entries.

| Evidence | Result |
|---|---:|
| Linked / Ghidra-discovered functions | 18 / 18 |
| Path-anchored functions | 5 |
| Raw path references / referencing functions | 9 / 5 |
| Executable body bytes | 2,266 |
| Data/alignment bytes | 138 |
| Physical bytes | 2,404 |
| Reachable instructions | 864 |
| Direct calls | 132 |
| Internal / external direct calls | 8 / 124 |
| Indirect calls | 0 |
| Whole-image direct `BL` entries | 644 |
| Stored entry pointers | 3 |
| Strict-interior entries | 0 |
| Production source-owned functions | 18 / 18 |

The concatenated body SHA-256 is
`5fd2d6ab6b12aaff1ad96cccffee0c3fd5519dcdb064e684f2d8c33ec8b3ffe7`.
The instruction topology digest is
`de955d35e9e218aeffd4cadc5baaccd0d07ce78b7d7c635d504966032a2d39cd`.
The direct-call digest is
`cbeafb5f6b090240e27585fb00fff0b2572da7b7d438c7adb1f914ecc1bebc66`;
the direct-entry digest is
`7cc5b01e9a58767e0b50a2857e1e47d06541d575db340d91d3f76fb8b92db279`.

## Complete source-owned surface

| Stock entry | Source-owned role |
|---:|---|
| `0x00474550` | file open |
| `0x004745F4` | file close |
| `0x00474634` | file read |
| `0x00474682` | file write |
| `0x00474814` | file seek |
| `0x00474870` | file tell |
| `0x004748B4` | file size |
| `0x00474910` | file flush |
| `0x0047498C` | path remove |
| `0x00474A02` | path rename |
| `0x00474A76` | directory create |
| `0x00474B02` | directory open |
| `0x00474BB8` | directory read |
| `0x00474C66` | directory close |
| `0x00474CD2` | synchronized allocation |
| `0x00474D16` | synchronized free |
| `0x00474D54` | synchronized reallocation |
| `0x00474D9C` | file/heap mutex initialization |

The file-write machine code ends at `0x00474802`; two zero alignment bytes
precede the four padded single-character mode strings `r`, `w`, `a`, and `+`.
The 120-byte trailing pool ends exactly at `0x00474EB4`, where the separate
cache-control object begins. This accounts for all physical bytes without
assigning the preceding display/file diagnostic pool to the runtime.

The three stored ingress pointers target the heap allocator, free wrapper, and
runtime initializer. No stored pointer or external branch reaches a strict
function interior.

## Provider closure

| Provider | Calls | Qualification |
|---|---:|---|
| CMSIS-FreeRTOS mutex wrappers | 36 | exact v10.5.1 source-owned entries |
| EasyLogger controls/output plus private compact hook | 30 | 24 upstream-derived logger calls and six separately closed G2 compact calls |
| Production errno/log helpers | 32 | bounded OpenCFW source replacements |
| IAR DLIB string helpers | 6 | `strncpy` and substring search only |
| G2 file-backend adapters | 14 | first-party adapters over selected littlefs |
| TLSF allocation/free/reallocation | 3 | exact production source redirects |
| G2 assertion helper | 3 | bounded first-party port seam |

The authenticated reusable baselines are:

- CMSIS-FreeRTOS v10.5.1 commit
  `d213f261b5be6bb29a7cce8b84071706b72f4d53` over FreeRTOS-Kernel commit
  `def7d2df2b0506d3d249334974f51e427c17a41c`;
- littlefs v2.10.1-equivalent commit
  `0494ce7169f06a734a7bd7585f49a9fa91fa7318`;
- TLSF v3.1-compatible commit
  `deff9ab509341f264addbd3c8ada533678591905`; and
- EasyLogger 2.2.99-compatible commit
  `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`.

The G2 backend adapters remain first-party code, so the littlefs commit is a
source-equivalent backend baseline rather than their generating commit. The
six calls to `0x0043CE9E` remain private compact-log integration, not upstream
EasyLogger source.

## OpenCFW implication

The compact-log port can bind directly to this existing production API. More
broadly, future first-party closures should treat the eighteen file/runtime
entries as source-owned terminal providers rather than reopening littlefs,
TLSF, mutex, errno, or directory-wrapper analysis. The remaining hardware
gates are the already documented non-destructive mount, golden external-flash,
power-loss, and concurrency validations; they do not represent an opaque local
implementation gap in this object.

No device, signing, flashing, erase, or runtime operation was performed.
