# EM9305 MetaWare runtime-islands clean-room candidate

Status: ARCv2-EM target-compiled software candidate; not production-routed

License: MIT

Hardware activity: none

## Result

The two residual segments previously classified as MetaWare runtime support
now have an isolated clean-room semantic candidate:

| Stock range | Bytes | SHA-256 | Contents |
|---|---:|---|---|
| `[0x00302664,0x0030299A)` | 822 | `60ac29e8…3ed1d86` | `memmove`, 64-bit division cores/wrappers, 64-bit shifts, stack guard |
| `[0x00332FC4,0x00333062)` | 158 | `510d1c07…d8e70fb` | `memcpy`, `memset` |
| **Total** | **980** | — | reconstructible runtime support |

The candidate lives in:

- `components/shared/em9305/runtime_metaware_helpers_candidate.c`
- `components/shared/em9305/runtime_metaware_helpers_candidate.h`

It is original OpenCFW code under MIT. It does not contain or reproduce
MetaWare source. The authenticated stock bodies remain retained and no
production manifest, component overlay, or firmware package references this
candidate.

## Recovered entry map

The authenticated ARC objdump provides ten independently reachable entry
points. Caller/reference counts include internal runtime branches and every
whole-application branch decoded by the pinned objdump.

| Entry | Semantic candidate | Entry instruction | References |
|---:|---|---|---:|
| `0x00302664` | overlap-safe `memmove` | `enter_s` | 1 |
| `0x003026A8` | optimized unsigned 64-by-32 division core | `enter_s` | 2 |
| `0x00302748` | unsigned 64-bit division wrapper | `mov_s` | 5 |
| `0x00302760` | signed 64-bit division wrapper | `enter_s` | 1 |
| `0x003027C8` | 64-bit left shift | `bmsk.f` | 8 |
| `0x003027F4` | 64-bit logical right shift | `bmsk.f` | 14 |
| `0x00302820` | inclusive stack-bounds guard | `push_s` | 1 |
| `0x00302844` | general unsigned 64-bit division core | `b.d` | 2 |
| `0x00332FC4` | alignment-optimized `memcpy` | `xor` | 199 |
| `0x0033301C` | alignment-optimized `memset` | `push_s` | 153 |

The shift count is masked to six bits, matching the stock `bmsk.f ...,0x5`
entries. The stack guard accepts both endpoints and rejects values below
`0x0080E978` or above `0x0080F978`, matching the two unsigned `brlo` checks
before `brk_s`.

The division implementation uses a fixed 64-step shift/subtract algorithm.
It contains no C `/` or `%` operation and its freestanding host object has no
undefined runtime symbol. This prevents a future ARC build from trivially
recursing into the same division helper. Candidate edge policy follows the
observed runtime shape:

- unsigned division by zero returns `UINT64_MAX`;
- signed division wraps `INT64_MIN / -1` to `INT64_MIN`;
- signed division by zero returns `-1` for nonnegative dividends and `1` for
  negative dividends.

The last policy must still be confirmed against the exact MetaWare ARC EABI
return contract before production admission. It is explicitly tested so any
future correction is deliberate.

All eight maintained EM9305 candidate translation units have also been
compiled for ARCv2 EM with GCC 16.1.1 using freestanding, no-builtins,
section-per-function/data flags. Their checked build receipt records zero
undefined symbols and zero division, shift, multiply, or memory-runtime
imports. This closes the target-compilation and recursive-runtime-import gap;
it does not establish exact MetaWare EABI compatibility, link placement,
interior-entry routing, or production firmware ownership.

## Reproduction

The read-only analyzer authenticates the official EM9305 image, complete GNU
ARC objdump, existing residual-provenance map, both exact island hashes,
instruction vocabulary, stack constants, all ten entry instructions, every
reference count, MIT declarations, candidate API, and absence of C division
or remainder:

```sh
python3 tools/analyze_em9305_metaware_runtime_candidate.py --json
```

With `arc-linux-gnu-gcc` and `arc-linux-gnu-nm` on `PATH` (or supplied through
`OPENCFW_ARC_GCC` and `OPENCFW_ARC_NM`), the target proof and checked readiness
receipts are reproduced by:

```sh
make em9305-arc-candidates
```

The focused host suite covers:

- all overlap directions for `memmove`;
- `memcpy`/`memset` data and return values;
- boundary vectors plus 2,000 deterministic randomized unsigned divisions;
- boundary vectors plus 2,000 deterministic randomized signed divisions;
- shift counts across and beyond the 64-bit width;
- inclusive, exclusive, and inverted stack bounds;
- injected-trap behavior;
- a freestanding, no-builtins object with no undefined symbols; and
- authenticated analyzer and JSON output.

```sh
python3 -m unittest -v tests.test_em9305_metaware_runtime_candidate
```

## Remaining integration blockers

1. Recover and pin the exact MetaWare ARC EABI helper symbol names, argument
   register pairs, return register pairs, and any remainder side channel.
2. Split or route all interior entry points explicitly. Replacing only the
   two outer residual ranges would break callers that target the eight inner
   entries directly.
3. Authenticate every redirect, relocation, target placement, and caller ABI
   before adding the candidate to an EM9305 component.
4. Decide whether the production stack guard must retain an exact `brk_s`
   trap or use a reviewed OpenCFW fatal-policy hook.

No hardware test is required for this candidate stage. Hardware qualification
belongs to the later complete EM9305 firmware validation phase.
