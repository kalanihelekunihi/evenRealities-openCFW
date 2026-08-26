# EM9305 QP/C ARCompact provenance audit

Status: family, QP/C 6.5.1, compiler, portable bodies, QK SWI port, and complete
cluster ownership proven. The exact official GPL-3.0-or-later portable sources
and recovered EM9305 configuration are now maintained and host-compile clean;
target replacement remains blocked by an unavailable reviewed ARC compiler.

## Result

The stock EM9305 application is Synopsys ARC EM7D/ARCv2 EM code, not Arm
Thumb. EM Microelectronic's own EM9305 datasheet describes its Real-Time
Embedded Framework as QP/C ported to ARC with minor customizations and
optimizations. Binary evidence independently recovers the canonical `qk`,
`qf_dyn`, `qf_act`, `qep_hsm`, `qf_actq`, and `qf_mem` module corpus.
Function topology also recovers the deliberately unlabeled `qf_qact.c` and
`qf_qeq.c` units through `QActive_ctor` and `QEQueue_init`; both were missing
from the earlier six-file source matrix because their module labels are
commented out upstream.

The upper release discriminator is the QK assertion-500 path at
`0x00311560...0x00311578`. It checks only that selected priority `p` is
nonzero, loads the `qk` module label at `0x0033451C`, and calls the shared
assertion handler at `0x003117D8` with ID 500. Official QP/C tags v6.0.1
through v6.6.0+ retain that precondition. v6.7.0 changes it to a compound
check of incoming and selected priorities against `QF_active_`, so v6.7.0 and
later implementations of this body are excluded.

The stock `QActive_post_` body at `[0x00310E28,0x00310EE4)` supplies the lower
discriminator. It restores the saved ARC interrupt status before its
critical-section assertion, behavior introduced in official v6.3.2, and
increments a dynamic event's reference counter before testing `status`, the
ordering introduced by official v6.3.6 commit
`5550cca87dedf72d45250ad01e9cdeee8c4140ba`. Earlier checked bodies do not
combine both properties. This narrows the checked portable-body ancestry:

| Role | Tag | Commit |
|---|---|---|
| Historical audit floor | v6.0.1 | `25636b87b0dbf4ccb015cb6eb9fb42aeb6010ef6` |
| Last earlier incompatible body | v6.3.4 | `2b231b3383d98b36585435030e7440dbade3da9b` |
| Portable-body ancestry floor | v6.3.6 | `5550cca87dedf72d45250ad01e9cdeee8c4140ba` |
| Latest compatible checked tag | v6.6.0+ | `a280d203c0f55753b18dd9fc76104936729e471a` |
| First excluded tag | v6.7.0 | `af0b6f2f00f96b9753aa1dcbe734284e6f99f25c` |

Pre-v6 and v6.0--v6.3.4 portable bodies are excluded by the recovered ordering.
The release is now independently pinned to **QP/C 6.5.1**, official commit
`416dcec8820b9cdb5827497e645d0d9375db53c6`. A public third-party EM9305 SDK
v4.2 snapshot embeds `qep.h` with `QP_VERSION 651U`, `QP_VERSION_STR "6.5.1"`,
and `QP_RELEASE 0x8E7055B4`. Its QP header blob, SDK commit, tree, and matching
symbol vocabulary are authenticated by the analyzer. The binary-derived
v6.3.6--v6.6.0+ interval remains useful independent corroboration.

This exact release pin does **not** prove EM's exact private checkout. A vendor
backport/cherry-pick and EM port modifications remain possible, and the public
snapshot is a source oracle rather than an authoritative EM repository.

Relocation-normalized comparison against the authenticated SDK archive now
confirms all 22 portable stock bodies and the substantial QF/QK hooks. The ELF
`.comment` records pin Synopsys MetaWare ARC Compiler T-2022.09 build 004,
LLVM 14.0.6, EM-Micro ARCv2 EM, and `-Os`. The archive comparison also closes
the QK SWI port and protocol-timer/QP boundary; see the
[SDK archive match audit](em9305-sdk-archive-match-audit.md).

## EM9305 SDK v4.2 source oracle

The oracle is `C0R3YY2/em9305_original` commit
`e4412bc98d4e76d441d1226ca3696e53cfae5f54`, tree
`f5cb9ba00df71c2612d6d64cf39e05615a2feb64`. It was published as a third-party
mirror and has no repository-level license declaration, so its content is not
automatically eligible for integration. Individual files carry their own
terms; license review remains a source-promotion gate.

| Oracle file | Git blob | SHA-256 | Evidence used |
|---|---|---|---|
| `emcore/bin/v4.2/standard/includes/qep.h` | `129bcda2ee271406a21a5197763974c822c2ad6e` | `94c999cea695d2803d95cf418151dd0847c4d484f84b664e81af5428cefbd986` | exact QP/C 6.5.1 macros and release code |
| `emcore/bin/v4.2/standard/includes/bsp.h` | `cd9fa65df3a6b33fbf8325adc7fd166aed8d473f` | `76e6d4af7f3bb3ea01cdb085405cd66291813118645732edcd8f5541aa43a896` | exact inline `QF_resume` control flow |
| `emcore/bin/v4.2/standard/emcore_standard.sym` | `7955274387f9d7a85708b8e18f06a977b42c168e` | `c27c8dce8445e13845c9c1d9f32db76ca30f0cffc4ceeadb0a85cf8979775828` | QF/QK hook names, sizes, and callback-global addresses |
| `emcore/custom/source/emcore_bsp.c` | `4cbe32d2c661346fb54b8502a729d3c2d8b1af10` | `45c0f2c7f9fe135bc2a6d96a64abeb73dcfc1b1e90e1424f1cff13ca6f0ba345` | extension-hook semantics in the SDK example |

Six binary archives are independently blob/SHA authenticated by the analyzer.
They confirm 98 exact functions/7,172 bytes; 92 are globally unique normalized
fingerprints/7,146 bytes. Full archive identities and per-library counts are
in the [SDK archive match audit](em9305-sdk-archive-match-audit.md).

## Authenticated stock boundaries

The package is 211,948 bytes with SHA-256
`91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9`.
Its application record occupies package `[0x424,0x33BEC)`, installs at
`[0x00302400,0x00335BC8)`, and hashes to
`0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03`.

| Installed range | Bytes | SHA-256 | Status |
|---|---:|---|---|
| `[0x00302518,0x00302664)` | 332 | `176b59324b400252aee4955eebb6e7cc8f5899a98592fe41010478170178a3e9` | QK SWI0/SWI1 ARC port exactly assigned from the SDK archive; stock retained |
| `[0x00310C00,0x003117EC)` | 3,052 | `9c5803cd925d3b575e05f7fed8b1d6c42eaac000368fc191d2092c71c65b65da` | Protocol-timer/QP cluster fully function-identified; 22 portable functions / 2,450 bytes hash-bounded; no anonymous executable bytes; approximately 80–90% semantically recovered; stock retained |
| `[0x00311554,0x003115E4)` | 144 | `844ab98ae09414027139ea278dc2cf5ae92757eed0fb7cda0d25efd06b898e2c` | QK activation/scheduling candidate with the release discriminator; stock retained |
| `[0x00310E28,0x00310EE4)` | 188 | `7b97ff5fc12c7d8504c997bc6ab414aa756a5fd9e10af97e775ffc83bad8127d` | `QActive_post_` candidate; portable ancestry floor, non-Q-SPY ABI, and ARC critical-section behavior recovered; stock retained |
| `[0x003126E0,0x003128E4)` | 516 | `3a2edcd4b08f74c6cc592a19916938ff1a96216555d0b1ca055ebb1a90366f4a` | Vendor-configured `SLEEP_MANAGER_GoToSleep`; boundary and two ARC `SLEEP` sites recovered; partially reverse engineered; stock retained |
| `[0x003128E4,0x00312918)` | 52 | `44956422195791d75f34b28115b61b7fe344318d5c00e71f0bf3f0cc477cdef5` | Exact relocation-normalized `SLEEP_MANAGER_RCCAL_Callback`; stock retained |
| `[0x00334514,0x00334550)` | 60 | `781612bc1eedf1760f7edb368325fb83cc2ecc88fbe042aeb678e2804da6805b` | Module-name table fully classified; stock retained data |
| `[0x00335B94,0x00335BB8)` | 36 | `1370d2789d143388ecbd5c84edf4dfaaaf2c059ff69ec59e0f68ff0df0514b51` | Nine-entry hook function-pointer table fully classified; stock retained data |
| `[0x003117E8,0x003117F8)` | 16 | `2deea6b7a791969cebd7a54d6da705031b568ae3bfc5bdce8bd0a7e338813727` | Full `Q_onAssertExt` boundary named from the oracle; stock retained |

The 3,052-byte range is a discovery boundary, not a claim that all QP code is
contiguous or that every byte in it is portable upstream code.

## Portable function boundary map

Vtable entries, direct-call topology, assertion identities, object offsets,
and source control flow now name and hash-pin 22 portable functions totaling
2,450 bytes, or 80.28% of the discovery cluster. These are provenance and
reverse-engineered boundaries; all stock bytes remain retained.

| Translation unit | Function | Stock range | Bytes | Status |
|---|---|---:|---:|---|
| `qf_qact.c` | `QActive_ctor` | `[0x310D18,0x310D36)` | 30 | Fully bounded/identified; stock retained |
| `qf_actq.c` | `QActive_get_` | `[0x310D38,0x310D9E)` | 102 | Fully bounded/identified; stock retained |
| `qf_actq.c` | `QActive_postLIFO_` | `[0x310DA0,0x310E26)` | 134 | Fully bounded/identified; stock retained |
| `qf_actq.c` | `QActive_post_` | `[0x310E28,0x310EE4)` | 188 | Fully bounded/identified; stock retained |
| `qk.c` | `QActive_start_` | `[0x310EE4,0x310F5A)` | 118 | Fully bounded/identified; stock retained |
| `qf_qeq.c` | `QEQueue_init` | `[0x310F5C,0x310F74)` | 24 | Fully bounded/identified; stock retained |
| `qf_act.c` | `QF_add_` | `[0x310F74,0x310FAA)` | 54 | Fully bounded/identified; stock retained |
| `qf_act.c` | `QF_bzero` | `[0x310FAC,0x310FB8)` | 12 | Fully bounded/identified; stock retained |
| `qf_dyn.c` | `QF_gc` | `[0x310FB8,0x311014)` | 92 | Fully bounded/identified; stock retained |
| `qk.c` | `QF_init` | `[0x311014,0x31105E)` | 74 | Fully bounded/identified; stock retained |
| `qf_dyn.c` | `QF_newX_` | `[0x311060,0x3110F2)` | 146 | Fully bounded/identified; stock retained |
| `qf_dyn.c` | `QF_poolInit` | `[0x3111A8,0x311216)` | 110 | Fully bounded/identified; stock retained |
| `qk.c` | `QF_run` | `[0x311230,0x31125E)` | 46 | Fully bounded/identified; stock retained |
| `qep_hsm.c` | `QHsm_ctor` | `[0x311260,0x311274)` | 20 | Fully bounded/identified; stock retained |
| `qep_hsm.c` | `QHsm_dispatch_` | `[0x311274,0x311490)` | 540 | Fully bounded/identified; stock retained |
| `qep_hsm.c` | `QHsm_init_` | `[0x311490,0x311550)` | 192 | Fully bounded/identified; stock retained |
| `qep_hsm.c` | `QHsm_top` | `[0x311550,0x311554)` | 4 | Fully bounded/identified; stock retained |
| `qk.c` | `QK_activate_` | `[0x311554,0x3115E4)` | 144 | Fully bounded/identified; stock retained |
| `qk.c` | `QK_sched_` | `[0x311634,0x31166C)` | 56 | Fully bounded/identified; stock retained |
| `qf_mem.c` | `QMPool_get` | `[0x31166C,0x3116F4)` | 136 | Fully bounded/identified; stock retained |
| `qf_mem.c` | `QMPool_init` | `[0x3116F4,0x311798)` | 164 | Fully bounded/identified; stock retained |
| `qf_mem.c` | `QMPool_put` | `[0x311798,0x3117D8)` | 64 | Fully bounded/identified; stock retained |

The remaining 602 cluster bytes include protocol-timer routines, alignment,
and vendor scheduling/idle/stop glue. They are not attributed to portable QP
merely because they are adjacent. The analyzer authenticates the exact
portable/remainder partition and labels every complement range explicitly:

| Remainder segment | Stock range | Bytes | Current state |
|---|---:|---:|---|
| Vendor-modified `ProtTimer_SetHwTriggerEnable` tail | `[0x310C00,0x310C08)` | 8 | Full 40-byte function begins at `0x310BE0`; saved-status critical section recovered; stock retained |
| `ProtTimer_StoreConfig` | `[0x310C08,0x310CEA)` | 226 | Exact relocation-normalized SDK archive body; stock retained |
| Protocol-timer alignment | `[0x310CEA,0x310CEC)` | 2 | Compiler alignment (`NOP_S`); fully classified; stock retained |
| `ProtTimer_UpdateRestartTime` | `[0x310CEC,0x310D18)` | 44 | Exact relocation-normalized SDK archive body; stock retained |
| Seven two-byte alignment islands | `0x310D36`, `0x310D9E`, `0x310E26`, `0x310F5A`, `0x310FAA`, `0x31105E`, `0x3110F2` | 14 | Compiler alignment (`NOP_S`); fully classified; stock retained |
| `QF_onResume` | `[0x3110F4,0x31114C)` | 88 | Name/size and callback slots recovered; interrupt bookkeeping partly reversed; stock retained |
| `QF_onResumeExt` | `[0x31114C,0x311150)` | 4 | Name/size recovered; empty stock hook plus alignment; stock retained |
| `QF_onResumeInternalHook` | `[0x311150,0x311154)` | 4 | Name/global slot recovered; stock branch to `0x310798`; stock retained |
| `QF_onStartup` | `[0x311154,0x31119E)` | 74 | Exact name/size corroborates `QF_run` topology; internals partly reversed; stock retained |
| Callback alignment | `[0x31119E,0x3111A0)` | 2 | Compiler alignment (`NOP_S`); fully classified; stock retained |
| `QF_onStartupExt` | `[0x3111A0,0x3111A4)` | 4 | Name/size recovered; empty stock hook plus alignment; stock retained |
| `QF_onStartupInternalHook` | `[0x3111A4,0x3111A8)` | 4 | Name/global slot recovered; stock branch to `0x30482C`; stock retained |
| Alignment after `QF_poolInit` | `[0x311216,0x311218)` | 2 | Compiler alignment (`NOP_S`); fully classified; stock retained |
| inline `QF_resume` | `[0x311218,0x311230)` | 24 | Exact SDK role recovered: disable interrupts, call `QF_onResume`, enable, idle forever; stock retained |
| Alignment after `QF_run` | `[0x31125E,0x311260)` | 2 | Compiler alignment (`NOP_S`); fully classified; stock retained |
| `QK_onIdle` | `[0x3115E4,0x31161C)` | 56 | Exact name/size recovered; ILINK race guard and sleep path partly reversed; stock retained |
| `QK_onIdleExt` | `[0x31161C,0x311620)` | 4 | Name/size recovered; empty stock hook plus alignment; stock retained |
| `QK_onIdleInternalHook` | `[0x311620,0x311634)` | 20 | Name/global slot and three callees recovered; internals partly reversed; stock retained |
| `Q_onAssert` | `[0x3117D8,0x3117E8)` | 16 | Exact 14-byte oracle size plus alignment; behavior fully reversed; stock retained |
| `Q_onAssertExt` prefix | `[0x3117E8,0x3117EC)` | 4 | First four bytes inside cluster; full 16-byte boundary continues to `0x3117F8`; stock retained |

These ranges total 602 bytes. Together with the 2,450 portable bytes they
cover all 3,052 cluster bytes without gaps or overlaps; all 26 machine-level
remainder segments are independently SHA-256 pinned in the analyzer.

The SDK symbol file names the RAM callback slots at `0x0080FE04` through
`0x0080FE1C`. Their addresses exactly match stock accesses:
`gQF_onResumeExt`, `gQF_onResumeInternalHook`, `gQF_onStartupExt`,
`gQF_onStartupInternalHook`, `gQK_onIdleExt`, `gQK_onIdleInternalHook`, and
`gQ_onAssertExt`. The terminal stock table at `[0x00335B94,0x00335BB8)` holds
the nine little-endian targets `0x30EB8C`, `0x30ECF8`, `0x31114C`, `0x311150`,
`0x3111A0`, `0x3111A4`, `0x31161C`, `0x311620`, and `0x3117E8`.

## Assertion topology

An exhaustive scan of every two-byte-aligned ARC `BL` encoding in the
application finds **31** calls to `0x003117D8`. All 31 are now assigned to a
module through 22 authenticated module-reference instructions and register
flow. Twenty-nine calls belong to portable QP/QF/QEP/QK translation units;
the remaining two are `MyApp` ID 181 and `WsfOs` ID 653.

This corrects the earlier count of 14. Rizin 0.9.1 and the experimental
Ghidra ARC extension greedily consume the legal six-byte ARCv2 EM
short-register/long-immediate form when analysis begins at an earlier
instruction. Global xrefs are therefore incomplete. Exact-address Rizin
decoding verifies every one of the 31 raw-scan results, but it is not used as
the discovery authority.

| Module | Calls | Recovered IDs | Call addresses |
|---|---:|---|---|
| `MyApp` | 1 | 181 | `0x30EACE` |
| `qf_actq` | 5 | 100, 110 (twice), 210, 310 | `0x310D4E`, `0x310D78`, `0x310DBE`, `0x310E3A`, `0x310E60` |
| `qk` | 5 | 189, 300, 410, 500, 510 | `0x310F0C`, `0x310F32`, `0x31156C`, `0x3115D6`, `0x311660` |
| `qf_act` | 1 | 100 | `0x310F92` |
| `qf_dyn` | 5 | 200, 201, 310, 320, 410 | `0x310FFC`, `0x3110A8`, `0x3110E8`, `0x3111C4`, `0x3111EA` |
| `qep_hsm` | 7 | 200, 210, 220, 400, 410, 510, 520 | `0x311290`, `0x311414`, `0x311478`, `0x311488`, `0x3114B4`, `0x3114C8`, `0x311502` |
| `qf_mem` | 6 | 100, 110, 200, 310, 320, 330 | `0x311698`, `0x3116C0`, `0x3116E0`, `0x311710`, `0x31175C`, `0x3117B8` |
| `WsfOs` | 1 | 653 | `0x3140E2` |

The portable ID constellation matches the checked v6.0.1 through v6.6.0+
sources for every linked path. Unlinked source paths account for `qf_actq`
400/900, `qf_dyn` 100/500, `qf_act` 200, `qep_hsm` 600/810, `qf_mem` 400,
and QK 600/700. QK ID 189 is especially useful: it is the source-line ID
emitted through `QF_CRIT_ENTRY_()` at `qk.c:189` in every checked tag in the
surviving interval. It corroborates that interval but does not distinguish a
single tag.

## Recovered configuration and ABI

ARCv2 EM instruction widths and object-field accesses now establish these
high-confidence compile-time values:

| Setting/layout fact | Recovered value | Binary evidence |
|---|---:|---|
| `QF_MAX_TICK_RATE` | 0 | `QF_init` calls `QF_bzero` on `QF_timeEvtHead_` with length zero, then clears `QK_attr_` at the same address |
| `QF_MAX_ACTIVE` | 16 | priority-minus-one bounds compare against 16; QK compares priorities below 17 |
| `QF_MAX_EPOOL` | 2 | `QF_poolInit` accepts `QF_maxPool_` only while below two |
| `Q_SIGNAL_SIZE` | 2 | allocated `QEvt` stores a halfword signal at `+0`, then byte pool/ref counters at `+2/+3` |
| `QF_EQUEUE_CTR_SIZE` | 1 | `qf_actq` queue counters use byte loads/stores |
| `QF_MPOOL_SIZ_SIZE` | 2 | the 20-byte `QMPool` stores block size as a halfword |
| `QF_MPOOL_CTR_SIZE` | 2 | `nTot`, `nFree`, and `nMin` use halfword loads/stores |
| QK ready-set width | 16 bits | ready-set operations use halfword loads/stores for priorities 1–16 |
| `sizeof(QActive)` | 36 bytes | `QActive_ctor` clears exactly `0x24` bytes before installing the HSM/active vtable |
| `sizeof(QK_attr_)` | 8 bytes | `QF_init` clears eight bytes at `0x00801394` and writes `lockCeil` at `+2` |
| `Q_SPY` | disabled | `QActive_post_` uses the three-argument non-Q-SPY ABI and has no QS record path |
| `QF_CRIT_STAT_TYPE` | 32-bit ARC status value | `CLRI r18; SYNC` enters and `SETI r18` restores the saved status |
| Critical assertion behavior | restore status before `Q_onAssert` | `SETI r18` precedes qf_actq assertion 110 at `0x00310E60` |
| `QF_onStartup` | `0x00311154` | `QF_run` calls this vendor callback after initial-event scheduling and before `SETI` |
| `QK_onIdle` | `0x003115E4` | both run loops call this vendor callback indefinitely after enabling interrupts |
| Idle interrupt race guard | `ILINK` sentinel | `QK_onIdle` clears `ILINK`, runs optional callbacks, executes `CLRI; SYNC`, and calls the power manager only if no interrupt rewrote `ILINK` |

The sole direct call at `0x00311610` enters the 516-byte vendor power manager
at `[0x003126E0,0x003128E4)`. Its two hardware `SLEEP` instructions are at
`0x0031280E` and `0x00312816`. The function is boundary/hash pinned and its
idle-entry paths are partially reversed, but its ROM calls and complete power
policy remain retained vendor dependencies rather than portable QP/C.

`qf_time` is absent from the module strings and from the exhaustive
shared-assertion module-reference set even though assertions are enabled.
Every surviving upstream `qf_time.c` would retain the module label through its
tick/constructor/arm assertion paths. `QF_init` independently proves why it is
absent: the configured head array has zero length and shares address
`0x00801394` with the following 8-byte `QK_attr_`. Thus
`QF_MAX_TICK_RATE=0` and no upstream time-event closure is linked.
`QF_TIMEEVT_CTR_SIZE` remains non-observable because no counter object or field
access survives. Separate protocol-timer and sleep-timer SDK bodies are now
located exactly, but their application policy, unmatched closure, and nested
ISR bookkeeping beyond the recovered QK/critical-section ABI remain opaque.

## Surviving portable-source epochs

Exact Git blob tuples for all eight linked portable source files collapse the
16 checked tags into ten build-worthy source epochs. Tags grouped on one row
have identical blobs for `qf_actq.c`, `qf_dyn.c`, `qf_act.c`, `qep_hsm.c`,
`qf_mem.c`, `qk.c`, `qf_qact.c`, and `qf_qeq.c` even if other repository
files differ. Adding the two previously omitted unlabeled units splits
v6.3.6 from v6.3.7--v6.3.8.

| Portable-source epoch | Bounding tag commits |
|---|---|
| v6.0.1 | `25636b87b0dbf4ccb015cb6eb9fb42aeb6010ef6` |
| v6.0.4 | `a1acc1d0e296780686d7246adb3c5c305b4c347d` |
| v6.2.0–v6.3.1 | `7bfce82cc98ec6306ebb2fe9a72a49ebb1f1a77e` … `58f80da3a7c2a2c9ba29637a76d4eda3f9488c7d` |
| v6.3.2–v6.3.4 | `952101792d5fccf6db6f353b0426039910311851` … `2b231b3383d98b36585435030e7440dbade3da9b` |
| v6.3.6 | `5550cca87dedf72d45250ad01e9cdeee8c4140ba` |
| v6.3.7–v6.3.8 | `21787336e81748423d9e88d8b780728bb65e7ee0` … `a39a56b5ef3482aeaa7aa9d749d1368a5899d417` |
| v6.4.0 | `5d14aa368a014be23dc51ca7b0be9f20cb3e15a5` |
| v6.5.0 | `076a8d5d6f9c093c8bc49a331f923668de52f10d` |
| v6.5.1 | `416dcec8820b9cdb5827497e645d0d9375db53c6` |
| v6.6.0+ | `a280d203c0f55753b18dd9fc76104936729e471a` |

The two stock-facing semantic discriminators leave seven tags in six source
epochs: v6.3.6, v6.3.7--v6.3.8, v6.4.0, v6.5.0, v6.5.1, and v6.6.0+. These are the
only epochs needed for subsequent stock comparison unless evidence indicates
a vendor backport. The full ten-epoch history remains audited so the lower
bound fails closed if upstream history or the interpretation changes.

## ARCv2 EM candidate-build matrix

`tools/build_em9305_qpc_epoch_matrix.py` turns the epoch audit into a
controlled comparison build. On Lorelei it uses the disposable Fedora
`gcc-arc-linux-gnu` 16.1.1-1.fc44 binary (SHA-256
`69693ab42dbdcef58f1d30579962d900ee9895ce412f60ab77ebaf0a5ea78c3d`)
with binutils 2.46, `-mcpu=em -Os`, freestanding C99, function/data sections,
and the recovered port configuration. The full matrix builds 80 objects:
eight translation units for each of ten source epochs. The report deliberately labels these objects
`comparison_only_not_stock_equivalent`; GCC 16 and the generic comparison
port are not claims about EM's production compiler or ARC port.

Normalized code hashes reduce the ten source epochs to seven code-comparison
epochs. In the surviving interval they reduce six source epochs to three code
epochs: v6.3.6/v6.3.7--v6.3.8, v6.4.0/v6.5.0/v6.5.1, and v6.6.0+.
`qf_dyn` is code-identical from
the v6.2.0–v6.3.1 epoch onward; `qf_mem` is identical from v6.3.2–v6.3.4
onward; and QK plus `qf_act` are identical from v6.4.0 onward under this
compiler/configuration. v6.6.0+ still differs in `qf_actq` and `qep_hsm`.

The current eight-unit Lorelei baseline is 12.63 seconds and 450,932 KiB peak
RSS for the full 80-object history at four jobs. Its report SHA-256 is
`4a52ab9206a6d160411cf115e7304892dc533491c235c94557b54a1315c62e69`.
Four jobs remain the default. The small workload is dominated by archive
extraction and compiler/process startup, so using all 64 hardware threads is
counterproductive. A single batched SSH invocation adds negligible orchestration
overhead relative to running the same command in a Lorelei terminal.
After applying the stock semantic filter, `--stock-compatible-only` builds 48
objects across six surviving epochs in 8.82 seconds at four jobs. The latest
run used 583,192 KiB peak RSS and produced report SHA-256
`5dd4e7d565e68a56aea0eeb314df21f4e2c8321ffe49b5fdc0b3f166fb3046f3`.

```sh
python3 tools/build_em9305_qpc_epoch_matrix.py \
  --qpc-checkout /path/to/official/qpc \
  --gcc /path/to/arc-linux-gnu-gcc \
  --binutils-dir /path/to/arc-linux-gnu/bin \
  --stock-compatible-only \
  --output /empty/output/directory
```

## Tooling and reproducibility

Stock Ghidra 12.1.2 has no ARCompact language module. A disposable Lorelei
evaluation compiled the Apache-2.0 ARC processor module from the still-open
NSA Ghidra pull request 3006, branch head
`d3fbf109ada6d051750e973779170c1758622530`. The resulting 44,816-byte
`ARCompact.sla` hashes to
`61af75c6e9beb457b72c6d4a55dd2f6822921694be37a436ffa9b7b9f1941737`.
It decompiles the controller and resolves ARC long immediates, although a few
constructors still produce p-code errors. The extension remains a disposable
analysis dependency and is not vendored or used by a production build.

GNU `binutils-arc-linux-gnu` 2.46-1.fc44 was also unpacked into a disposable
Lorelei directory. Its `arc-linux-gnu-objdump` binary hashes to
`278eb56300a03b7b3b39b1742d32376b856aa26917077f548288d6ed826b10a2`.
Wrapping the raw application in an ARCv2 EM carrier object compiled with
`-mcpu=em`, then disassembling with `-M cpu=em`, correctly renders the forms
that the other analyzers miss. For example, it resolves `0x00311070` as
`mov_s r16,0x334520`, preserving the `qf_dyn` module argument for assertions
310 and 320. ARC700 mode is incorrect for these EM7D encodings; ARCv2 EM is
now the preferred independent disassembly oracle.

`tools/disassemble_em9305_arcompact.py` automates that wrapper. It authenticates
the stock image, rejects unaligned/out-of-package ranges, preserves the ARCv2
ELF machine flags, and refuses to continue if the wrapper reports ARC600. A
direct raw-binary `objcopy -B arc` conversion must not be used because it
silently selects ARC600 and can still misdecode long immediates.

```sh
python3 tools/disassemble_em9305_arcompact.py \
  --gcc /path/to/arc-linux-gnu-gcc \
  --binutils-dir /path/to/arc-linux-gnu/bin \
  --range 0x311230:0x31125e \
  --range 0x3115e4:0x31161c
```

Repository scripts now provide bounded vector seeding, aligned range
disassembly, register-use reporting, instruction windows, and reference
dumps under `tools/ghidra/`. The fail-closed
`tools/analyze_em9305_qpc.py` pins the stock identities and boundaries and,
with `--rizin`, exact-address verifies all 31 calls plus the six-instruction
QK fingerprint.

`tools/run_ghidra_shard_batch.sh` and
`tools/manifests/em9305-ghidra-pending.tsv` now turn those bounded questions
into isolated headless projects with deterministic status/result/log files.
The current checked-in runner's Lorelei replay scheduled 16 targeted shards at
concurrency 16; all completed in 18.042--18.299 seconds. Its returned
`results.tsv` hashes to
`6547ee7fcbe6fd1164c84d1c16046b1acb8dc3bfa7923300351679b9d5b3cafa`,
its authenticated `INPUTS.tsv` hashes to
`145ba2002bad9e554565cb9d1cf33a8478ca326f905aa72feda77453955caad0`,
its `CONFIG.tsv` hashes to
`e7a730cf196899bec0272f0f3413bfc80c622b5435512826f5c82414b8ef75ae`,
and its artifact `SHA256SUMS` hashes to
`632a9ef24aaf7c7acab901838b9f9680a5bd2825e743cfe55159e45fe0b36b12`.
Targeted `-noanalysis` retained all bounded instruction/decompile outputs and
was 1.46x faster by mean shard time than the same manifest with broad
auto-analysis. The input ledger now authenticates the runner and analysis
configuration in addition to the firmware, manifest, and scripts.
The experimental ARC processor emitted p-code warnings, so Ghidra output is
accepted only when raw bytes, GNU ARC decoding, Rizin, a pointer table, or the
authenticated source oracle corroborates it. This batch recovered the hook
boundaries and terminal-table xrefs used above.

`tools/compare_em9305_sdk_archive.py` is now the stronger compiler/object lane.
It authenticates six SDK archives, masks only known four-byte ARC relocation
fields, scans all halfword-aligned stock addresses, and requires 98 exact
matches plus three deliberately modified QP hooks. Its six Lorelei report
hashes and full results are recorded in the
[SDK archive match audit](em9305-sdk-archive-match-audit.md).

```sh
python3 tools/analyze_em9305_qpc.py --rizin --json
python3 tools/analyze_em9305_qpc.py --qpc-checkout /path/to/official/qpc --json
python3 tools/analyze_em9305_qpc.py \
  --em9305-sdk-checkout /path/to/C0R3YY2/em9305_original --json
python3 tools/compare_em9305_sdk_archive.py \
  --archive /path/to/lib_QPC.a --archive-kind qpc \
  --binutils-dir /path/to/arc-linux-gnu/bin --json
python3 -m unittest tests.test_analyze_em9305_qpc
```

Primary references:

- [EM9305 datasheet](https://www.emmicroelectronic.com/sites/default/files/products/datasheets/EM9305-DS.pdf)
- [official Quantum Leaps QP/C repository](https://github.com/QuantumLeaps/qpc)
- [third-party EM9305 SDK v4.2 source oracle](https://github.com/C0R3YY2/em9305_original/tree/e4412bc98d4e76d441d1226ca3696e53cfae5f54)
- [NSA Ghidra ARCompact pull request 3006](https://github.com/NationalSecurityAgency/ghidra/pull/3006)
- [ARCompact Ghidra implementation paper](https://www.sstic.org/media/SSTIC2021/SSTIC-actes/analyzing_arcompact_firmware_with_ghidra/SSTIC2021-Article-analyzing_arcompact_firmware_with_ghidra-iooss.pdf)

## Next discriminators

1. Follow the named vendor hook bodies' out-of-cluster callees and classify
   the remaining application-specific callback implementations.
2. Locate any timer/event substitute above the now-exact protocol/sleep timer
   libraries; do not invent upstream QP time-event settings for the absent
   closure.
3. Use the exact MetaWare T-2022.09 object fingerprint as the compiler baseline
   while reconstructing or cutting forward the vendor ARC libraries.
4. Keep ARC CPU port, ROM calls, radio/WSF glue, startup, flash records, and
   vendor customizations separate from portable QP source.
5. Review the applicable historical QP license or commercial-license status
   before any source is linked into a controller image.
