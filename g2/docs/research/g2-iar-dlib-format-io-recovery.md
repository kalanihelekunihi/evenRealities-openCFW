# IAR DLIB formatted-I/O bounded audit

Scope: official G2 `2.2.6.10` Apollo-main image. Status: bounded audit
complete for all twelve `iar-dlib` formatted-I/O cluster units; one unit
already production-recreated, eight units clean-room recreation candidates
with explicit admission conditions, three units retained as bounded licensed
runtime. No device or flash operation is performed.

This audit closes follow-up frontier #3 of the
[Apollo unanchored-function provenance census](g2-apollo-unanchored-census.md)
to the same standard as the thirteen bounded IAR runtime units of the
[IAR DLIB runtime census](iar-dlib-runtime-census.md): exact physical
identity, full topology, provenance evidence, behavioral contract, and a
per-unit provider decision.

## Result

The census identified the cluster by five functions that reference the IAR
DLIB Annex-K diagnostic strings, plus six single-family topology neighbours
and one link-order sandwich member — twelve functions, 7,496 envelope bytes
(7,462 official opaque bytes; the 34-byte `string_scanf_wrapper` body is
already production source-owned, hence zero opaque bytes in the census).
The bounded audit refines that identification into twelve exact units:

| Unit | Span | Bytes | Evidence | Ingress (raw BL / verified / unverifiable) | Decision |
|---|---|---:|---|---|---|
| `bounded_printf_wrapper_a` | `[0x0044B728,0x0044B766)` | 62 | topology, medium | 156 / 115 / 41 | clean-room-recreate |
| `bounded_printf_wrapper_b` | `[0x0044B76C,0x0044B7A2)` | 54 | topology, medium | 3 / 3 / 0 | clean-room-recreate |
| `string_scanf_wrapper` | `[0x00475FC0,0x00475FE2)` | 34 | topology, medium | 7 / 3 / 4 | **recreated-production** |
| `printf_core` | `[0x00481836,0x004824EE)` | 3,256 | string-signature, high | 4 / 4 / 0 | licensed-retention |
| `unbounded_printf_wrapper` | `[0x004B4728,0x004B4762)` | 58 | topology, medium | 75 / 65 / 10 | clean-room-recreate |
| `scanf_core` | `[0x004D1638,0x004D2112)` | 2,778 | string-signature, high | 1 / 1 / 0 | licensed-retention |
| `scanset_matcher` | `[0x004D2112,0x004D2158)` | 70 | sandwich, low | 2 / 2 / 0 | clean-room-recreate (candidate qualified) |
| `scanf_string_helper` | `[0x004D2158,0x004D22FC)` | 420 | string-signature, high | 1 / 1 / 0 | clean-room-recreate (conditional) |
| `constraint_dispatcher` | `[0x004D40A0,0x004D40BC)` | 28 | string-signature, high | 3 / 3 / 0 | clean-room-recreate |
| `strtod_engine` | `[0x00542C20,0x00542D0C)` | 236 | topology, medium | 1 / 1 / 0 | licensed-retention |
| `hexfloat_scanner` | `[0x00585410,0x005855E2)` | 466 | string-signature, high | 2 / 1 / 1 | clean-room-recreate (conditional) |
| `default_output_printf_wrapper` | `[0x00595A34,0x00595A56)` | 34 | topology, medium | 2 / 2 / 0 | clean-room-recreate (conditional) |

Raw ingress is the image-wide BL/B.W scan (257 sites total, all BL; zero
B.W).  "Verified" sites sit inside a corpus function whose decompilation
tokens name the unit entry (201); "unverifiable" sites are raw BL-shaped
bytes inside Ghidra's rejected oversized envelopes where decompilation
cannot corroborate them (56, dominated by wrapper A's 41 and the unbounded
wrapper's 10 — consistent with the format-heavy logging code the oversized
envelopes overlap).  Both halves are pinned by count and caller-address
digest.  No image word stores any unit entry or its Thumb pointer form, and
the only strict-interior branch from outside an owning unit is a
mid-instruction decode artifact (the bytes at `0x005C87E0` are the second
half of a 32-bit `mul` at `0x005C87DE` inside corpus function
`FUN_005c877a`), pinned as such.

## Physical identity

Each unit's exact body span and SHA-256, instruction census, external BL/BLX
call set, DLIB string materialization sites (`addw`/`adr` PC-relative forms
plus the IAR self-relative PIC `ldr [pc]` + `add pc` idiom), remaining
PC-relative literal loads, and 8/16 bytes of leading/trailing boundary
context are re-derived from the authenticated image on every analyzer run
and fail closed on any drift.  Adjacent data spans that form the cluster's
physical identity are pinned as evidence spans:

- the constraint-handler pool word `0x20074F10` and the
  `" constraint handler: bad message"` string overlapping its top byte
  (`[0x004D40BC,0x004D40E0)`);
- the `scanf_s` diagnostic string island (`[0x004D22FC,0x004D2362)`);
- the hex-float scanner's exponent-cap literal (`100000000`) and nibble map
  (`[0x005855E4,0x005855E8)`, `[0x00585600,0x00585616)`);
- the `strtod` engine's binary64 constants (`[0x00542D0C,0x00542D44)`);
- the errno island `0, 0x20074F14, 0x20074F14, 0`
  (`[0x00439CD0,0x00439CE0)`) shared with the bounded runtime census.

The `scanf_core` carries a 22-byte inline literal/jump-table window at its
tail (`[0x004D20FC,0x004D2112)`), separately hashed; every other unit is
code to its boundary.  Ten DLIB diagnostic strings anchor provenance; each
occurs exactly once in the image at its pinned address.

## Topology and behavioral contract

All twelve units are leaf-ward shims or self-contained engines around two
cores; the wrappers install a state record and a callback and tail through
the core.  Recovered contracts:

- **`printf_core`** (`0x00481836`): DLIB printf formatter engine —
  `(writer_callback, state, format, va_list_cursor, secure_flag)` —
  materializing `printf: bad %n argument` (8 sites), `printf_s: bad %s
  argument`, and `printf_s: %n disallowed`.  Its 31 external BLs reach the
  DLIB helper sea (`0x0048262C`/`0x00482684`/`0x00482518`,
  `0x004D41xx`/`0x004D43xx` float and locale helpers), much of which lies
  inside the rejected oversized envelopes.  Only four callers: the four
  wrappers below.
- **`bounded_printf_wrapper_a`** (`0x0044B728`): `vsnprintf`-family wrapper.
  Builds a four-word state `{cursor, remaining, would_be_count,
  va_list_cursor}`, installs the bounded writer callback at `0x00439C8A`
  (increment would-be count; if remaining, store byte, advance cursor,
  decrement remaining — the 26-byte leaf filling the gap between
  `__aeabi_memcpy` and the EDOM setter), NUL-terminates on exit, returns
  the would-be count on success and the negative core status on constraint.
  156 raw callers — the firmware's dominant logging path.
- **`bounded_printf_wrapper_b`** (`0x0044B76C`): same contract with a
  three-word state and a different `va_list` hand-off layout; 3 callers.
- **`unbounded_printf_wrapper`** (`0x004B4728`): `vsprintf`-family wrapper;
  installs the unbounded writer at `0x004397C6` (store byte, advance
  cursor), NUL-terminates, returns `cursor - base` on success or the
  negative core status; 75 raw callers.
- **`default_output_printf_wrapper`** (`0x00595A34`): `vprintf`-family
  15-instruction shim; installs the stream writer at `0x005FA008`
  (forwards to the low-level I/O sea at `0x005F9FA4`, returns state or 0 on
  short write) and passes `secure=1`.
- **`scanf_core`** (`0x004D1638`): DLIB scanf scanner engine —
  `(reader_callback, cursor, format, arguments, secure)` — materializing
  four `scanf_s` diagnostics and PIC-referencing the floating-point
  diagnostic at `0x007514CC`.  Sole caller: `string_scanf_wrapper`.
- **`string_scanf_wrapper`** (`0x00475FC0`): `vsscanf`-family wrapper;
  installs the computed reader callback at `0x00439BC6` (read: return byte
  and advance, `-1` at NUL; unread: retract cursor).  **Already clean-room
  recreated and production-redirected** by
  `components/apollo_main/core_overlay/scan_string.c`
  (`open_cfw_scan_string`, patch site `replace_scan_string`, SHA-pinned
  34-byte full-span B.W redirect): the stock body carries zero official
  opaque bytes.  This is the in-cluster precedent that the remaining
  recreation decisions follow.
- **`scanset_matcher`** (`0x004D2112`): pure `%[...]` membership leaf — no
  calls, no literals, no writes.  Walks the compiled scanset table as range
  triples (`lo '-' hi`, match iff `lo <= ch <= hi`) and single literal
  bytes; windows under three remaining bytes match as literals only, so a
  trailing `-` loses its range meaning; `ch` is masked to eight bits
  (stock `UXTB`).  Returns 1/0.  Called only by `scanf_string_helper`
  (2 sites).
- **`scanf_string_helper`** (`0x004D2158`): Annex-K aware `%s`/`%c`/`%[`
  string-conversion helper; materializes the size and argument `scanf_s`
  diagnostics and PIC-references `scanf_s: bad %c, %s, or %[ argument`.
  Sole caller: `scanf_core`.
- **`constraint_dispatcher`** (`0x004D40A0`): Annex-K dispatcher — if the
  message argument is NULL substitute the default diagnostic; dispatch
  through the SRAM handler cell `0x20074F10` (four bytes below the bounded
  census's errno word `0x20074F14`) with `(msg, NULL, 34)`; if no handler
  is registered, fall back to the retained default handler at `0x00541B74`
  (inside a rejected oversized envelope); always return 34.  Three callers,
  all Annex-K violation paths: the `printf_s` site in `printf_core`, the
  `scanf_s` site in `scanf_core`, and the `scanf_string_helper`.
- **`strtod_engine`** (`0x00542C20`): `strtod`-family binary64 parse engine
  with five external calls: four into decimal/hex classification and
  combination helper entries (`0x00585134`/`0x00585258`/`0x00542A80`/
  `0x004D4208`) that sit inside rejected oversized envelopes, and one into
  the cluster's own `hexfloat_scanner`.
- **`hexfloat_scanner`** (`0x00585410`): hexadecimal mantissa/exponent
  scanner (`%a`, `strtod` hex path); three `adr` references to the
  `0123456789abcdefABCDEF` digit table at `0x005855E8`, 7-hexit grouping
  with a rounding nibble, and the `100000000` exponent cap.

## Provenance

The Annex-K `_s` diagnostic spellings and the constraint-handler message are
emitted only by the IAR DLIB runtime; no vendored or first-party translation
unit contains them (each string occurs exactly once, image-wide).  The
self-relative PIC `ldr [pc]` + `add pc` idiom the wrappers use to install
their callbacks is the IAR compiler's position-independent literal form.
Combined with the retained `D:\01_workspace\s200_ap510b_iar_git\...` source
paths, this keeps the cluster inside the runtime census's honest
classification: **EWARM 9.x likely, 9.20+ floor, exact release unknown** —
this audit adds no release discriminator.  DLIB is proprietary IAR runtime;
no IAR source or object bytes have been imported.  All recreation is
clean-room behavioral re-expression from the bounded disassembly, exactly
the standard the thirteen prior runtime units met.

## Provider decisions

Precedent: all thirteen previously censused IAR runtime units were
clean-room recreated and production-redirected (memory, math/errno, float
exponent tranches), and the in-cluster `string_scanf_wrapper` is already
recreated and production-integrated.  The decisions therefore default to
recreation, with retention only where the qualification burden or the
dependency boundary makes recreation presently unjustifiable:

- **Recreated-production (1):** `string_scanf_wrapper` — done; stock body
  is fully redirect-owned.
- **Clean-room-recreate (8):** the four small output wrappers, the scanset
  matcher, the scanf string helper, the constraint dispatcher, and the
  default-output wrapper.  Each is a compact shim or leaf with an
  enumerable contract.  Admission conditions per unit:
  - wrapper A/B: ship the bounded writer callback at `0x00439C8A`, return
    the would-be count on success and the negative core status on
    constraint, and pass Unicorn differential qualification per the
    memory/math precedent;
  - unbounded wrapper: ship the writer at `0x004397C6`, return
    `cursor - base` on success;
  - scanset matcher: reproduce the range-triple walk, the sub-triple
    literal tail, and both exit codes — **done**, see below;
  - scanf string helper: conditional on clean-room `strchr`
    (`0x00481818`) and `memchr` (`0x004D40E0`) leaves, which sit inside
    rejected oversized envelopes, and the small unanchored ctype leaf at
    `0x004D58AE`, which is not yet a bounded unit;
  - constraint dispatcher: dispatch through SRAM cell `0x20074F10`, fall
    back to the retained default handler at `0x00541B74`, return 34;
  - default-output wrapper: conditional on the retained stream-writer
    boundary at `0x005FA008`; the wrapper itself is a 15-instruction shim.
- **Licensed-retention (3):** `printf_core`, `scanf_core`, `strtod_engine`.
  Retention here is a *bounded* boundary, not an open-ended one:
  1. their helper callees (float formatting/parsing, locale, scanset
     support) lie inside the rejected oversized envelopes and are not yet
     bounded units, so a recreation could not be qualified against a
     closed contract;
  2. exact `printf`/`scanf` floating-point and `strtod` binary64 rounding
     behavior makes the differential-qualification burden an order larger
     than any previously admitted unit;
  3. production reachability is fully enumerated: `scanf_core` is reached
     only through the already-redirected `string_scanf_wrapper`, and
     `printf_core` only through the four wrappers above — the retention
     boundary can be enforced at the wrapper layer.  Recreation of the
     cores stays gated on bounding the helper sea (oversized-envelope
     classification is census frontier #7).

## Scanset-matcher clean-room candidate

[`iar_dlib_scanset_matcher.c`](../../research/candidates/iar_dlib_scanset_matcher.c)
is a host-compilable GPL-3.0-only behavioral recreation of the
`scanset_matcher` leaf, written from the recovered table-walk contract (not
decompiler output).  It lives in `research/candidates/`, which is not
covered by `research/MANIFEST.sha256` (the index lists corpus and readiness
evidence only), so no index regeneration was required or performed.

Qualification: the authenticated 70-byte stock body was executed under
Unicorn 2.1.4 on the Lorelei host (Cortex-M Thumb mode, stop-at-LR harness)
over a deterministic 4,022-vector stream — 22 directed scanset edge cases
(range edges, `'-'` in every position, sub-triple tails, reversed ranges,
`ch > 0xFF` UXTB masking) plus 4,000 seeded random tables (lengths 0–24,
`ch` up to `0x1FF`).  The host-compiled candidate reproduces all 4,022
stock verdicts: stream SHA-256
`a6b61024db97f4f2cde71c88d8b7276a4f19dd0fff1c5bc0a3aa1865b5d51929`,
results SHA-256
`9a6be0ba5dc0e399717bce0ef4d79a2792bcb084830bab3ec5f76a397d41dde9`
(204 matches).  The disposable remote transport directory is
`/var/tmp/opencfw-scanset-qualify`; the pinned digests, not that path, are
the evidence identity.  Before production admission the candidate still
needs the standard gates: selector-isolated target build, section pins in
both reviewed toolchain profiles, and a SHA-guarded full-span redirect —
its two call sites inside the retained `scanf_string_helper` also pin the
stock callback ABI.

## What remains before production admission

1. Wrapper A/B, unbounded wrapper, constraint dispatcher: candidate source,
   Unicorn differential qualification, dual-toolchain section pins,
   guarded redirects (per the memory/math precedent).
2. Scanset matcher: the integration gates above; behavioral qualification
   is complete.
3. Scanf string helper and default-output wrapper: their conditional leaves
   (`strchr`/`memchr`/ctype, stream writer) must first be bounded out of
   the rejected oversized envelopes.
4. The three retained cores: no production work until the DLIB helper sea
   inside the oversized envelopes is bounded (census frontier #7); exact
   EWARM release identification remains independently open
   (20% per the runtime census).

## Reproduction

```sh
python3 tools/analyze_g2_iar_dlib_format_io.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifest tools/manifests
python3 -m unittest -v tests.test_analyze_g2_iar_dlib_format_io
python3 -m unittest -v tests.test_iar_dlib_scanset_matcher_candidate
```

The analyzer authenticates the official image
(`36c5b0e4…78a27863`), re-derives every pin from it, cross-pins the twelve
`iar-dlib` rows of the unanchored census manifest, and — with
`--ghidra-corpus` — authenticates the 64-shard corpus `SHA256SUMS` and the
per-unit caller verification split.  Any drift raises `AuditError`.  Note:
this increment also repaired two latent comprehension defects in the
previously committed analyzer (a stale loop variable in the ingress count
and an undefined name in `map_tsv`) that prevented its fail-closed checks
from executing at all; every pin it now enforces is unchanged.

Machine-readable output:
[`tools/manifests/g2-iar-dlib-format-io-map.tsv`](../tools/manifests/g2-iar-dlib-format-io-map.tsv)
— per-unit span, size, digest, instruction/BLX census, ingress census,
string references, and provider decision.

## Limitations

- The 56 unverifiable raw ingress sites cannot be corpus-corroborated until
  the oversized envelopes they live in are classified; they are pinned by
  digest so any change fails closed.
- Envelope shape remains a Ghidra analyzer artifact; the audit trusts the
  census envelopes because every unit's boundary context, string island,
  and inline data window is pinned byte-for-byte.
- The scanset candidate is qualified against stock behavior over the
  deterministic vector stream, not yet over target-compiled sections; the
  production gates above still apply.
- Provider decisions are justified by the existing recreation precedent and
  the bounded reachability argument; they are not a legal determination
  about DLIB licensing, which the project-level ownership model already
  records as "licensed or proprietary dependency".
