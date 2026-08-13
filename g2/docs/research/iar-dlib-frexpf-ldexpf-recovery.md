# IAR DLIB `frexpf` / `ldexpf` recovery

Status: complete stock identification, exact clean-room machine-code recovery,
and canonical Apple production admission. Linux profile recording remains an
external reviewed-toolchain gate. No device or flash operation is performed.

## Result

The 268-byte interval `[0x0059D244,0x0059D350)` contains three IAR DLIB
single-precision exponent helpers, not Translate UI source:

| Function | Interval | Bytes | Evidence |
|---|---|---:|---|
| `frexpf` | `[0x0059D244,0x0059D258)` | 20 | hard-float `s0` input/result, exponent pointer in `r0`, four external callers |
| internal binary32 decomposition helper | `[0x0059D258,0x0059D28C)` | 52 | sole call from the wrapper; returns fraction bits and exponent |
| `ldexpf` | `[0x0059D28C,0x0059D350)` | 196 | hard-float `s0` plus integer exponent, five external callers, ERANGE tail |

The code is physically bounded by the already closed ULED object's terminal
pool and the source-owned CRC-16/XMODEM leaf at `0x0059D350`. Ten direct entry
sites account for all callers, there is no stored pointer or strict-interior
ingress, and the only internal BL is `frexpf` to its decomposition helper.

The `ldexpf` implementation directly edits the binary32 exponent for normal
cases, uses a controlled VFP multiplication for subnormal results, preserves
signed zero/NaN/infinity behavior, saturates overflow, and tail-branches to the
already source-owned IAR ERANGE setter at `0x00439CB2`.

## Provenance

These are Standard C math-library functions supplied by IAR DLIB, not a public
upstream with a source commit. IAR's official ARM documentation describes DLIB
as the Standard C/C++ runtime delivered in prebuilt libraries and, depending on
the package, source form. Official IAR 5.50 release notes specifically list
VFP `frexpf` and `ldexpf` among optimized DLIB math functions. That establishes
family and long-standing lineage, but not the exact G2 archive.

The broader binary census still supports an EWARM 9.20+ floor and EWARM 9.60.2
as the leading compatibility candidate. These three bodies add no discriminator
capable of selecting an exact release, archive, or source commit. No proprietary
IAR implementation source has been imported.

This discovery expands the bounded IAR executable census from ten to thirteen
functions. The clean-room selector-isolated source at
`components/apollo_main/core_overlay/candidates/iar_runtime_float_exponent.S`
recreates all three. After resolving its BL and B.W relocations at the stock
addresses, every byte equals the authenticated 268-byte stock interval. A
Unicorn Cortex-M33/M-class replay also compares 4,000 deterministic bit-pattern
cases per entry point (12,000 executions total), including zeros, subnormals,
normals, infinities, NaNs, overflow, underflow, errno, FPSCR, and ABI-visible
register results.

The canonical Apple-clang overlay now appends 268 source bytes and replaces all
three complete stock entries through SHA-pinned B.W redirects. The resulting
overlay is 142,578 bytes (`3d5c9fe8…98ab4`), the Apollo provider is 3,665,974
bytes (`5cef32ba…10d22`), and the package is 4,444,468 bytes
(`e6472064…b94bc`). The existing Linux profile is intentionally unchanged and
excludes these three leaves: its reviewed Homebrew Clang 22.1.8 environment is
not installed locally, so Linux admission must be recorded and replayed there
rather than inferred from Apple output. This is a reproducibility/profile gate,
not a remaining semantic implementation gap.

Exact IAR release provenance remains unresolved. Exact source recovery does not
make 9.60.2 historical fact; only release-matched proprietary archives or
listing/map artifacts can discriminate that external question.

References: [IAR ARM development guide](https://updates.iar.com/SuppDB/Public/UPDINFO/007047/arm/doc/EWARM_DevelopmentGuide.ENU.pdf), [IAR 5.50 compiler release notes](https://updates.iar.com/SuppDB/Public/UPDINFO/005323/arm/doc/infocenter/iccarm.ENU.htm).

## Addendum: toolchain drift re-pin (2026-08-13)

The host toolchain moved from Apple clang version 21.0.0 (clang-2100.3.27.1)
to Apple clang version 21.0.0 (clang-2100.3.30.1) via an Xcode/CLT update.
The canonical `make core-component` rebuild under the updated compiler
reproduces the post-float-exponent-admission artifacts byte-for-byte, so the
admission set recorded above stands. The candidate tests that pinned the
pre-admission aggregate (or the old exact compiler string) were re-pinned to
the authenticated current build state:

- Apple overlay: 142,578 bytes, sha256
  `3d5c9fe87fd46cbc40bb5670653f45d3d61f9d777168aa47b70fb10712698ab4`
- Apple Apollo provider component: 3,665,974 bytes, sha256
  `5cef32ba7350e7f6476336fa6a087010e6143e3e692205215c271430aa110d22`
- Apple package: 4,444,468 bytes, sha256
  `e6472064c2536c055fb9a47efe49c9d9b553ce15ed1bc308115730454e3b94bc`
- Linux-profile expected overlay/component: 144,266 bytes
  (`4c95f20608c70a065b05837415d2d4471fc7eeeb61fa30ce1c1c9f07f717ddb9`) /
  3,667,662 bytes
  (`686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6`);
  Linux package 4,446,156 bytes
  (`2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3`),
  unchanged from the recorded Linux profile gate.

All pinned function bodies (including the three IAR exponent helpers and the
CmBacktrace adapter/get pair) are byte-identical under the updated compiler;
only aggregate positions and compiler-identity pins moved. Two test-local
linker fixture configs and the reviewed-compiler gates now record
`Apple clang version 21.0.0 (clang-2100.3.30.1)`.

Environment note: the reviewed Linux qualification container was restored on
this host by committing its originating stopped container back to
`opencfw-linux-llvm:22.1.8` after the image tag was lost; the restored image
ID is `92ccf0cddac1680db0d9912cf681735b39e729d21e052965e177fa3c97faef26`
(replacing `ab76b1cddd63c9c1…b6d36805`). The container still reports
Homebrew clang version 22.1.8 and reproduces the pinned Linux object bytes.
