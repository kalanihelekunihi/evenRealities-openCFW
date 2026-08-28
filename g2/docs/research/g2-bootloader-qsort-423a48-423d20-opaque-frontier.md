# G2 bootloader qsort opaque-frontier boundary

The sequential bootloader frontier at the time of this audit began at
`0x00423A48`. The first
complete cluster is 728 bytes: a 704-byte recursive introsort core at
`[0x00423A48,0x00423D08)` and a 24-byte ISO C `qsort` wrapper at
`[0x00423D08,0x00423D20)`. Their authenticated SHA-256 values are
`9c13dd0e980154026e6c64019ce90997dcbd5abafb79aabbbf7d3def82215bb8` and
`ebab1f26584cfab24667fa6bd4a9c63641d5676a46affda15c6478a5d697d474`.

## Census and ABI evidence

The initial retained parent region `[0x00423A48,0x00426506)` was 10,942 bytes.
The next authenticated source leaf is the AmbiqSuite MSPI interrupt-clear
entry at `0x00426506`. The later retained parent region
`[0x00426536,0x00434477)` is 57,153 bytes. The separate earlier complete body
`[0x0042308E,0x004232C8)` remains 570 bytes and is not silently counted as
literal data.

The public wrapper has the ordinary four-argument ABI
`qsort(base, count, width, compare)`. Its sole aligned direct caller is
`0x0041FA22`, where the authenticated boot-initializer runner sorts eight-byte
records with comparator Thumb pointer `0x0041F9F1`. The wrapper rejects null
base and comparator pointers, duplicates `count` as the core's initial depth
budget, passes `width` as the fourth register argument, and passes the
comparator as the fifth stack argument.

The core recursively calls itself at `0x00423BD0` and `0x00423C58`; its third
ingress is the wrapper call at `0x00423D1A`. Its closed helper graph calls the
already source-owned sort3, swap, rotate3, rotate-front, and Floyd heap-sift
leaves, plus the authenticated memory-copy entry. The body selects median
pivots, partitions equal records, limits recursion, falls back to heap sort,
and finishes small partitions with insertion-style rotation.

## Fail-closed provider and license decision

The body is attributable to the IAR DLIB compiler-runtime family, but the
exact EWARM release and archive option remain unresolved. No release-matched
IAR source or archive is available under authenticated redistribution terms.
The existing `runtime_target_scalar_candidate.c` contains an MIT clean-room
insertion-sort `qsort` for production-excluded link tests. It is a useful
behavior oracle, but it is not the same algorithm and does not reproduce the
retained target body.

Accordingly this initial wave did not route, copy, or relicense the stock bytes
and did not claim source ownership. The MIT header and descriptor under
`research/admission/bootloader_opaque_frontier/` preserve the exact public and
internal ABI while returning
`OPEN_CFW_BOOT_QSORT_EXACT_PROVIDER_UNSUPPORTED`. Admission requires either a
release-matched IAR provider with adequate redistribution authority or an
evidence-backed exact in-place clean-room implementation reviewed separately.

That second condition has since been met: the reviewed MIT
clean-room implementation in `runtime_memory_qsort_423a48.c` now reproduces
both bodies exactly under both toolchain profiles and is production-routed.
The typed unsupported descriptor remains as fail-closed chronology and must not
be treated as the current qsort admission status. A subsequent concurrent
admissions source-owned the hardware-control bodies and state mapper through
`0x00423E40`; the current retained parent region consequently begins at
`0x00423E40` and is 9,926 bytes. The separate stage-one through Wave 4
frontier analyzers pin that supersession and preserve their provider,
toolchain, and redistribution boundaries.

No package manifest, overlay, provider binary, signing path, or hardware path
is changed by this boundary.
