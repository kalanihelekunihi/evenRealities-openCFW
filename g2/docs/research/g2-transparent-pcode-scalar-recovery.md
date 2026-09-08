# Decompiled C scalar-operation recovery

Date: 2026-09-07. Compatibility input: G2 `s200_v2.2.6.10`.

The experimental transparent-source runtime now implements the missing
`CARRY4`, `SCARRY4`, `SBORROW4`, `CONCAT15`, and `CONCAT16` helpers. The
concatenation implementation also masks the low operand to its declared byte
width. Previously, a five-byte value carried in `uint64_t`, for example, could
set bits belonging to the high operand.

These are clean-room MIT C implementations of Ghidra's documented p-code
operations, following the upstream
[Decompiler Concepts](https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/Features/Decompiler/src/main/help/help/topics/DecompilePlugin/DecompilerConcepts.html)
semantics. They are not missing firmware library exports. Overflow predicates
use unsigned 32-bit arithmetic and sign-bit tests, avoiding signed C overflow.
No Ghidra implementation source is copied, and no historical firmware library
commit is inferred from these helpers.

## Verification

`make -C g2 transparent-test` passes all 27 tests. The new tests compare the
three predicates with Python's unbounded integer arithmetic on 64 boundary
pairs and 10,000 seeded random pairs; verify five odd-width concatenations on
boundary and randomized inputs; and compile all tested helpers for Cortex-M55
with no undefined ELF symbols. Four actual recovered consumers also compile
and relocate within their authenticated stock envelopes, collectively
exercising all five added helpers.

A same-compiler `-Oz` comparison against the previous runtime header covers
122 affected recovered translation units. Undefined references to the five
new helpers decrease from 58 to zero. Successfully placed units increase from
32 to 52, with no placement regressions. The 20 newly placed functions cover
7,316 stock bytes and produce 4,954 compiled bytes. These figures describe the
bounded `-Oz` comparison, not the full image's optimization-variant census.
The [checked comparison summary](g2-transparent-pcode-scalar-comparison.json)
records the compiler, baseline commit, header hashes, and every newly placed
function. The full local per-function evidence is in
`build/transparent-pcode-recovery/comparison/report.json`.

Header SHA-256 before:
`b25058b5b48db4d6ae5552768439fad5b982f131e253c27a8174cf33bd42b5fe`.
Header SHA-256 after:
`d2fa40880014418691dc120aa6564dabbdbbf5308da7ac2348dd850d7df28b33`.

Rebuild the experimental image with:

```sh
make -C g2 transparent-image TRANSPARENT_BUILD_DIR=build/transparent-pcode-recovery
```

The completed full-image build places 5,145 functions, compared with 5,125 in
the previous ledger. It emits 711,144 compiled-code bytes, 194,970 padding
bytes, 2,128,548 vendor-derived data bytes, and 488,734 trap bytes. Trap
coverage decreases by 7,316 bytes. The 3,523,396-byte experimental image has
SHA-256 `9bab3c4ac4929f0d896adb1855f88e1c689c7d4256245118becf2ec10eca4275`.
The [aggregate ledger](../transparent-source-ledger.md) was regenerated using
`tools/report_transparent_coverage.py` from this completed build.

Separately, the existing hybrid production profile was rebuilt with
`make -C g2 source` and authenticated using:

```sh
python3 g2/tools/open_cfw.py verify-artifacts \
  --manifest g2/manifests/g2-2.2.6.10-core-source.json \
  --output-dir g2/build/source --toolchain-profile apple-clang
```

Its package is 4,750,780 bytes with SHA-256
`1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771`;
7,822 flash regions are placed and zero are unresolved. This verifies the
existing working-tree production build; the experimental helper change is
not routed into that package and does not increase its production coverage.
The LC3 production replay, atomic component, and scalar runtime tests also
passed: 12 tests run, one skipped.

## Remaining boundary

Helper semantics and placement do not establish the behavior of the surrounding
decompiled functions. Recovered signed expressions, register and stack
artifacts, SIMD helpers, processor operations, split functions, and size
constraints still require review. No placeholder implementation is supplied
for processor operations whose recovered ABI remains unverified.

The transparent image remains experimental and contains explicit traps and
vendor-derived data. The hybrid package still retains original code. Neither
result establishes complete source recovery or a hardware-qualified runnable
replacement. No hardware operation was performed.
