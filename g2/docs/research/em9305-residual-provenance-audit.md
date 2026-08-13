# EM9305 residual provenance classification audit

Status date: 2026-08-13

## Result

The [residual segment census](em9305-residual-segment-census.md) leaves 175
segments / 33,658 bytes as `stock_retained_unresolved_code_or_mixed` (15.960130%
of the 210,888-byte application).  `tools/analyze_em9305_residual_provenance.py`
now classifies every one of those segments by structural class and by a
seven-category source-ownership scheme, using only authenticated local
evidence: the official firmware blob, the authenticated whole-application GNU
ARCv2 EM objdump, the authenticated exact and link-order function maps, the
authenticated nine-entry QF/QK hook-pointer table, and the QP/C audit's
exhaustive 31-call assertion topology.  The per-segment map is
`tools/manifests/em9305-residual-provenance-map.tsv`, SHA-256
`2ac24d2abf1f4a4fbce236a82f4591a38dfdb0a71c5ca5b2f8e88bcd9a722d36`; the
canonical JSON report hashes to
`754765734aa8d24b2d6d9baf2ba733e27000fc7df7bc95e607cad0a0b2cccd36`.

| Ownership category | Segments | Bytes | Share of residual tier |
|---|---:|---:|---:|
| `proprietary_modern_controller_source_unavailable` | 130 | 30,564 | 90.807% |
| `first_party_application_retained` | 7 | 1,224 | 3.637% |
| `toolchain_or_linker_generated` | 2 | 980 | 2.912% |
| `unclassified_insufficient_evidence` | 36 | 890 | 2.644% |
| `public_upstream_redistribution_safe` | 0 | 0 | 0% |
| `sdk_oracle_matched_license_unresolved` | 0 | 0 | 0% |
| `vendor_modified_upstream_identified` | 0 | 0 | 0% |
| **Total** | **175** | **33,658** | **100%** |

The three zero-populated categories are deliberate fail-closed states, not
oversights: the residual tier is defined by the absence of any SDK archive
match, so no segment can claim an archive/oracle identity, and this analyzer
performs no public-source comparison that could justify a
redistribution-safe assignment.  Any future promotion into those categories
must arrive with its own positive match evidence and will change the pinned
census, failing the verifier closed until reviewed.

Two structural findings shape the whole tier:

1. **The tier is executable code, not data.**  No segment contains a real
   string (every ≥6-byte printable run is incidental code bytes), no segment
   contains any aligned word pointing into application text (no jump tables,
   descriptor tables, or callback arrays), and no segment contains ROM or RAM
   pointer tables.  The post-text table/data region was already separated by
   the census.  Constants survive only as inline instruction immediates.
2. **The tier is densely connected to the identified controller.**  170 of
   175 segments (33,628 bytes) fall into code-bearing structural classes;
   only five 4–8-byte items (30 bytes) remain constant/struct candidates,
   and none shows pointer-table or string content.  135 segments (31,772
   bytes) carry direct connectivity evidence — an `enter_s`/`push_s`
   prologue, entry branches or calls from identified functions, or calls
   into the identified map.  The named call frontier of the large
   segments is overwhelmingly Packetcraft controller vocabulary (`Bb*`,
   `Sch*`, `Lmgr*`, `lctr*`, `Ll*`, `Pal*`, `Wsf*`).

## Seven-category scheme

The scheme is declared in the analyzer and pinned by
`tests/test_analyze_em9305_residual_provenance.py`:

1. `public_upstream_redistribution_safe` — a positive match to public source
   with redistribution-safe terms.  Requires an exact match record; none
   exists in this tier.
2. `sdk_oracle_matched_license_unresolved` — identity established only
   through the third-party EM9305 SDK v4.2 oracle (no repository-level
   license).  Residual segments have no oracle match by construction.
3. `vendor_modified_upstream_identified` — upstream role identified, stock
   body differs.  Already covered by the link-order modified placements;
   residual segments carry no symbol identity.
4. `proprietary_modern_controller_source_unavailable` — call-topology
   evidence ties the segment to the modern Packetcraft/EM Bleu controller
   (`LL_VER_NUM=28992`, Bluetooth 5.4) or to EM vendor system/power support
   whose authoritative source is not publicly obtainable.
5. `toolchain_or_linker_generated` — MetaWare compiler runtime support or
   vector/linker artifacts; reconstructible without proprietary source once
   the compiler runtime is pinned.
6. `first_party_application_retained` — Even application-level module, hook,
   and startup glue identified by authenticated tables and call topology.
7. `unclassified_insufficient_evidence` — code or mixed bytes whose family
   cannot be established from authenticated evidence; no ownership claim is
   made.

## Proprietary modern-controller spans (category 4, 30,564 bytes)

Family split, enforced by the analyzer:

| Family hint | Bytes | Basis |
|---|---:|---|
| `packetcraft_modern_controller` | 27,542 | named Packetcraft call frontier (exact `emb_controller`/`emb_controller_iso` archives or `lctr`/`ll`/`bb`/`sch`/`lmgr` placement objects) |
| `em_vendor_system` | 2,952 | EM system/PML/protocol-timer/NVM frontier, ROM calls, or unanimous identified-neighbor family |
| `em_vendor_rom_wrapper` | 54 | tiny stubs with tail branches into the authenticated EM ROM window `[0x00100000,0x00110000)` |
| `em_vendor_rom_stub` | 16 | post-vector default-handler stub pairs at `[0x00302508,0x00302518)` |

Confidence is recorded per segment: 40 Packetcraft-family segments / 20,600
bytes are `high` (prologue or identified entry evidence plus at least three
named frontier callees), 67 / 6,942 bytes are `medium`.  Representative
high-confidence spans:

| Segment | Bytes | Named call frontier (sample) |
|---|---:|---|
| `[0x00329888,0x0032A4BE)` | 3,126 | `BbGetSchSetupDelayUs`, `BbGetTargetTimeDelta`, `BbSetBodTerminateFlag`, `LlMathDivideUint32`, `LmgrConnInit` |
| `[0x00321C30,0x0032233C)` | 1,804 | `BbGetClockAccuracy`, `LmgrBuildRemapTable`, `PalFrcDeltaUs`, `SchBleCalcAdvOpDuration` |
| `[0x0031DFD0,0x0031E5EC)` | 1,564 | `SchInsertAtDueTime`, `SchRmGetOffsetUsec`, `SchRmRemove`, `WsfMsgAlloc`, `WsfMsgSend` |
| `[0x00315FF4,0x0031636A)` | 886 | `lctrNotifyHostSubrateChangeIndFailed`, `lctrSendRejectInd`, `lctrTxCtrlPduAlloc/Queue` |
| `[0x003125A4,0x003128E2)` | 830 | `BOOT_IsAllActionHandled`, `PML_ConfigWakeByStInSysClkWithBootTimeComp`, `PML_GoToSleep`, ROM calls (EM vendor power) |
| `[0x0032B82C,0x0032BB3E)` | 786 | `CalcCrc32`, `LmgrSendPerAdvSubeventDataReq`, `LmgrSendPeriodicAdvStartInd` |

These spans call the identified Bluetooth-5.4 controller but match none of
the 48 authenticated SDK v4.2 archives.  Combined with the version evidence
in the [expanded SDK archive census](em9305-expanded-sdk-archive-census.md)
— public Packetcraft source ends at r20.05c / `LL_VER_NUM=1366` while stock
is `LL_VER_NUM=28992` — the defensible conclusion is that these are
**modern Packetcraft/EM Bleu controller bodies (and EM vendor support
routines) whose authoritative source is not publicly available**.  Family
assignment is call-topology inference, not symbol identity: individual
functions inside these spans are unnamed, and a segment's frontier family is
recorded as a hint with an explicit confidence.

**Recommendation (enforced in the analyzer's report): every category-4 span
remains an explicit hash-pinned stock retention behind the declared EM9305
controller boundary.**  Each segment's SHA-256 is pinned in the manifest and
re-verified against the official blob by the test.  This classification does
not assert that SDK binary identity equals redistribution-safe source
availability; it narrows *where* the licensed-source decision applies.
Obtaining licensed modern Packetcraft/EM source (or a redistribution-safe
release) would let future work match these spans exactly; until then they
are cut forward unchanged.

## MetaWare toolchain runtime (category 5, 980 bytes)

Two segments are compiler-runtime support, identified by instruction
vocabulary, reference patterns, and caller topology rather than by guesswork:

- `[0x00302664,0x0030299A)` (822 bytes) — a memmove backward-copy loop, a
  complete 64-bit `norm`/`divu`/`macdu` division family, 64-bit shift
  helpers, and a stack-bounds guard that compares `sp` against the
  linker-provided limits `0x0080E978`/`0x0080F978` and traps with `brk_s`.
  The analyzer requires the arithmetic vocabulary, both stack-limit
  references, and the guard opcode; any drift raises.
- `[0x00332FC4,0x00333062)` (158 bytes) — an alignment-optimized `memcpy`
  (byte/head/tail loops, no external calls) immediately followed by the
  `memset` body at `0x0033301C`; both are reached from across the whole
  application with `(dst, src, n)` / `(ptr, 0, n)` call shapes.

These are reconstructible from the pinned MetaWare T-2022.09 runtime (or
clean-room equivalents) and are the only residual bytes whose replacement
does not depend on any proprietary-source decision.

## First-party application spans (category 6, 1,224 bytes)

Seven segments are tied to the Even application by authenticated tables and
the assertion topology, not by inference:

| Segment | Bytes | Evidence |
|---|---:|---|
| `[0x0030EB8C,0x0030EC96)` | 270 | entry 0 of the authenticated nine-entry hook-pointer table; calls `BSP_Init`, PML registration |
| `[0x0030ECF8,0x0030EF12)` | 538 | entry 1 of the hook table; calls `APP_InitCopy`, `BOOT_BootUp`, NVM copy hooks, `QF_bzero`; 18 ROM calls |
| `[0x00311150,0x00311154)` | 4 | `QF_onResumeInternalHook` stub (single `b 0x00310798`), named in the QP/C audit |
| `[0x003111A4,0x003111A8)` | 4 | `QF_onStartupInternalHook` stub (single `b 0x0030482C`), named in the QP/C audit |
| `[0x00311620,0x00311634)` | 20 | `QK_onIdleInternalHook`, entry 7 of the hook table; three recovered callees per the QP/C audit |
| `[0x0030482C,0x003048AE)` | 130 | authenticated branch target of the `QF_onStartupInternalHook` stub; RAM-config load plus a 912-stride connection-table walk (`mpyuw r0,r0,912`), matching the stock-modified `lctrConnCtx_t` stride |
| `[0x0030EA08,0x0030EB0A)` | 258 | contains the authenticated `MyApp` assertion call site `0x0030EACE` (ID 181) from the 31-call topology; calls `QF_newX_`/`Q_onAssert` — `MyApp` active-object module code |

A negative guard fails closed if the already-identified `WsfOs` assertion
site `0x003140E2` (ID 653) ever enters the residual tier.

These are Even-side module/hook bodies: reimplementing them is a project
clean-room decision, not a third-party licensing question.  They remain
stock-retained; no byte is source-replaced by this audit.

## Unclassified remainder (category 7, 890 bytes)

36 segments / 890 bytes carry no family-grade evidence:

| Structural class | Segments | Notes |
|---|---:|---|
| `code_leaf_accessor` | 12 | 10–16-byte `mov_s rX,0x0080....; j_s.d [blink]; ld/st` global accessors; trivially reconstructible once ownership is known |
| `code_veneer` | 9 | 2–16-byte branch-only islands and MetaWare `memset` tail stubs; three referenced as immediates from startup registration code |
| `code_fragment` | 8 | 22–146-byte real code with entry/incoming evidence but no identified frontier |
| `code_function` | 2 | prologue-bearing code (146 and 90 bytes) with residual-only connectivity |
| `constant_or_struct_candidate` | 5 | 4–8-byte non-branch items; no pointer-table or string evidence |

Nothing in this tier is guessed: the fallback rule emits
`no_positive_code_or_data_evidence` and the category makes no ownership
claim.  Retention applies exactly as for category 4.

## Method and reproducibility

The analyzer recomputes the authenticated residual census, exact map, and
link-order placements through the existing fail-closed analyzers, parses the
hash-pinned whole-application objdump, builds incoming/outgoing reference
edges between identified code and residual segments, and applies an ordered
rule set: authenticated hook stubs and hook-table entries first, then the
hook-target and assertion-site rules, MetaWare runtime vocabulary guards,
ROM-wrapper and memset-tail small-island shapes, RAM leaf accessors, tiny
branch/constant islands, call-frontier family inference (BL frontier, then
tail-branch frontier, then ROM calls, then unanimous identified-neighbor
family as a last resort), and finally weak structural code features.  Any
rule, input, map, or classification drift raises `ResidualProvenanceError`.

```sh
python3 tools/analyze_em9305_residual_provenance.py --json
python3 tools/analyze_em9305_residual_provenance.py \
  --tsv tools/manifests/em9305-residual-provenance-map.tsv
python3 -m unittest tests.test_analyze_em9305_residual_provenance
```

Default inputs are the repository-owned Lorelei corpus under
`research/corpus/em9305/`; every input identity (firmware, per-archive
reports, input ledgers, objdump) is enforced by the underlying analyzers.
Run with `PYTHONDONTWRITEBYTECODE=1` and a Python that can import the
existing EM9305 analyzers (`/usr/bin/python3`).

## What remains gated

1. **Licensed modern controller source.**  30,564 bytes (91.0% of the tier)
   are modern Packetcraft/EM Bleu controller or EM vendor support bodies
   with no publicly obtainable authoritative source.  Only a licensed
   Packetcraft/EM source release (or a redistribution-safe modern drop) can
   convert identification into source ownership; binary archive identity
   alone does not grant that.
2. **Function-level identity inside category-4 spans.**  The two largest
   clusters are now resolved: the
   [controller cluster recovery](em9305-controller-cluster-recovery.md)
   pins ten functions / 4,920 bytes plus padding, exactly tiling
   `[0x00329888,0x0032A4BE)` and `[0x00321C30,0x0032233C)` with three
   opcode-exact, five modified, and two divergent SDK-identified bodies.
   The remaining 173 segments keep segment-level classification.
3. **Category-7 ownership.**  890 bytes (leaf accessors, veneers, fragments,
   small constants) need either MetaWare-runtime pattern matching at object
   granularity or targeted Ghidra/GNU ARC review; both are bounded
   follow-ups.
4. **MetaWare runtime pin.**  The two toolchain segments become replaceable
   once the T-2022.09 runtime objects (or reviewed clean-room equivalents)
   are admitted under the compiler-baseline decision already recorded in the
   QP/C audit.
5. **The seven-category scheme itself.**  This audit introduces the
   category labels for the EM9305 component; if the project-level taxonomy
   standardizes different labels, remapping is a mechanical manifest/schema
   change that will fail the pinned census until reviewed.

No EM9305 byte is source-replaced by this audit; all 33,658 bytes remain
hash-pinned stock retentions behind the declared controller boundary.
