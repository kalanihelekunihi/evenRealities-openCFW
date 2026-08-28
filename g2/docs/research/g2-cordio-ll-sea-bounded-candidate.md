# Apollo `0x5Dxxxx` Cordio/LL-sea bounded candidate

Status: isolated software candidate; not production-routed

License: Apache-2.0

Hardware activity: none

## Scope and evidence limit

This tranche consumes the corrected 300-function / 52,866-byte `0x5Dxxxx`
census. It does not restore the earlier LVGL hypothesis. The census attributes
102 functions / 19,222 bytes to a Cordio/LL-island topology, but explicitly
does not prove a public Packetcraft translation unit for any individual sea
function.

The candidate therefore uses a narrower admission rule: only all twelve
medium-confidence direct callees of the two Cordio census seeds are selected.
Within that closed set, only bodies whose complete behavior is mechanically
established by a small decompiled leaf are implemented. Large arithmetic,
indirect dispatch, and unresolved-call bodies remain external.

The checked-in census summary has one metadata mismatch: it records Ghidra
checksum-manifest digest `87d0befa…`, while the repository's current
authenticated 64-shard manifest is `3ff8aa90…`. Full regeneration reproduces
the per-function TSV and fails only the summary metadata comparison. This
candidate independently authenticates the current containing log and every
selected stock body, but reports `corpus_metadata_reconciled: false`; updating
the global census summary is intentionally outside this isolated tranche.

| Medium-confidence disposition | Functions | Bytes |
|---|---:|---:|
| Concrete bounded semantics | 6 | 64 |
| Typed unsupported external boundary | 6 | 9,356 |
| **Total** | **12** | **9,420** |

The remaining 288 sea functions / 43,446 bytes are not admitted by this
tranche and remain unsupported external behavior.

## Concrete candidates

| Stock range | Bytes | Exact observed semantic |
|---|---:|---|
| `[0x005D2A0A,0x005D2A18)` | 14 | if the destination is non-null and contains zero, store the supplied value |
| `[0x005D3238,0x005D323E)` | 6 | load a 32-bit field at offset `0x218` |
| `[0x005D323E,0x005D3248)` | 10 | load a 32-bit field at offset `0x214`, then add `0x0C28` |
| `[0x005D3268,0x005D3272)` | 10 | follow pointers at `+4` and `+0x58`, load a halfword at `+0x0E`, shift to Q16 |
| `[0x005D3272,0x005D327E)` | 12 | follow the pointer at `+0x218`, load word `+0x190`, shift to Q16 |
| `[0x005D327E,0x005D328A)` | 12 | follow the pointer at `+0x218`, load word `+0x18C`, shift to Q16 |

The five memory accessors use an OpenCFW reader interface instead of directly
dereferencing stock addresses. This makes read order, offsets, 32-bit address
wrapping, provider failure, and Q16 truncation host-testable without claiming
the unresolved structure type or touching hardware.

The implementation is in:

- `components/shared/cordio/runtime_cordio_ll_sea_bounded_candidate.c`
- `components/shared/cordio/runtime_cordio_ll_sea_bounded_candidate.h`

It is original OpenCFW code under Apache-2.0. The license choice is compatible
with the surrounding Cordio work; it is not evidence that these six stock
bodies have been matched to a named public Cordio source file.

## Typed external boundaries

| Stock range | Bytes | Reason for refusing semantic reconstruction |
|---|---:|---|
| `[0x005D2418,0x005D280E)` | 1,014 | large opaque direct anchor callee |
| `[0x005D2A18,0x005D2BAE)` | 406 | fixed-point interpolation behavior without recovered type/contract |
| `[0x005D3252,0x005D3268)` | 22 | six-argument indirect callback dispatch through nested tables |
| `[0x005D350C,0x005D351C)` | 16 | state clear followed by an unresolved callee |
| `[0x005D351C,0x005D352E)` | 18 | two unresolved ordered calls |
| `[0x005D4ED0,0x005D6D98)` | 7,880 | largest opaque medium-confidence body; decompiler type propagation does not settle |

These six ranges have a closed evidence table and typed eight-word provider
carrier. Missing providers return `UNSUPPORTED_EXTERNAL`; provider errors are
reported separately. No candidate casts or calls a stock absolute address.

## Qualification

The read-only analyzer authenticates:

- the official Apollo image;
- the corrected 300-function sea census and summary;
- the authenticated 64-shard Ghidra checksum manifest and containing log;
- all twelve exact ranges, byte counts, and stock SHA-256 values;
- medium-confidence direct-callee membership for exactly 12 / 9,420 bytes;
- all decompiled semantic signatures used by the six concrete candidates;
- the six external descriptors;
- Apache-2.0 declarations; and
- absence of an LVGL attribution in candidate source.

```sh
python3 tools/analyze_g2_cordio_ll_sea_bounded_candidate.py --json
python3 -m unittest -v tests.test_g2_cordio_ll_sea_bounded_candidate
```

The host tests cover write-once behavior, every exact reader address and read
order, Q16 overflow/truncation, invalid inputs, reader failures, all external
descriptors, provider success/failure, JSON output, and a freestanding object
with no undefined runtime imports.

## Remaining blockers

1. Recover positive per-module source attribution for the Cordio/LL topology
   cluster; call topology alone remains insufficient.
2. Regenerate the corrected-census summary against the current authenticated
   corpus checksum manifest and review the metadata-only delta.
3. Recover and bind the exact five structure layouts and Thumb ABI.
4. Independently implement the six opaque medium-confidence bodies before
   supplying their providers.
5. Bound the other 288 sea functions individually; they remain unsupported
   external behavior, not assumed Cordio or LVGL source.
6. Authenticate relocations, placement, function-pointer ingress, and all
   strict interior references before production routing.

No Makefile, overlay, package, global manifest, production ledger, firmware
image, or hardware state is modified by this tranche.
