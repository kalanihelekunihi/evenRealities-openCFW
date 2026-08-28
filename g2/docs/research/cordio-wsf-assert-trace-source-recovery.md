# Cordio WSF assert/trace source recovery

## Outcome

The G2 stock image now has exact boundaries and ingress closure for the two
linked functions from the Ambiq Cordio FreeRTOS assert/trace port:
`WsfTrace` and `WsfAssert`. Together they account for 208 authenticated code
bytes. A MIT, production-excluded behavioral candidate and focused
host/ARM tests cover both functions. No production overlay or manifest was
changed.

Official AmbiqSuite R2.4.2 and R2.5.1 carry byte-identical proprietary
Wicentric source files. They are source-family and behavior oracles only and
are not redistributed. Unlike the WSF message tranche, Packetcraft's public
Apache-2.0 implementations differ materially and are not an exact body route.
Stock `WsfTrace` matches the Ambiq implementation and configuration but its
embedded assertion line is six lines later than the archive. Stock
`WsfAssert` retains the Ambiq terminal debugger-escape loop but adds a local
EasyLogger diagnostic, hook, and reset path.

## Stock boundaries and ingress

The authority is
`blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, raw load base
`0x00437FE0`, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.

| Function/data | Stock span | Bytes | Stock SHA-256 |
|---|---:|---:|---|
| `WsfTrace` | `[0x0052A63C,0x0052A672)` | 54 | `80980ca4…71a5` |
| trace newline/path data | `[0x0052A672,0x0052A67C)` | 10 | `d47ac31e…db8c` |
| `WsfAssert` | `[0x00569A44,0x00569ADE)` | 154 | `526251ab…3406` |
| assert NOP/literal table | `[0x00569ADE,0x00569B04)` | 38 | `79487c70…d33` |

The raw halfword Thumb scan finds 126 real direct `BL` callers of `WsfTrace`;
their sorted packed-address digest is `c59e0672…1b4`. `WsfAssert` has one
direct caller, the overflow branch at `0x0052A660` in `WsfTrace`. No aligned
stored pointer addresses either entry or an interior halfword. The linked
image has no bounded `WsfPacketTrace`, `WsfToken`, or `WsfTokenService` body;
those source APIs are classified as dead-stripped rather than opaque code.

The retained paths are exact:

```text
D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\wsf\sources\port\freertos\wsf_trace.c
D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\wsf\sources\port\freertos\wsf_assert.c
```

## Recovered behavior and configuration

`WsfTrace` reserves a 1,024-byte stack buffer, performs unbounded variadic
formatting, and passes the resulting buffer itself as the next debug-print
format string. This double-format behavior is intentionally preserved for
compatibility rather than presented as a safe logging API. The unsigned
debug-print result is compared with 1,024; overflow calls
`WsfAssert(retained_trace_path, 137)`. A newline is printed afterward if the
assertion returns. This proves effective `AM_DEBUG_PRINTF` and
`WSF_TRACE_ENABLED`; the token branch was not selected.

`WsfAssert(file, line)` performs the recovered EasyLogger flag gates and:

- conditionally emits the structured and backend records, using backend mask
  `0x04800000`;
- when `file` is null, invokes the hook at global `0x2007456C` with
  `("pFile", "WsfAssert", 44)`;
- if that hook is null, emits the internal assertion record and calls the
  reset/fail-stop wrapper repeatedly if it returns; and
- otherwise enters the Ambiq volatile local escape loop, from which only a
  debugger write permits return.

Normal `WSF_ASSERT` macro sites in the already audited buffer/message units
were compiled out. `WsfAssert` remains linked because `WsfTrace` calls it
directly; its presence is not evidence that those normal macros were enabled.

## Upstream and license qualification

The strongest authenticated archive is official AmbiqSuite R2.5.1, SHA-256
`87b03680…4133`. Relevant identities are:

| File | Bytes | SHA-256 | Git blob |
|---|---:|---|---|
| `wsf_assert.c` | 1,864 | `f51b7b14…b1f` | `3ffe904be53a7d2248f6324cd96c4bcbe75c0397` |
| `wsf_assert.h` | 2,862 | `d3518013…be4` | `82020666a9b09e188743b1b82b4115a965bbe84e` |
| `wsf_trace.c` | 6,275 | `677ad691…d918` | `13d6b7720da262e55aefac109577f42ebe7b1f56` |
| `wsf_trace.h` | 15,307 | `41d28cd3…50f` | `856cfe94998813a71fc6bc2fd981c6866464a25a` |

All four files are byte-identical in R2.4.2 and R2.5.1 apart from their
ancestor directory. Their file-specific Wicentric confidential/proprietary
headers control use; none is copied into the clean candidate. Packetcraft
r19.02/r20.05 public assert/trace bodies use different trap and buffered
callback designs, so they remain API/history oracles only.

## Lorelei matrix and candidate status

Lorelei compiled the authenticated source/config lanes across 13 ARM GCC
profiles: 26 comparisons and 13 complete closure links in 2.098 seconds.
Every link had zero unresolved symbols. There were zero raw and zero
strict-normalized matches. Optimized GCC `WsfTrace` remains 18 bytes larger
than stock. The pristine archived `WsfAssert` remains 118 bytes smaller at its
best size, independently confirming that the EasyLogger extension is real
downstream behavior rather than compiler drift.

The compact artifact is
`research/readiness/wsf-assert-trace/`, 15,515
bytes, SHA-256 `c9f3ad9f…c54d`. Its 25-member checksum manifest authenticates
the full ledger, flags, source identities, provider/include closure, and
timings. It excludes proprietary source, generated objects, stock bytes, and
disassembly caches.

`components/shared/cordio/runtime_cordio_wsf_assert_trace_candidate.c/.h`
expresses only the observed behavior behind narrow logger/formatter/reset
seams. Focused tests compile it for Cortex-M4 with `-Werror`, exercise normal
trace formatting, the null-file hook, and the hook-null reset path. Both
entries are production-routed as 170 compiled bytes under five strict
relocations. Trace retains the stock formatter/debug providers; assertion
retains hook/reset/fail-stop behavior while non-ABI-compatible reconstructed
diagnostic wrappers are omitted from the production leaf.

## Reproduce

```sh
python3 tools/analyze_g2_cordio_wsf_assert_trace.py --json
python3 -m unittest -v \
  tests/test_analyze_g2_cordio_wsf_assert_trace.py \
  tests/test_runtime_cordio_wsf_assert_trace_candidate.py \
  tests/test_verify_research_corpus.py
```

This closes the linked assert/trace portion of the FreeRTOS port. A focused
inclusion census is handling the remaining EFS/math source inventory; negative
results are recorded as exclusions rather than invented stock functions.
