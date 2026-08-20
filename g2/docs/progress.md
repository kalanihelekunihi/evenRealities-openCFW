# openCFW reconstruction progress

Status date: 2026-08-12
Compatibility target: official G2 `s200_v2.2.6.10`

This is the concise status index for dependency provenance, byte ownership,
and controller-segment reconstruction. Detailed evidence remains in
[`upstream-inventory.md`](upstream-inventory.md),
[`source-coverage.md`](source-coverage.md), and
[`memory-map.md`](memory-map.md).
The current third-party identity and functional-gap priority is summarized in
[`research/third-party-utility-gap-priority.md`](research/third-party-utility-gap-priority.md).

The fail-closed aggregate [third-party dependency closure audit](research/third-party-dependency-closure-audit.md)
now reconciles 26 families, 25 selected public source commits/baselines, the
130,000-byte retained third-party-path opaque lower bound, zero unclassified
Cordio reusable paths, the complete seven-function / 638-byte private LVGL
display port, and FreeType lifecycle absence evidence. The 26th family is the
DaveGamble cJSON parser shared by service_android_notify.c and
service_whitelist.c, identified to version interval v1.7.9--v1.7.12 and now
admitted as an authenticated pristine MIT snapshot at interval-ceiling tag
v1.7.12 (`3c8935676a97c7c97bf006db8312875b4f292f6c`), production-excluded by
explicit decision. The audit reports zero
bounded third-party functional gaps that are still locally actionable;
residual work requires hardware, unavailable private/proprietary inputs, or
an explicit production-admission decision.

The first-party retained-path frontier is now fully closed: 234 closed /
0 open over all 234 retained paths, covering all 1,230 anchored functions
and all 485,274 anchored body bytes, with 814,534 complete-object body bytes
and 885,418 known physical bytes over 232 closure manifests.

Headless reverse-engineering throughput is now available on the 32-core,
64-thread `lorelei` worker. A version-matched Ghidra 12.1.2/JDK 21 setup and
reproducible benchmark show 2.28x higher throughput for eight independent
decompilation batches and 5.00x for the observed 16-task workstation run.
The tested safe default for independent import/decompile jobs is 16 remote
workers in one SSH command. Apollo main now has a separate 64-chunk lane that
analyzes once, reflink-clones the closed project, and decompiles all 7,370
discovered functions with zero failures. Its measured cold path is about 5.0
minutes; retained-template replay is about 2.4 minutes, and 64 workers beat the
tested 16- and 32-worker points for that workload. Full results,
hashes, caveats, and the fail-closed integration policy are in
[`research/lorelei-re-acceleration-benchmark.md`](research/lorelei-re-acceleration-benchmark.md).
The first production census used that lane to decompile 35 early-island
targets as 16 shards in about 12 seconds. Local Rizin plus a new fail-closed
analyzer separated application/DSP code from ten retained IAR runtime units:
the four memory providers, signed and unsigned 64-bit division cores and
wrappers, VFP `sqrtf`, two errno setters, and the errno-address accessor. All
ten bounded units are now source-recreated and production-integrated.
The same lane has now run the current targeted 16-shard EM9305 ARC manifest:
all isolated projects completed in 18.042--18.299 seconds and returned
hash-manifested artifacts. This is 1.46x faster by mean shard time than the
same manifest with broad auto-analysis, while retaining all bounded
instruction/decompile sections. That
pass recovered the QF/QK hook boundaries and terminal pointer-table xrefs;
GNU ARC decoding, Rizin, and the authenticated SDK oracle remain the acceptance
authorities where the experimental Ghidra ARC extension reports p-code errors.

The Apollo run is mechanical discovery rather than source completion. Equal
byte chunks 0–33 contain all currently discovered functions; chunks 34–63
cover data/resources after `0x00600FAA` and remain in the complete tiling so
missed code is not silently excluded. Upstream attribution, ABI recovery,
boundary repair, and clean source recreation remain the limiting work.

The first whole-corpus ownership pass now authenticates all 357 retained
`s200_ap510b_iar_git` C source paths and 712 raw pointer cells. It maps 314
paths to 1,760 discovered functions: 530 third-party anchors and 1,230
project/first-party anchors, with no cross-root function. The baseline leaves
43 paths without a decompiler-token anchor and 5,610 functions without a
retained-path anchor.
All seven embedded third-party directory families were already inventoried;
no new dependency family was found in the retained `__FILE__` set. These are
triage counts, not byte-ownership percentages. See the
[source-path census](research/apollo-embedded-source-path-census.md).

The parallel Cordio lane now adds a fail-closed function map over the same
authenticated replay: 36 retained translation-unit paths, 32 paths with
anchors, and 114 distinct anchored functions. The normalized map SHA-256 is
`772063dc1841dc33523e68ecca9188923e28efd5cbe6db5a22a36979c41b2623`.
It records function bounds, direct-call topology, small literal constants, and
logger/assert source-line values, while separating 22 generic Packetcraft
candidates from five Ambiq ports and nine Ambiq/application-or-Even paths.
The public r20.05--r20.05c interval remains limited to the previously audited
ATT/DM behavior and unchanged blobs; it is not an exact vendor-tree claim.
No production manifest changed. See the
[Cordio source-path/function map](research/cordio-source-path-function-map.md).

The follow-on aggregate reconciliation supersedes the older 80–85% Cordio
identity estimate for the reusable host-stack surface. All 22 retained public
Packetcraft candidates and all five retained Ambiq ports now map to focused
audits and matching tests. Repository-wide, 67 focused module analyzers match
67 tests and 67 function maps; 69 provenance manifests retain the per-module
r19/r20/R4/AmbiqSuite source-oracle distinctions. No retained reusable path or
focused third-party module remains unclassified. The exact historical mixed
tree remains unobservable, production admission and hardware/controller
validation remain, and nine application/product paths are explicitly
first-party boundary work. See the
[Cordio aggregate closure](research/cordio-aggregate-closure-audit.md).

The parallel discovery-gap lane resolves the baseline 43-path ambiguity more
carefully. Their 46 path-pointer cells have 273 exact-cell, halfword-aligned
Thumb `LDR` decode sites. Independent call/table evidence recovers eight
functions across AgingTest and Cordio WSF timer, raising the reviewed effective
discovery count from the immutable Ghidra baseline of 7,370 to 7,378. The
other 41 paths remain missed-code candidates; zero are confirmed path-only
data. Only the eight witnessed entries are promoted, and none changes
production ownership. See the
[source-path recovery audit](research/apollo-embedded-source-path-recovery.md).

The follow-on WSF timer pass names the complete 536-byte FreeRTOS port cluster,
recovers `WsfTimerInit` as the eighth missed function, closes the 16-byte timer
ABI, queue/handle/tick globals, WSF interrupt-nesting locks, and all external
dispatcher calls, and adds a host-tested clean-room behavioral candidate
covering all eleven functions / 536 code bytes. Its exhaustive
ingress audit closes 53 BL callers and the sole stored callback pointer, with
no other entry/interior branch or pointer consumers. Official Packetcraft
r19.02 is a public semantic oracle for the bool-pointer next-expiration and
expired-service bodies. Official AmbiqSuite 2.5.1 archive SHA-256
`87b03680…` supplies the exact proprietary implementation/source family, and
its 2.5.1-only saved-tick statement is present in stock; minor local
text/config drift remains. Lorelei's public-oracle matrix ran in 0.800405321
seconds; its follow-on eleven-function matrix ran 143 comparisons in
2.448108512 seconds, linked with zero unresolved symbols after 13 explicit
seams, and made 8/11 functions size-exact under bounded configs. Neither
matrix produced a raw or strict-normalized IAR match. Timer-module semantic
identification was 95–98%; the then-current 80–85% aggregate estimate is
superseded by the aggregate closure below. See the
[focused timer audit](research/cordio-wsf-timer-source-recovery.md).

The adjacent WSF OS/queue pass closes 12 OS functions / 532 bytes and six
linked queue functions / 242 bytes. The stock task is exactly 64 bytes with
ten handlers, ten byte-wide handler masks, its queue at `+0x34`, task mask at
`+0x3C`, and handler count at `+0x3D`. Official AmbiqSuite 2.5.1 supplies the
proprietary implementation family and dispatcher discriminator; later
official Ambiq source corroborates the otherwise identical ten-handler
variant, but the exact G2 definition site is unavailable. Lorelei completed
234 stock-ABI GCC comparisons in 3.521196588 seconds with zero unresolved
closure symbols and no raw/strict-normalized match. All 18 bounded functions
are behaviorally recreated and tested but production-excluded. This tranche
is 95–98% semantically/source-family identified; overall Cordio remains
80–85%. See the [WSF OS/queue audit](research/cordio-wsf-os-queue-source-recovery.md).

The next WSF buffer/message pass closes another ten functions / 556 bytes.
Three buffer functions are bounded over 430 bytes; initialized-SRAM recovery
pins the four pools to `{16×8, 32×4, 64×10, 480×20}`, consuming `0x2930`
of the `0x2940` region at `0x2004FA98`. The exact Ambiq FreeRTOS buffer
implementation family is proprietary and remains an oracle only. All seven
message definitions / 126 bytes instead have an exact Apache-2.0 Packetcraft
r19.02 route. Lorelei completed 78 buffer comparisons and 26 closure links in
3.463 seconds; every link closed, but no raw/strict match occurred. The
warning seam reduced the best aggregate size gap to 34 bytes and Free is
within two bytes. All ten functions are behaviorally recreated and tested but
production-excluded. This tranche was 95–98% semantically/source-family
identified; the then-current 80–85% aggregate estimate is superseded by the
aggregate closure below. See the
[buffer/message audit](research/cordio-wsf-buffer-message-source-recovery.md).

The WSF assert/trace pass closes two more linked functions / 208 code bytes.
`WsfTrace` has 126 direct callers, a 1,024-byte stack buffer, retained source
path and line 137, and the stock double-format debug path. `WsfAssert` is the
sole overflow target and combines the Ambiq debugger-escape loop with a
downstream EasyLogger hook/reset extension at global `0x2007456C`. Lorelei
completed 26 comparisons and 13 zero-unresolved links in 2.098 seconds; zero
raw/strict matches and the pristine assert source's 118-byte size deficit
independently prove the local augmentation. Both functions have tested,
production-excluded source, while the proprietary Ambiq files remain oracles
only. This tranche is 95–98% behavior/source-family identified; overall Cordio
remains 80–85%. See the
[assert/trace audit](research/cordio-wsf-assert-trace-source-recovery.md).

The remaining FreeRTOS-port census classifies `wsf_efs.c` and `wsf_math.c` as
unlinked with high confidence. EFS has none of its distinctive six-by-52-byte
file table, four-media callback layout, 12-caller validator, WDXS consumer
topology, strings, or retained paths. Math has neither its xorshift128 seed
quartet nor the combined 11/19/8 shift signature. No stock bytes are assigned
to either module. All 20 EFS bodies nevertheless have an exact Apache-2.0
Packetcraft r19.02 route if future images prove inclusion. The same census
identified linked `wstr.c` as the next bounded WSF target. See the
[EFS/math exclusion audit](research/cordio-wsf-efs-math-exclusion-audit.md).

The linked follow-up closes the two retained `wstr.c` reverse helpers / 118
bytes with 39 plus two direct callers and no callee, pointer, or interior
ingress. Both definitions have an exact Apache-2.0 Packetcraft route from
r19.02 through r20.05c and a tested production-excluded candidate. Lorelei's
26-row matrix linked with zero unresolved symbols in 2.153 seconds; its best
common `-O1` lane is ten aggregate bytes from stock, with no raw/strict match.
The WDXS-only `WstrnCpy` is explicitly dead-stripped. See the
[WSF string-helper audit](research/cordio-wstr-source-recovery.md).

The next ranked Cordio pass closes the ATT client-supported-features module:
ten linked functions / 4,814 code bytes in `[0x0052C6C0,0x0052DA0C)`, plus
126 bytes of literal/string/data pools. Stock selects Packetcraft
r20.05--r20.05c semantics, while keeping Ambiq-era API names and adding local
connId validation and logger/assert expansion. The 13-byte-observable control
block at `0x20073E04`, three two-byte records, callback/hash offsets, 20 direct
callers, and pointer/ingress closure are exact. `AttsCsfInit` is dead-stripped
and supplied by BSS zeroing. Lorelei's two readiness builds close four provider
seams with zero undefined symbols; broad compiler comparison is deferred until
the vendor instrumentation seam is modeled. Module identification was 90–95%;
the then-current 80–85% aggregate estimate is superseded by the aggregate
closure below, and production ownership was unchanged. See the
[ATT CSF audit](research/cordio-atts-csf-source-recovery.md).

The next public-host tranche closes the complete linked `smp_db.c` module:
eleven functions / 2,952 code bytes in `[0x00541E34,0x005429F2)`, with 54
bytes of literal/alignment data and two source-only remove APIs dead-stripped.
The Apache definitions are stable from Ambiq/r19 through r20.05c, while stock
event `0x20` independently selects the r20 message ABI. The 256-byte SRAM
control block at `0x200708EC` proves ten 24-byte records versus the upstream
default three, and both the boot and normal runtime SMP configurations are
now distinguished. Lorelei's compact two-profile readiness artifact links
with zero unresolved symbols. Module identification was 95–98%; the
then-current 80–85% aggregate estimate is superseded by the aggregate closure
below, and production ownership was unchanged. See the
[SMP DB audit](research/cordio-smp-db-source-recovery.md).

The adjacent ATT CCC tranche is now complete: all fourteen `atts_ccc.c`
functions / 2,770 code bytes plus 138 bytes of inline/literal data occupy
`[0x0052BB64,0x0052C6C0)`. The exact Apache definitions are stable from
Ambiq/r19 through r20.05c; stock callback event `0x14` selects the r20 ATT
header ABI. The 24-byte control block, three connection-table pointers, six
product CCC settings, 23 direct calls, registered callback, and eight indirect
consumers are closed. Lorelei's two-profile readiness links have zero
unresolved symbols. Module identification is 95–98%; overall Cordio remains
80–85% and all bytes remain stock-retained. See the
[ATT CCC audit](research/cordio-atts-ccc-source-recovery.md).

The ATT client-discovery tranche is also complete: fifteen common
`attc_disc.c` functions / 2,908 code bytes plus 104 bytes of literal/alignment
data occupy `[0x0056B7EC,0x0056C3B0)`. Stock's characteristic scan contains
the r20-only post-match `break`, and its retained line numbers select the
Packetcraft r20.05--r20.05c source family over AmbiqSuite 2.5.1/r19. The
20-byte state ABI, all 20 direct callers, and pointer/interior ingress are
closed; three unused included-service routines are dead-stripped. Lorelei's
two readiness profiles link with zero unresolved symbols. Module
identification is 95--98%; overall Cordio remains 80--85% and production
ownership is unchanged. See the
[ATT discovery audit](research/cordio-attc-disc-source-recovery.md).

The ATT client core is now closed as well: twenty linked `attc_main.c`
functions / 3,540 code bytes plus 140 owned data bytes occupy
`[0x00530D74,0x00531BD4)`. Stock's three-bearer-per-connection layout and
17-entry request table select the Packetcraft r20.05 EATT architecture; its
zero-length packet rejection matches the later official Ambiq R4.4.1 patch.
The analyzer closes 32 direct calls, 17 stored entries, the retained path,
and all strict-interior ingress. Only `AttcSetAutoConfirm` is source-only.
Identification is 95--98%; production ownership is unchanged. See the
[ATT client-core audit](research/cordio-attc-main-source-recovery.md).

The client PDU and optional request units now close the rest of the stock
response table. `attc_proc.c` contributes fifteen linked functions / 1,884
code bytes in `[0x004B5230,0x004B59C0)`; `attc_read.c` contributes four / 414
bytes in `[0x0056C3B0,0x0056C550)`; and `attc_write.c` contributes two / 124
bytes in `[0x00539DCC,0x00539E48)`. Nine unused APIs are dead-stripped across
the three units. The first two independently confirm the r20 per-bearer/EATT
architecture; the write bodies are release-invariant and inherit that pin.
All 24 direct calls, 13 local response-table entries, object boundaries, and
strict-interior ingress are closed. The mandatory-PDU audit also records the
inherited R4 response/minimum-length table bounds defect without treating
adjacent string bytes as owned table data. Production ownership is unchanged.
See the [PDU processor](research/cordio-attc-proc-source-recovery.md),
[client read](research/cordio-attc-read-source-recovery.md), and
[client write](research/cordio-attc-write-source-recovery.md) audits.

Optional ATT client signing is conclusively absent. `AttcInit` leaves the
signing interface null, no later installation exists, and complete
CMAC/local-CSRK/write-wrapper caller censuses assign every candidate to other
bounded modules. All seven `attc_sign.c` definitions are therefore
source-only; this removes an optional dependency without assigning any stock
bytes. See the
[client-signing exclusion](research/cordio-attc-sign-exclusion.md).

The legacy advertising tranche closes seventeen linked `dm_adv_leg.c`
functions / 4,396 code bytes in `[0x004B9A80,0x004BAC4E)`, plus 162 inline
data bytes and a separately owned 100-byte trailing pool after one interleaved
foreign function. Function definitions are Apache-identical from r19/Ambiq
through r20.05c, but stock message offset `+8` proves Ambiq's flexible-array
payload ABI. The two-set SRAM layout, action/interface tables, and every direct
or registered entry are closed; `DmAdvModeLeg` is dead-stripped. Lorelei's two
profiles link with zero unresolved symbols. Module identification is 95--98%;
overall Cordio remains 80--85% and production ownership is unchanged. See the
[legacy advertising audit](research/cordio-dm-adv-leg-source-recovery.md).

The common advertising producer tranche closes nine linked `dm_adv.c`
functions / 562 code bytes plus its ten-byte literal pool. Exact AmbiqSuite
R2.4.2/R2.5.1 Apache source matches stock's `len+8` allocation and inline
payload copy; Packetcraft r19/r20 instead uses an incompatible payload
pointer. All eleven callers, direct providers, two-set globals, and pointer
closure are guarded. Six unused APIs are dead-stripped, and both Lorelei
profiles link with zero unresolved symbols. Module identification is 95--98%;
overall Cordio remains 80--85% and production ownership is unchanged. See the
[common advertising audit](research/cordio-dm-adv-source-recovery.md).

The DM connection-manager tranche closes 57 linked functions / 6,216 code
bytes in `[0x004B5B24,0x004B7426)`, plus 186 interstitial bytes and an
82-byte trailing pool through `0x004B7478`. Fifty-six bodies map to the
Apache-2.0 Packetcraft r20.05 source inventory; one 62-byte helper is a
vendor-only addition, and five public APIs are dead-stripped. Action/component
tables, 209 direct callers, thirteen registered Thumb pointers, the
three-connection/196-byte SRAM ABI, and all stock spans are fail-closed.
Lorelei's corrected v2 handoff preserves two non-vacuous zero-unresolved
build closures and nine conservative anchors; local analysis expands it to the
complete linked module. The architecture is a hybrid: r20 connection-update
and peer-SCA behavior, Ambiq 2.5.1 warning suppression, and product validation
patches. Module identification is 95--98%; overall Cordio remains 80--85%,
and production ownership is unchanged. See the
[DM connection-manager audit](research/cordio-dm-conn-source-recovery.md).

The adjacent DM connection state-machine tranche closes the sole linked
`dm_conn_sm.c` function / 1,598 code bytes, its 58-byte pool, exact 80-byte
state table, both callers, all 90 direct logger relocations, and three
registered action tables. Its five-by-eight table and mask 7 unequivocally
select Packetcraft r20.05's separated connection-update architecture over
the thirteen-event r19/Ambiq table. Stock adds vendor diagnostics and an
action-set bound check, so public Apache source is a semantic/table oracle,
not exact downstream text. Both Lorelei profiles retain live code and close
their two provider seams. Production ownership remains unchanged. See the
[DM state-machine audit](research/cordio-dm-conn-sm-source-recovery.md).

The DM local-device tranche closes twelve linked functions / 626 code bytes
and 46 bytes of literal/alignment data in the complete 672-byte
`dm_dev.c` footprint. Three interface/action pointers, 29 direct calls, all
provider relocations, the 21-component message ABI, and the retained source
path are fail-closed. Official Ambiq R4.4.1 source explains the vendor-command
translator, stale-reset clear, and trace layout; six filter/whitelist APIs are
dead-stripped. Lorelei's live Os/O1 closures have zero unresolved symbols.
Production ownership is unchanged. See the
[DM local-device audit](research/cordio-dm-dev-source-recovery.md).

The optional DM device-privacy tranche is now closed as a stock exclusion.
All 18 public `dm_dev_priv.c` functions compile and link in two Lorelei
profiles, but none is present in G2. The authenticated 21-slot boot table keeps
component 1 on `dmFcnDefault`; all nine interface-table base references and
every component install are accounted for, with no write to slot 1. There is
also no privacy action/interface table, retained path, or Start/Stop allocation
wrapper. The analyzer therefore records zero linked bytes and eighteen
source-only functions. Production ownership is unchanged. See the
[device-privacy exclusion audit](research/cordio-dm-dev-priv-exclusion.md).

The DM main-router tranche now closes all sixteen `dm_main.c` functions / 484
code bytes and the complete 508-byte physical interval. More importantly,
stock's 90-entry HCI route table, 92-entry callback-size table, and 21-slot
component table exactly select the official AmbiqSuite R4.4.1 source family;
r19, AmbiqSuite 2.5.1, and vanilla Packetcraft r20 have different dimensions.
Twenty-nine direct calls, fifteen stored entries, the decoded boot interface
table, and zero interior ingress are fail-closed. Lorelei preserves dual
public-r20/R4 Os/O1 lanes with four live zero-unresolved closures; the R4 lane
is explicitly a hybrid header/config build. Production ownership is unchanged.
See the [DM router audit](research/cordio-dm-main-source-recovery.md).

The adjacent DM privacy tranche closes 21 linked `dm_priv.c` functions / 980
code bytes and the full 1,008-byte physical interval. Its seven-entry main
action table, two-entry AES action table, and component-6/component-15
interface installs select the Packetcraft r20.05/Ambiq R4 split architecture.
Four unused public APIs are dead-stripped; nineteen direct calls, thirteen
stored entry pointers, and zero interior pointers close ingress. Production
ownership is unchanged. See the
[DM privacy audit](research/cordio-dm-priv-source-recovery.md).

The adjacent DM security tranche closes eight linked `dm_sec.c` functions /
462 code bytes and the full 488-byte physical object. Stock's nonzero
EDIV/Rand LTK rejection while LESC is enabled is the decisive Packetcraft
r20/Ambiq R4 behavior and excludes r19/AmbiqSuite 2.x. Four unused APIs are
dead-stripped; the three registered interface entries and all direct ingress
are fail-closed. Production ownership is unchanged. See the
[DM security audit](research/cordio-dm-sec-source-recovery.md).

The component-8 LESC tranche closes seven linked `dm_sec_lesc.c` functions /
222 code bytes in a 248-byte object and four dead APIs. Its source bodies are
release-invariant, while the exact `0x40/0x41` message values pin the r20/R4
shift-three ABI. The interface, ECC-key storage, calls, and interior ingress
are fail-closed. See the
[DM LESC audit](research/cordio-dm-sec-lesc-source-recovery.md).

The component-9 PHY tranche closes six linked `dm_phy.c` functions / 308
code bytes in a 320-byte object and two dead APIs. `DmPhyInit` uses the
widened 64-bit `HciSetLeSupFeat(0x900, TRUE)` ABI under the task lock, which
decisively selects Packetcraft r20/Ambiq R4 over r19/AmbiqSuite 2.x. The
registered interface, five direct calls, callback ABI, and zero interior
ingress are fail-closed. See the
[DM PHY audit](research/cordio-dm-phy-source-recovery.md).

The slave-security tranche closes all three `dm_sec_slave.c` wrappers / 148
code bytes in a 152-byte object. Six direct callers, no stored pointers, and
zero interior ingress are fail-closed. The bodies are release-invariant, but
the LTK-response event `0x29` independently selects the r20/R4 three-bit
message ABI over r19's `0x51`. See the
[DM slave-security audit](research/cordio-dm-sec-slave-source-recovery.md).

The master-security tranche likewise closes all three `dm_sec_master.c`
functions / 144 code bytes in a 152-byte object. Four direct callers and zero
stored/interior pointers close ingress; event `0x28` selects r20/R4. This
tranche also proves `dmSecCb=0x20074114` and
`calc128Zeros=0x007856B0`. See the
[DM master-security audit](research/cordio-dm-sec-master-source-recovery.md).

The master-connection tranche closes five linked `dm_conn_master.c`
functions / 138 code bytes in a 140-byte span; only `DmConnSetAddrType` is
dead-stripped. Event `0x72`, component 14, and `dmConnUpdExecute` decisively
select r20/R4's separated update architecture. Two direct calls, three action
pointers, and zero interior ingress are fail-closed. See the
[DM master-connection audit](research/cordio-dm-conn-master-source-recovery.md).

The legacy-master connection tranche closes all three
`dm_conn_master_leg.c` functions / 136 code bytes and its 24-byte pool. The
r20 two-table locked initializer and two-entry main table exactly match stock
and exclude r19's unlocked four-entry architecture. Two direct calls, one
registered pointer, and zero interior ingress are fail-closed. See the
[legacy-master audit](research/cordio-dm-conn-master-leg-source-recovery.md).

The adjacent legacy-slave tranche closes all five
`dm_conn_slave_leg.c` functions / 104 code bytes and its 16-byte pool. Its
four-entry main table and separate two-entry update table are installed under
the task lock, excluding r19's unlocked six-entry architecture. One direct
call, four registered pointers, and zero interior ingress are fail-closed.
See the [legacy-slave audit](research/cordio-dm-conn-slave-leg-source-recovery.md).

The core slave-connection tranche closes five linked `dm_conn_slave.c`
functions / 206 code bytes in a 212-byte object; only `DmConnAccept` is
dead-stripped. The exact two-entry action table, component-14 event `0x73`,
and `dmConnUpdExecute` route independently select r20/R4. Five direct calls,
two registered pointers, and zero interior ingress are fail-closed. See the
[slave-connection audit](research/cordio-dm-conn-slave-source-recovery.md).

The L2CAP slave tranche closes six linked `l2c_slave.c` functions / 1,078
code bytes in a complete 1,148-byte object; only `L2cDmSigReq` is
dead-stripped. Stock contains r20's connection-ID validation and `connId-1`
state indexing, excluding AmbiqSuite 2.x. Four direct calls, two stored
pointers, and zero interior ingress are fail-closed. See the
[L2CAP slave audit](research/cordio-l2c-slave-source-recovery.md).

The adjacent L2CAP master tranche closes all three `l2c_master.c` functions /
658 code bytes in a complete 700-byte object. Its bodies are release-invariant,
so it is qualified through exact Apache definitions plus the neighboring
r20/R4 DM ABI rather than treated as an independent version discriminator.
Three calls, one stored callback, and zero interior ingress are fail-closed.
See the [L2CAP master audit](research/cordio-l2c-master-source-recovery.md).

The L2CAP core tranche closes all 11 `l2c_main.c` definitions / 1,636 code
bytes in the corrected 1,736-byte object ending at `0x00530C00`. Sixteen direct
calls, six registered callback entries, and zero interior pointers are
fail-closed. Its bodies are release-invariant, so exact r20 Apache definitions
are qualified by the neighboring r20/R4 DM architecture. See the
[L2CAP core audit](research/cordio-l2c-main-source-recovery.md).

The remaining optional `l2c_coc.c` unit is positively excluded: all 67 public
definitions are source-only. Stock has only the three known `l2cCb` literals
and three non-CoC `DmConnRegister` callers, while mandatory `L2cCocInit`
requires both. No CoC path, API, or diagnostic marker survives. See the
[L2CAP CoC exclusion](research/cordio-l2c-coc-exclusion.md).

The secure-connections SMP-main tranche closes 18 linked `smp_sc_main.c`
functions / 2,626 code bytes in the complete 2,820-byte object at
`[0x0056CDC0,0x0056D8C4)`. Four unused public definitions are source-only.
The retained cleanup-event name at value `0x1F` independently selects the r20
message ABI. One hundred eleven direct calls, no registered entry pointer, and
zero real interior ingress are fail-closed. See the
[SMP secure-connections main audit](research/cordio-smp-sc-main-source-recovery.md).

The paired secure-connections state-machine tranche closes all four
`smpi_sc_sm.c` / `smpr_sc_sm.c` functions / 598 code bytes, both physical
objects, and 1,495 scattered dispatch-data bytes. Its two interfaces lead to
106 action pointers, 78 state pointers, and all 80 common/per-state tables.
The responder's 55-action table and API-pair-request timeout/cleanup rows
exclude r19. Four direct calls and zero stored/interior function pointers are
fail-closed. See the
[SMP SC state-machine audit](research/cordio-smp-sc-state-machines-source-recovery.md).

## Percentage definitions

The current Apple Clang core-source package is 4,444,468 bytes. The table uses
the component builder as the ownership authority and therefore applies the
1,592-byte flash-plan metadata correction proven by the origin-accounting
audit:

| Byte ownership | Bytes | Package share | Meaning |
|---|---:|---:|---|
| Source compiled | 143,245 | 3.222995% | Human-readable openCFW source emitted in `source_compiled` regions |
| Generated | 100,384 | 2.258628% | Container/wrapper/checksum/alignment/redirect bytes, including the 1,592 controlled bytes still mislabeled by the hand-partitioned flash plan |
| Controlled total | 243,629 | 5.481623% | Source compiled plus generated |
| Opaque compatibility bytes remaining | 4,200,839 | 94.518377% | Bytes still copied from official firmware or retained external payloads after metadata reconciliation |

`94.518377%` is the exact reconciled answer to “how much of the package remains
blob-backed,” but it is **not** a defensible estimate of proprietary Even
source. Opaque spans still mix identified upstream libraries, first-party Even
code/data, vendor ports, generated assets, and proprietary controller images.
The source manifest does not assign every opaque byte a fine-grained origin,
so a precise “original, non-upstream source” percentage would be false
precision. The origin-aware companion ledger supplies conservative Apollo
lower bounds without relabeling mixed residual bytes as data or first-party
source.

## Upstream dependency identification

The estimates below measure provenance/configuration identification, not byte
replacement. `100%` means an exact maintained upstream commit and required
G2 selection are pinned; a range means a compatible source interval or vendor
fork remains. Production replacement can be much lower even when identity is
complete.

| Dependency | Identification estimate | Maintained source pin | Principal remainder |
|---|---:|---|---|
| FreeRTOS-Kernel | 100% | V10.5.1 `def7d2df2b0506d3d249334974f51e427c17a41c`; recovered one-field G2 TCB patch SHA-256 `cf8c457153b75ad6a3163b9b6e6873e476e03537bb4534c9c8e4557de0eb4eb3`; scheduler/port start and complete STIMER setup/IRQ/tickless algorithms dual-profile qualified | Original private patch commit/name unobservable; atomic production binding, hardware timing/sleep validation, and first-party power/trace hooks |
| CMSIS-FreeRTOS | 100% | v10.5.1 `d213f261b5be6bb29a7cce8b84071706b72f4d53`; exact `cmsis_os2.c` blob first at `13acfbef7be85119fc6bc56832c455d4547d92c7`; all 43 linked functions and all 38 public plus five private production entries source-owned | No linked functional gap; exact historical checkout remains bounded, not unique |
| CMSIS Core | 100% | `d23a6949a0331ca96853bcd98b0fdcc4db47184c` | None for the selected header closure |
| AmbiqSuite Apollo510 | 100% | 5.1.0 `5efc0228528a8adce5eae0d226fac85d2551eb3b` | Wider HAL ordinal/port reconciliation |
| AmbiqSuite ANCC profile | 100% source lineage and stock boundary | selected 2.5.1 import `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`; exact 17-definition source/header; implementation identical across authenticated 2.2.0-2.5.1 imports; 12 source-derived and nine G2-local stock functions | Exact private producing release/commit is binary-unobservable; production admission and first-party G2 extension implementation |
| AmbiqSuite AMOTA profile | 100% application-skeleton lineage and G2 OTA boundary | selected 2.5.1 import `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`; exact source/API oracle; stable across four authenticated release imports; four skeleton-derived and three G2-local stock functions | Exact private producing release/commit is binary-unobservable; production admission and first-party Even OTA actions |
| NemaGFX / NemaVG / Ambiq GPU patch | 100% public package identity; NemaGFX stock floor exact | AmbiqSuite 5.1.0 revision `release_sdk5p1p0-634f7c117b`; public tree `e690768a…` at `b853fded…`; NemaGFX 1.4.12; NemaVG 1.1.8; all 11 GPU-patch exports and all 18 stock HAL functions source-qualified | Original IAR/private HAL commits, atomic candidate admission, and hardware validation |
| FreeType | 100% | 2.9.1 `86bc8a95056c97a810986434a3f268cbe67f2902` | Remaining toggles, destructor closure, font payloads, IAR details |
| littlefs | 95–100% | v2.10.1-equivalent `0494ce7169f06a734a7bd7585f49a9fa91fa7318` | Exact historical checkout and golden external-flash capture |
| TLSF | 90–95% | v3.1-compatible `deff9ab509341f264addbd3c8ada533678591905` | Exact historical checkout |
| LZ4 | 90–95% | v1.10.0 `ebb370ca83af193212df4dcbadcc5d87bc0de2f0` | Stock v1.9.4/v1.10.0 discriminator and optional unreachable-stock compaction |
| nanopb | 90–95% | 0.4.9 `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | Vendor 0.4.7–0.4.9.1 discriminator and schemas/generated messages; accumulated Linux/Clang 22 profile is now recorded and twice replayed |
| FlashDB | 90–95% | 2.1.1 `714d6159e7e6afb267a3953756abca445c350e61` | Vendor-checkout proof, schema/non-destructive mount policy, and golden-capture validation |
| Packetcraft Cordio | 100% retained reusable-path/module classification; production-excluded | r20.05–r20.05c public interval ending at `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; r19.02 `86372d84…`; later Ambiq R4 oracle `4264b930…`; R2.5.1 port archive `87b03680…`; GATT, ANCC, AMOTA lineage classified; EUS/ESS/EFS/NUS/Ring proven G2-local; all retained BLE-profile paths closed | Exact mixed producing commit is unobservable; production admission/placement and hardware/controller validation; application/product behaviors remain first-party boundary work |
| LVGL | 95–98% | official-core ceiling `344c7c318047b7348e1be8572a9fd4260c251cfa`; exact Ambiq subtree `1e774257…` at canonical `5be8e0ae…` / replay `67fd93e2…`; exact public Nema package tree `e690768a…`; all seven private display-port functions / 638 stock bytes are source-owned | Whole hybrid-tree and private display-port commits are unobservable; stock GPU/HAL admission, assets, hardware validation, and first-party input/display integration remain |
| EasyLogger | 95–97% | 2.2.99-compatible `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; main output/hexdump integrated; all downstream `elog_async_api.c` queue, callback/consumer, and event-worker/thread algorithms dual-profile qualified | Target concurrency/hardware stress, production admission, exact historical checkout, and image-specific transports |
| FreeRTOS-Plus-CLI | 100% linked reusable behavior | exact C/H interval `43defa56…` through `1309654d…` plus isolated G2 patch; all five linked interpreter entries and console/accessor seams source-owned | Historical checkout is binary-unobservable; descriptors/commands are first-party and static allocation is a future policy choice |
| mpaland/printf | 100% linked behavior | `d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e`; all linked helpers, conversions, variadic core, wrappers, and G2 recursive-pointer extensions source-owned | Exact historical checkout only; no linked functional gap |
| TinyFrame | 99% | authenticated exact core snapshot introduced by `eb75483e035916ef9f3e9fce0d2ae389cb09785f`; checkout interval `eb75483e`…`a29167a69f052975b0e0134a73b4d31d03afa8fa`; all 31 linked functions mapped; single-instance peer-role census, G2 adapter, source-owned heap port, retained sync wrapper, no-op logging policy, and dual-profile 14-function atomic production graph closed | Hardware golden packets; exact historical checkout within the core-identical interval is binary-unobservable |
| CmBacktrace | 70–80% | compatibility selection `73714489f9d8af130aacb515586b397b604a5768` | Exact vendor commit and remaining port/config details |
| AndersKaloer/Ring-Buffer | 100% | selected `190e30bebcec22d7311fd941179d70b4f439c441`; binary-compatible interval starts at `cda00e1efb815bad5100757f0d10d117f633ced6` | Deferred hardware validation; exact Even checkout is not binary-distinguishable |
| First-party `fw_event_loop` | 100% provenance/behavior | clean-room production source; no upstream pin applies | Deferred hardware scheduling validation; retained dependency pool remains stock data |
| EM9305 QP/C | 100% release/family; 95–100% configuration | QP/C v6.5.1 `416dcec8820b9cdb5827497e645d0d9375db53c6`; 36 stock functions match the authenticated SDK archive at known addresses, three internal hooks are proven vendor-modified, the exact QK SWI port is recovered, and the compiler is MetaWare ARC T-2022.09 build 004 / LLVM 14.0.6 at `-Os`; exact private source checkout remains unproven | Named hook callees, unused time-event counter layout, private source tree, and license; see the [ARCompact](research/em9305-qpc-arcompact-audit.md) and [archive](research/em9305-sdk-archive-match-audit.md) audits |
| EM9305 Packetcraft/EM Bleu controller | 100% SDK binary artifact identity; authoritative public source commit/final runtime configuration unresolved | SDK v4.2 `lib_emb_controller.a` blob `6a1a8e3d…` supplies 1,055 address/body fingerprints; ISO, strict, and NOP-aware lanes now identify 202 link-order placements / 11,934 bytes, including 50 exact and 51 same-size or size-delta modified functions; Bluetooth 5.4 `BT_VER=13`, Packetcraft `LL_VER_NUM=28992`, exact MetaWare compiler | Packetcraft public source ends at much older r20.05c/`LL_VER_NUM=1366`; locate authoritative licensed 2024 source and reconcile final-link configuration, or retain cut-forward spans; see the [expanded census](research/em9305-expanded-sdk-archive-census.md), [link-order ledger](research/em9305-sdk-link-order-recovery.md), and [residual census](research/em9305-residual-segment-census.md) |
| EM9305 EM system/HAL/radio support | 100% for matched SDK artifacts; wider source closure incomplete | Two archive censuses pin EM HAL/system/radio, LL PAL, NVM, RC calibration, transport, app-entry/core/stack and AOAD artifacts; boundary-qualified, NOP-aware, vector-ABI, and short-prefix replay produce the 1,494-function exact map | Classify/recreate remaining modified functions and recover redistribution-safe source/configuration |
| EM9305 PML | 100% SDK artifact; source unavailable | SDK v4.2 `lib_pml.a` blob `45c88f15bc6367dc15e3cdcabb9a23be74bb9934`; 44 unique exact stock functions / 3,000 bytes | Recover or recreate proprietary source/configuration; retain exact stock spans meanwhile |
| EM9305 protocol timer | 100% SDK artifact; source unavailable | SDK v4.2 `lib_prot_timer.a` blob `cf8f1f22ea840568c83c6a2662c86e7d95b6581a`; 13 unique exact functions / 932 bytes plus one bounded vendor-modified function | Recreate source/configuration or maintain cut-forward spans |
| EM9305 sleep manager | 100% SDK artifact identity; behavior 70–80% | SDK v4.2 `lib_sleep_manager.a` blob `05af021ac9132dc8c727913c4382eba9019aebdb`; exact RC-cal callback and configured 516-byte sleep manager named | Fully reverse configured sleep policy/ROM seams or cut forward |
| EM9305 sleep timer | 100% SDK artifact; source unavailable | SDK v4.2 `lib_sleep_timer.a` blob `3713f176b7f1614920a3043c4dcb41ba730e3fe0`; three unique exact functions / 128 bytes | Recreate missing store/restore/disable closure or cut forward |
| EM9305 unitimer | 100% matched leaf; wider archive closure incomplete | SDK v4.2 `lib_unitimer.a` blob `07ed4df5a464637adf024d383bc89d2fd0b57bb0`; exact `Timer_RegisterModule` | Match/recreate remaining configured unitimer bodies |
| IAR DLIB runtime | 40–50% provenance; 100% bounded functional source | IAR family; three authenticated `Jul  6 2026` build banners; formal Cortex-M55 support implies a practical EWARM 9.20+ floor; 9.60.2 is the leading compatibility candidate; likely `m7M_tl{v|s}`/`rt7M_tl` archive families, exact release unproven; all 13 bounded runtime code units now have exact or qualified clean-room source and canonical Apple guarded production integration | Exact IAR release, VFP-library variant, Normal/Full DLIB option, release-specific archive comparison, wider DLIB census, Linux profile recording for the newest three leaves, and hardware validation; see the [runtime census](research/iar-dlib-runtime-census.md) and [`frexpf`/`ldexpf` audit](research/iar-dlib-frexpf-ldexpf-recovery.md) |

Every named third-party family in the Apollo-main build tree is identified at
least to a family. IAR DLIB remains the lowest-confidence dependency row and
is deliberately not assigned an exact release until stronger evidence exists.
The authenticated LVGL path/corpus correlation now also maps the complete
178-byte `lv_iter_create` body to `src/misc/lv_iter.c`, including allocation,
field-offset, and assertion-line evidence. It remains production-excluded:
the corpus has no direct caller token, and indirect reachability plus original
relocation/caller closure are unresolved.

## Firmware controller and segment status

| Package/controller domain | Current reconstruction state | Approximate provenance identification | Required next evidence |
|---|---|---:|---|
| Apollo510 main | Mixed: 142,760 source-owned bytes plus 98,402 generated patch bytes and a 3,424,780-byte retained base | 100% coarse origin accounting for the retained base; named upstream families remain 90–100% individually | The retained base now splits into 130,000 third-party-path, 461,468 first-party/project-path, 675,636 unanchored-function, and 2,157,676 outside-envelope bytes; prioritize the unanchored code and preserve conservative residual labels |
| Apollo510 bootloader | Mixed: selected littlefs/EasyLogger/Ambiq leaves recreated; remainder retained | 85–90% | Continue source closure without crossing protected secure-loader boundary |
| EM9305 BLE controller | Cut-forward; QP/C 6.5.1, Packetcraft/EM Bleu Bluetooth-5.4 controller, exact compiler, and 54 SDK archive lanes authenticated. Across 875 merged intervals, 1,494 exact functions cover 157,122 bytes (74.504950%); link-order, vector-ABI, and authenticated short-prefix placements raise function-provenance identification to 167,684 bytes (79.513296%). Residual structure is fully partitioned into vectors, alignment, post-text data, and 33,658 unresolved code-or-mixed bytes | 92–95% overall provenance; QP/C 95–100% configuration; exact-function byte coverage 74.504950% | Resolve/recreate the 33,658-byte code-or-mixed queue and modified vendor seams, and obtain licensed authoritative Packetcraft/EM source or retain cut-forward boundaries |
| Audio codec/DSP | Opaque/cut-forward; proprietary NationalChip image with U-Boot-derived CLI | 25–35% | Resolve both segment destinations and isolate reusable CLI/runtime code |
| Touch controller | Opaque/cut-forward; vector base inferred | 10–20% | Identify controller SDK/library lineage and complete memory map |
| Charging case | Opaque/cut-forward; FreeRTOS family certain | 35–45% | Pin FreeRTOS/HAL versions and STM32G0 configuration |
| Secure Apollo bootloader | Protected and absent from EVENOTA | Not reconstructable from current bundle | Owned-device readout or authoritative vendor source; preserve boundary |

“Cut-forward” means the official bytes remain hash-pinned and can be carried
into a reproducible bundle while their source is unavailable. It is a
compatibility strategy, not a reverse-engineering completion claim.

The exhaustive per-address status is in [`memory-map.md`](memory-map.md).
Each emitted build also generates `build/source/flash-plan.json`, which is the
machine-readable authority for placed, unresolved, and container-only regions.

## Chronological frontier log

The entries below are retained in completion order. The authoritative current
state is the latest entry at the end of the log plus the summary tables above;
earlier size/ownership pins are historical milestones, not current totals.

The newest promoted boundary is nanopb private `read_raw_value` at
`[0x0048F6EA,0x0048F77E)`. Rizin and the fail-closed analyzer prove the
148-byte stock function, sole caller, three calls to the source-owned `pb_read`
provider, and two diagnostics. Apple Clang 21 emits a 134-byte text leaf plus
34 bytes of source-owned rodata at `[0x007B2CC4,0x007B2D6C)`; object, closure,
placement, full-span redirect, component, package, and ownership pins are
complete. The resulting overlay/component/package sizes are
125,512/3,648,908/4,427,402 bytes, with 1,040 placed and two unresolved flash
regions. The reviewed Linux/Clang 22 profile remains fail-closed pending access
to that compiler; no Linux value was inferred from Apple output.

The following `pb_make_string_substream` span at
`[0x0048F77E,0x0048F7CA)` is now source-recreated. Its 72-byte text and 24-byte
diagnostic closure occupy `[0x007B2D6C,0x007B2DCC)`; explicit field copies
remove the stock `__aeabi_memcpy` seam. Overlay/component/package sizes are
125,608/3,649,004/4,427,498 bytes with 1,042 placed flash regions. The next
nanopb boundary audit begins at `0x0048F7F4` after the already source-owned
close-substream helper.

The public `pb_decode_bool` body `[0x0049012C,0x00490150)` and private
`pb_dec_bool` adapter `[0x004901CC,0x004901D6)` are now source-recreated. Apple
places 28-byte and 6-byte leaves at `[0x007B2DCC,0x007B2DEE)`, with both
relocations resolving to source-owned nanopb providers. Current
overlay/component/package sizes at that milestone were
125,642/3,649,038/4,427,532 bytes, with 1,046 placed and two unresolved flash
regions. That milestone selected `pb_dec_varint` at
`[0x004901D6,0x00490352)` as the next low-level runtime frontier; the larger
`decode_basic_field` dispatcher at `[0x0048F7F4,0x0048F968)` remains identified
but should follow its scalar providers.

Private `pb_dec_varint` at `[0x004901D6,0x00490352)` is now also
source-recreated. Rizin and the fail-closed analyzer close the 380-byte stock
body, its sole exterior entry, all three provider calls, two diagnostic
strings, and all wide/narrow branch and stored-pointer ingress forms. Apple
places 304 text bytes and 36 diagnostic bytes at
`[0x007B2DF0,0x007B2F44)`. Current overlay/component/package sizes are
125,984/3,649,380/4,427,874 bytes, with 1,050 placed and two unresolved flash
regions. The next scalar-provider frontier is private `pb_dec_bytes` at
`[0x00490358,0x004903EA)`; the six-byte literal island at
`[0x00490352,0x00490358)` remains separately opaque and pinned.

Private `pb_dec_bytes` at `[0x00490358,0x004903EA)` is now source-recreated.
The fail-closed analyzer closes its sole direct caller, two source-owned
provider calls, three diagnostics, and all branch/pointer ingress forms. Two
raw four-byte matches were independently classified by Rizin as 16-bit pair
table records rather than executable pointers. Apple places 98 text bytes and
48 diagnostic bytes at `[0x007B2F44,0x007B2FD6)`. Current
overlay/component/package sizes are 126,130/3,649,526/4,428,020 bytes, with
1,054 placed and two unresolved flash regions. The next contiguous nanopb
frontier is private `pb_dec_string` at `[0x004903EA,0x00490488)`; the six-byte
literal island at `[0x00490352,0x00490358)` remains opaque and separately
pinned.

Private `pb_dec_string` at `[0x004903EA,0x00490488)` is now source-recreated.
The fail-closed analyzer closes its sole direct caller, two source-owned
provider calls, three diagnostics, and all branch/pointer ingress forms.
Apple places a two-byte alignment span, 114 text bytes, and 49 diagnostic
bytes at `[0x007B2FD6,0x007B307B)`. Current overlay/component/package sizes
are 126,295/3,649,691/4,428,185 bytes, with 1,058 placed and two unresolved
flash regions. After the separately pinned four-byte literal island at
`[0x00490488,0x0049048C)`, the next contiguous nanopb frontier is private
`pb_dec_submessage` at `[0x0049048C,0x00490538)`.

Private `pb_dec_submessage` at `[0x0049048C,0x00490538)` is now
source-recreated with explicitly partial closure. The fail-closed analyzer
pins its sole caller, source-owned substream make/close calls, local diagnostic,
application callback ABI, and one retained fixed stock call to
`pb_decode_inner` at `0x0048FE98`. Apple places one alignment byte, 138 text
bytes, and 25 diagnostic bytes at `[0x007B307B,0x007B311F)`. Current
overlay/component/package sizes are 126,459/3,649,855/4,428,349 bytes, with
1,063 placed and two unresolved flash regions. The next dependency frontier
is private `pb_decode_inner`; the successor literal island at
`[0x00490538,0x0049053C)` remains separately opaque.

No signing, flashing, erase, filesystem mutation, or physical device operation
is authorized by these estimates.

## Latest milestone: FreeRTOS priority-inheritance, IAR scanset, littlefs size leaf

Apollo main now source-owns `xTaskPriorityInherit` (`[0x004558CC,0x0045596E)`,
162 bytes), `vTaskPriorityDisinheritAfterTimeout` (`[0x00455A1C,0x00455ACA)`,
174 bytes), the IAR DLIB scanset matcher `open_cfw_iar_scanset_match`
(`[0x004D2112,0x004D2158)`, 70 bytes, byte-identical), and the littlefs
`lfs_file_size` public wrapper (`[0x004CFC2E,0x004CFC5C)`, 46 bytes; recovered
`lfs_t.mlist` at `0x28`).

Current overlay/component/package sizes are `142986 / 3666382 / 4444876`. The
apple-clang canonical build, byte-identical package, manifest verify, and Apollo
origin accounting pass fail-closed; the linux-clang profile pins await a Linux
toolchain regeneration.

## Latest milestone: nanopb private decoder loop

Private `pb_decode_inner` at `[0x0048FE98,0x00490112)` is now
source-recreated with explicitly partial helper closure. Rizin and the
fail-closed analyzer authenticate the 634-byte single-entry body, both direct
callers, no interior ingress, all outgoing calls, four diagnostics, neighboring
literal/wrapper spans, and 19 non-pointer table/text collisions. Apple places
one alignment byte, 522 text bytes, and 88 diagnostic bytes at
`[0x007B311F,0x007B3382)`. The stock memory-fill dependency is eliminated and
`pb_skip_field` is source-owned; six helper families remain pinned stock seams.

Current overlay/component/package sizes are
`127070 / 3650466 / 4428960`, with 1,068 placed, two unresolved, and five
container-only regions. Package ownership is 127,832 source bytes (2.886276%),
90,501 generated bytes (2.043392%), and 4,210,627 opaque/cut-forward bytes
(95.070333%); controlled ownership is 218,333 bytes (4.929667%). The next
nanopb frontier is the retained helper family: `pb_decode_tag`, defaults,
iterator operations, extension decoding, and `decode_field`. Linux/Clang 22
and hardware validation remain deferred.

## Latest milestone: nanopb tag decoder and short-enum ABI

Public `pb_decode_tag` at `[0x0048F66C,0x0048F6A0)` is now source-recreated
and source-closed. The analyzer authenticates its 52 bytes, three callers, sole
varint32/eof provider, neighboring functions, no alternate ingress, and no
stored pointers. Three stock `STRB` sites prove G2's one-byte
`pb_wire_type_t`; correcting the decoder-loop temporary changes its Apple text
from 522 to 530 bytes. The tag leaf adds two alignment bytes and 42 text bytes
at `[0x007B338A,0x007B33B6)`.

Current overlay/component/package sizes are
`127122 / 3650518 / 4429012`, with 1,070 placed, two unresolved, and five
container-only regions. Package ownership is 127,882 source bytes (2.887371%),
90,555 generated bytes (2.044587%), and 4,210,575 opaque/cut-forward bytes
(95.068042%); controlled ownership is 218,437 bytes (4.931958%). The private
decoder loop now retains six stock calls across five helper families. The next
frontier is `pb_message_set_to_defaults` and its iterator/default-value
dependencies; Linux/Clang 22 and hardware validation remain deferred.

## Latest audit: nanopb message defaults and accelerated source inference

`pb_message_set_to_defaults` is now bounded at
`[0x0048FDF2,0x0048FE98)`: 166 stock bytes, four direct callers, no alternate
or interior ingress, and no stored-pointer ingress. Its authenticated nanopb
0.4.9 source definition is `pb_decode.c[31080:32048]`. Four of seven outgoing
call sites already resolve to source-owned `pb_istream_from_buffer` and
`pb_decode_tag`; the remaining closure is only `decode_field`,
`pb_field_iter_next`, and `pb_field_set_to_default`. Boundary, source identity,
and call closure are 100% identified; source recreation and production
integration remain 0%, so package ownership stays 2.887371% source, 2.044587%
generated, and 95.068042% opaque/cut-forward.

The workflow now explicitly uses remembered upstream lineage and intermittent
web research to generate candidates, followed by immutable Git-object/source
span pins and release/commit compile matrices for proof. Local Ghidra 12.1.2
headless/PyGhidra and Rizin 0.9.1 were inventoried. Rizin produced this audit;
Ghidra requires the installed Homebrew OpenJDK 21 through an explicit
`JAVA_HOME`. `rz-ghidra`, BinDiff/BSim, and a disposable loopback-only Ghidra
MCP evaluation are the next tooling accelerators. See
`research/reverse-engineering-acceleration-strategy.md`.

## Latest audit: nanopb field-default recursion

`pb_field_set_to_default` is now 100% bounded and upstream-identified at
`[0x0048FCE2,0x0048FDF2)`: 272 stock bytes, one direct caller, five outgoing
calls, no alternate/interior ingress, and no stored-pointer ingress. A
four-release checkout matrix proves its 2,604-byte source definition is
byte-identical at nanopb 0.4.7, 0.4.8, 0.4.9, and 0.4.9.1. This narrows the
function to an exact compatibility interval but does not uniquely prove the
vendor checkout.

Rizin and a five-second targeted Ghidra noanalysis decompile independently
match extension recursion, optional/repeated/oneof initialization, submessage
recursion, static zeroing, and pointer reset. Pairing this function with the
already audited message-defaults loop will internalize three calls and remove
the released memory-fill dependency. The paired 438-byte candidate then has
only four fixed helper families: iterator begin, iterator begin-extension,
iterator next, and `decode_field`. Source recreation/integration remain 0%, so
package ownership remains 2.887371% source, 2.044587% generated, and
95.068042% opaque/cut-forward.

## Latest milestone: nanopb iterator production integration and release correction

The complete `[0x004D916E,0x004D9522)` nanopb `pb_common.c` iterator cluster
is now 100% bounded and source-recreated: 948 stock bytes across eleven
functions, with every direct caller, sixteen fixed calls, two dynamic callback
sites, one legitimate stored function pointer, and one classified data-island
branch collision authenticated. Nine isolated source leaves now production-route
all eight live iterator/callback entries through reviewed full-span redirects.
The 536 unreachable private stock bytes remain opaque rather than overclaimed.

This cluster closes six decoder/defaults call sites across five unique
iterator entries. Its only stock fixed dependency, the released memory-fill
routine, is removed by a local loop. A multi-address Ghidra noanalysis pass
decompiled seven functions in 6.3 seconds and independently matched the compact
descriptor ABI recovered by Rizin.

The Apple overlay/component/package are now 128,264 / 3,651,660 / 4,430,154
bytes. Package ownership is 129,014 source bytes (2.912179%), 90,977 generated
bytes (2.053585%), and 4,210,163 opaque bytes (95.034236%). The manifest has
1,022 Apollo-main regions and the flash plan places 1,094 regions with two
unresolved and five container-only records.

The upstream release audit now includes nanopb 0.4.9.1. Its only runtime
behavior change from 0.4.9 is in dead-stripped `pb_decode_ex`, and the firmware
build timestamp postdates the release. The corrected pristine candidate range
is 0.4.7--0.4.9.1; selected baseline 0.4.9 remains a compatibility choice, not
claimed vendor provenance.

## Latest milestone: nanopb paired defaults production integration

Private `pb_field_set_to_default` and `pb_message_set_to_defaults` are now
100% source-recreated and production-integrated. The complete 438 stock bytes
at `[0x0048FCE2,0x0048FE98)` are full-span redirects. Apple places 158 bytes
of message-default text at `0x007B382C`, two alignment bytes, and 256 bytes of
field-default text at `0x007B38CC`. The pair internalizes recursive defaults,
uses the source-owned iterator/stream/tag leaves, and removes the released
memory-fill dependency; only `decode_field @ 0x0048FBE4` remains fixed stock.

The Apple overlay/component/package are now 128,680 / 3,652,076 / 4,430,570
bytes. The 1,027-region Apollo manifest and 1,099 placed flash records account
for 129,428 source bytes (2.921249%), 91,417 generated bytes (2.063324%), and
4,209,725 opaque bytes (95.015427%). Two flash records remain unresolved and
five are container-only. Linux/Clang 22 replay and hardware execution remain
deferred; the next contiguous nanopb frontier is `decode_field` and its
extension/dispatch closure.

## Latest milestone: nanopb dispatch and extension production integration

Private `decode_field`, `default_extension_decoder`, and `decode_extension`
are now 100% bounded, upstream-identified, source-recreated, and
production-integrated. This corrects the old boundary label at `0x0048FC26`:
that entry is `default_extension_decoder`; `decode_extension` begins at
`0x0048FC88`. Three guarded redirects cover the executable stock spans, while
the 16-byte literal island `[0x0048FC78,0x0048FC88)` remains explicitly
opaque/cut-forward.

The source definitions are pinned to nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Official-tag comparison shows
the three exact definitions are byte-identical from 0.4.4 through 0.4.9.1;
this establishes compatibility but does not uniquely identify the vendor
checkout. Apple places the closures/leaves at `0x007B39CC`, `0x007B3A14`, and
`0x007B3A70`; only the dynamic extension callback remains an intentional ABI
seam.

The production nanopb allowlist is now 38 functions. The reviewed Apple
overlay/component/package sizes are `128924/3652320/4430814`, and the
1,035-region Apollo manifest yields 1,107 placed, two unresolved, and five
container-only flash records. Package ownership is 129,671 source bytes
(2.926573%), 91,656 generated bytes (2.068604%), and 4,209,487 opaque or
cut-forward bytes (95.004823%); total controlled ownership is 4.995177%.

The next contiguous nanopb frontier is the field-decoder cluster:
`decode_static_field @ 0x0048F968`, the no-malloc pointer stub at
`0x0048FB1C`, and `decode_callback_field @ 0x0048FB30`, with
`decode_basic_field @ 0x0048F7F4` as the likely predecessor closure. Linux
aggregate replay, signing/flashing, and hardware execution remain deferred.

## Next-frontier seed: nanopb field decoders

Rizin and targeted Ghidra have now split and semantically checked the complete
1,008-byte field-decoder cluster `[0x0048F7F4,0x0048FBE4)`. Boundary/direct
call identification is 100%, semantic recovery is approximately 95%, and
source recreation/integration remain 0%. All external executable calls already
route to source except `pb_dec_fixed_length_bytes [0x0049053C,0x004905A8)`;
the two callback `BLX` sites are intentional schema ABI.

Official-tag source comparison shows `decode_basic_field` unchanged across
0.4.4--0.4.9.1, the current static definition from 0.4.5 onward, and current
pointer/callback definitions from 0.4.6 onward. The efficient next promotion
unit is the four-function cluster plus the 108-byte fixed-length-bytes decoder.
See `research/nanopb-field-decoder-cluster-boundary-audit.md`.

## Latest milestone: nanopb field-decoder production integration

The complete four-function field-decoder cluster
`[0x0048F7F4,0x0048FBE4)` plus `pb_dec_fixed_length_bytes`
`[0x0049053C,0x004905A8)` is now 100% bounded, upstream-identified,
source-recreated, host-qualified, and Apple-production-integrated. Five
guarded full-span redirects replace 1,116 stock executable bytes. The five
selector-isolated Apple closures contribute 1,132 source bytes and eight
alignment bytes at `[0x007B3AC0,0x007B3F34)`. All fixed calls resolve to
source-owned providers; the two dynamic callback sites remain intentional
application/schema ABI.

The fail-closed analyzer authenticates five stock entries, 26 fixed outgoing
calls, eight diagnostics, both callback sequences, all upstream definitions,
no stored entry pointers, and every apparent branch/pointer collision. Ten
host and target tests pass. The production nanopb allowlist is now 43
functions.

Current overlay/component/package sizes are
`130064/3653460/4431954`. The 1,049-region Apollo manifest and current flash
plan place 1,121 regions, preserve two unresolved records, and skip five
container-only records. Package ownership is 130,803 source bytes
(2.951362%), 92,780 generated bytes (2.093433%), and 4,208,371 opaque or
cut-forward bytes (94.955205%); controlled ownership is 223,583 bytes
(5.044795%). Linux/Clang 22 replay and hardware execution remain deferred.

## Latest milestone: AndersKaloer/Ring-Buffer production integration

The complete seven-function stock cluster at
`[0x00598134,0x0059823C)` is now upstream-identified, ABI-recovered,
host-qualified, and Apple-production-integrated. The authenticated compatible
commit interval is `cda00e1...190e30b`; `190e30b` is the maintained
source-equivalent selection, not an overclaim about Even's exact checkout.
Seven guarded redirects replace all 252 callable stock-span bytes (250
instructions plus two alignment bytes). The relocated
production leaves add 248 source bytes and four generated alignment bytes at
`[0x007B3F34,0x007B4030)` while reusing the authenticated stock assertion
provider and diagnostic strings.

Current overlay/component/package sizes are
`130316/3653712/4432206`, with package SHA-256
`a5625a4bcc1ff20ff9e339f9bb0a074d999508674c7aeb315101e653c90630c2`.
The 1,067-region Apollo manifest produces 1,139 placed, two unresolved, and
five container-only flash records. Ownership is 131,051 source bytes
(2.956789%), 93,036 generated bytes (2.099090%), and 4,208,119 opaque bytes
(94.944120%); controlled ownership is 224,087 bytes (5.055880%). Linux/Clang
replay and hardware execution remain deferred.

## Latest milestone: IAR void-EABI memory providers production integration

The authenticated `__aeabi_memmove` span `[0x00439710,0x004397A6)` and
`__aeabi_memcpy` span `[0x00439BE4,0x00439C8A)` are now 100% bounded,
ABI-recovered, source-recreated, host-emulated, instruction-count-qualified,
and production-integrated. The overlapping memcpy ownership is represented as
disjoint public and aligned-entry redirects. Three relocation-free source
sections add 626 bytes at `[0x007B4030,0x007B42A2)`; 316 stock bytes move from
opaque to generated ownership.

Apple overlay/component/package pins are
`130942/3654338/4432832`, with package SHA-256
`dbd7327ff42d80c8ff3b728ff9843f3a2b6e9bde3786bd68b929588d677539d5`.
The 1,075-region Apollo manifest produces 1,147 placed, two unresolved, and
five container-only records; the 822,357-byte flash plan hashes to
`27f1d981fb4e7ede7c0d39d4dfb15a039d309b4677a02c157ae9509b7d14ea9b`.
Package ownership is 131,677 source bytes (2.970494%), 93,352 generated
(2.105922%), and 4,207,803 opaque (94.923584%); controlled ownership is
225,029 bytes (5.076416%).

Lorelei recorded and twice replayed Linux overlay/component/package pins
`132810/3656206/4434700`, with package SHA-256
`03ec13df126c98f679e6e85c79cefea447943e746e74c8652e57ff71785ce2bf`.
The Linux plan places 896 regions with two unresolved. Hardware timing remains
deferred; exact EWARM release and DLIB archive options remain unresolved.

## Latest milestone: IAR `sqrtf` and errno quartet production integration

The final four retained code units in the bounded IAR census now have
selector-isolated clean-room source: hard-float `sqrtf`, EDOM and ERANGE
setters, and the errno-address accessor. Apple Clang 21 and Lorelei Linux
Clang 22.1.8 emit identical 28/20/20/10-byte section pins. The `sqrtf` leaf has
one declared tail relocation to the candidate EDOM helper; all other sections
are relocation-free.

Lorelei Unicorn matched 4,000 float bit patterns and 500 randomized executions
for each errno helper against authenticated stock, for 5,500 executions total.
Four stock-hash-guarded full-span redirects now install the 78 source bytes,
moving the final 72 bounded IAR executable bytes from opaque to generated
ownership. Bounded IAR source recreation and production integration are both
10/10 code units; no executable unit in this census remains retained.

Apple places the leaves at `[0x007B42A2,0x007B42F0)` and twice replayed
overlay/component/package sizes `131020/3654416/4432910`. Lorelei places them
at `[0x007B49EE,0x007B4A3C)` and twice replayed
`132888/3656284/4434778`. Canonical package ownership is 131,755 source
(2.972201%), 93,424 generated (2.107510%), and 4,207,731 opaque/cut-forward
(94.920289%); controlled ownership is 225,179 bytes (5.079711%). Exact EWARM
archive provenance remains independently unresolved.

## Latest tooling decision: Ghidra MCP remains an amortized lane

A disposable evaluation pinned `clearbluejar/pyghidra-mcp` v0.2.5 at
`f29063b8636100b71e9c3aec61fe056827c556e4`. It successfully opened a Ghidra
12.1.2 project and exposed 20 initial tools over stdio, but rejects raw
`BinaryLoader` imports and fails closed on read/decompile calls until a project
is marked fully analyzed. The current authenticated-address workflow obtains
multi-function decompilation in about five seconds with `-noanalysis`, so MCP
is deferred until semantic search or repeated whole-project exploration can
amortize full analysis/indexing. Details and resolved dependency versions are
in `research/reverse-engineering-acceleration-strategy.md`.

## Latest milestone: EM9305 ARCompact QP/C release ceiling

The controller application is now analyzed as Synopsys ARC EM7D/ARCv2 EM,
matching EM Microelectronic's documented QP/C-derived ARC framework. A
disposable Apache-2.0 Ghidra ARC extension, GNU ARC binutils on Lorelei, and
local Rizin bound a
3,052-byte assertion-rich cluster, a 144-byte QK scheduling candidate, the
60-byte eight-label module table, and all 31 direct calls to the shared
assertion handler. Twenty-nine calls are assigned to six portable QP modules;
the other two are `MyApp` and `WsfOs`. All remain stock-retained; this
milestone changes provenance and semantic coverage, not package byte ownership.

The decoded QK assertion-500 path checks only `p != 0`, retaining the v6.6.0+
ceiling. The 188-byte stock `QActive_post_` body restores interrupt status for
critical assertions (v6.3.2 behavior) and moves dynamic-event reference
increment ahead of the status branch (v6.3.6 behavior). Together these set an
official portable-body ancestry floor at v6.3.6 commit
`5550cca87dedf72d45250ad01e9cdeee8c4140ba`. Seven tags in six complete
eight-file source epochs survive through v6.6.0+; a vendor backport is still
possible. This raises QP/C release/configuration identification to 90–95%.
The QK ID-189 macro callsite
also matches `qk.c:189` throughout the checked interval. Object accesses recover `QF_MAX_ACTIVE=16`,
`QF_MAX_EPOOL=2`, two-byte signals, one-byte event-queue counters, two-byte
memory-pool size/counters, a 16-bit QK ready set, disabled Q-SPY, and the ARC
`CLRI; SYNC` / `SETI` critical-section ABI. `QF_init` additionally proves
`QF_MAX_TICK_RATE=0`, a 36-byte `QActive`, and an 8-byte `QK_attr_`.
Twenty-two portable functions from eight source units now occupy 2,450
hash-pinned bytes. The 602-byte complement is independently partitioned into
23 state-labeled, hash-pinned segments without gaps or overlaps. The
fail-closed analyzer and twelve tests reproduce the
stock identity, boundaries, 22 module references, 31-call topology, complete
module assignments, and six-instruction QK fingerprint. Full evidence is in
`research/em9305-qpc-arcompact-audit.md`.

The expanded ARCv2 EM epoch builder compiles all 80 comparison objects with
Lorelei's disposable GCC 16.1.1/binutils 2.46 toolchain and reduces ten source
epochs to seven normalized code epochs in 12.63 seconds at four jobs. The
objects are comparison-only and do not claim the stock compiler or vendor
port. The `--stock-compatible-only` lane builds 48 objects across six epochs
in 8.82 seconds and reduces them to three normalized code epochs. Three
builder-helper tests, three ARCv2-wrapper tests, and twelve analyzer tests pass.

## Latest milestone: EM9305 QP/C 6.5.1 and hook closure

A hash-pinned public EM9305 SDK v4.2 source oracle now selects exact upstream
QP/C release 6.5.1, official commit
`416dcec8820b9cdb5827497e645d0d9375db53c6`, from the independently recovered
v6.3.6--v6.6.0+ binary interval. The oracle is third-party commit
`e4412bc98d4e76d441d1226ca3696e53cfae5f54`, tree
`f5cb9ba00df71c2612d6d64cf39e05615a2feb64`; it is not proof of EM's exact
private checkout and is not accepted as licensed production source.

A 16-way isolated Lorelei Ghidra batch completed all EM9305 shards in
24.714--28.462 seconds and returned hash-manifested logs/status/results. Correlated
with the SDK symbols, GNU ARC decoding, Rizin, and raw stock pointers, it names
`QF_onResume`, `QF_onStartup`, inline `QF_resume`, `QK_onIdle`, `Q_onAssert`,
all extension/internal hooks, seven RAM callback globals, and nine terminal
function-pointer entries. At this intermediate milestone, the 602-byte cluster
complement was fully partitioned but its anonymous executable remainder was
concentrated in the 280-byte pre-QP hardware/port span plus internals of named
retained hooks; the following archive-comparison milestone supersedes that
classification and reduces anonymous executable cluster bytes to zero.
The full `Q_onAssertExt` boundary and 36-byte hook table are hash-pinned.

The analyzer now authenticates the SDK commit/tree and four oracle blobs as an
optional fail-closed input. Fourteen analyzer tests plus three epoch-builder
and three ARC-wrapper tests pass; the full 20-test EM9305 group also passes.

## Latest milestone: EM9305 vendor archive and compiler fingerprint closure

The SDK oracle contains relocation-bearing ARCv2 object archives. A new
fail-closed comparator authenticates QP/C, PML, sleep-manager, sleep-timer,
protocol-timer, and unitimer archives; masks only the four known ARC relocation
types; and scans every halfword-aligned application address. Six enforced
Lorelei lanes require 98 exact stock functions/7,172 bytes. Ninety-two are
globally unique fingerprints totaling 7,146 bytes; three QP internal hooks are
separately required to remain vendor-modified.

All 22 portable QP/C bodies now match the SDK build rather than merely a source
epoch. Archive metadata pins Synopsys MetaWare ARC T-2022.09 build 004 / LLVM
14.0.6, EM-Micro ARCv2 EM, `-Os`. The exact QK SWI port occupies
`[0x00302518,0x00302664)`, and `BSP_Init` is unique at
`[0x00302E80,0x00302E8E)`.

The former 280-byte anonymous QP-cluster prefix is now a protocol-timer
closure: a vendor-modified `ProtTimer_SetHwTriggerEnable` tail, exact
`ProtTimer_StoreConfig`, alignment, and exact
`ProtTimer_UpdateRestartTime`. Consequently all 3,052 cluster bytes are
function-identified across 26 hash-pinned remainder segments; anonymous
executable cluster bytes are zero. The 516-byte idle callee is named
`SLEEP_MANAGER_GoToSleep`, and its adjacent 52-byte RC-calibration callback is
an exact archive match. Full evidence is in
`research/em9305-sdk-archive-match-audit.md`.

## Latest milestone: EM9305 two-round Packetcraft/SDK function census

The optimized relocation matcher now uses an unmasked byte-run anchor followed
by a complete normalized comparison. It remains equivalent to exhaustive
halfword scanning but reduces the enforced QP/C archive lane to 0.32 seconds
on Lorelei. A new authenticated 16-job batch applies a 16-compared-byte floor
to controller, peripheral, LL PAL, EM system/HAL, radio, NVM, RC-calibration,
transport, and support archives. All 16 lanes passed; the largest profile
completed in 12.228 seconds.

The first raw 2,180 match records collapse without body conflicts to 1,146
distinct, non-overlapping stock functions / 132,610 bytes. A second
authenticated 32-archive pass produced 8,542 records / 1,201 distinct
address-body identities. Global deduplication rejects 1,134 already-proven
identities and promotes 67 new functions / 13,078 bytes. Together with the
prior six archives, the conservative lane covers 1,311 exact functions /
152,860 bytes. An 8-byte replay yields 129 additional candidates; independent
entry-boundary/xref qualification promotes 124 / 2,106 bytes and withholds
five. Exact-neighbor link-order tiling subsequently resolves 16 more exact
functions / 784 bytes and identifies 30 non-exact functions / 1,332 bytes.
The NOP-aware extension adds 156 functions / 9,818 stock bytes, including 34
exact bodies. Vector ABI resolution adds three exact interrupt handlers / 574
bytes and identifies the 186-byte modified radio-TX handler. The current exact
map is 1,494 functions in 875 intervals / 157,122 bytes, or 74.504950% of the
complete EM9305 application. Function provenance is identified for 167,684
bytes (79.513296%). The 43,204-byte remainder is partitioned into 264 vector
bytes, 1,812 alignment bytes, 7,470 post-text table/data bytes, and 33,658
unresolved code-or-mixed bytes.

`lib_emb_controller.a` is exact at 1,057 records / 1,055 address-body
fingerprints and proves the EM Bleu/Packetcraft Bluetooth-5.4 controller
profile (`BT_VER=13`, `LL_VER_NUM=28992`). Its 77 controller-only fingerprints
exclude the Bluetooth-5.2 peripheral profile as a complete stock explanation.
The second pass's `lib_emb_controller_iso.a` adds 62 ISO/BIG functions / 12,624
bytes, while `lib_em_system_di03.a` adds four NVM functions and `lib_aoad.a`
adds `AOAD_Init`. This exact link-time evidence means the adjacent non-ISO
profile header cannot be treated as the complete stock-link configuration,
although it does not by itself prove runtime activation of every ISO path.
Packetcraft's public repository stops at r20.05c/`LL_VER_NUM=1366`, so the
exact 2024 source state is pinned only to authenticated SDK blobs and remains
proprietary/unavailable as an authoritative public commit. The dynamic
per-function map and all report hashes are enforced by
`tools/analyze_em9305_sdk_discovery.py`; full evidence is in
`research/em9305-expanded-sdk-archive-census.md`.

The link-order analyzer now enforces 156 ranges / 202 functions across strict
and NOP-aware tiers. Its first nine same-size modified placements compare 942
of 1,008 non-relocation bytes exactly; the next 29 compare 3,815 of 3,868
(98.630%). The dominant deltas remain configuration/ABI changes, including a
912-byte stock connection-context stride versus the SDK's 900-byte layout.
Full status is in `research/em9305-sdk-link-order-recovery.md` and
`research/em9305-residual-segment-census.md`.

The next 16-way Lorelei Ghidra batch assigns separate large residual gaps to
isolated projects. All lanes completed in 17.644--17.993 seconds. The
experimental ARCompact decompiler emitted unusable constructor p-code for 15
entries; those remain candidate-only. Its one coherent 12-byte result is
independently exact-matched and named
`lctrSlvCheckEncOverridePowerControl @ 0x00329554`, so no Ghidra-only semantic
claim enters the ledger. Returned hashes and paths are pinned in the
[Lorelei benchmark](research/lorelei-re-acceleration-benchmark.md).

A third 16-way Lorelei batch targeted individual NOP-aware modified-function
entries and completed all projects in 16.766–17.023 seconds. The experimental
ARC processor produced no promotable semantics, but archive/GNU comparison
confirmed the 29 same-size identities at 98.630% aggregate meaningful-byte
similarity. Returned hashes, per-state residual accounting, and the remaining
33,658-byte queue are pinned in the
[residual segment census](research/em9305-residual-segment-census.md).

A fourth 16-way Lorelei batch processed 5,922 bytes across 16 previously
unprocessed residual spans in 17.217–17.502 seconds with no process failure.
Three entry-level decompilations were coherent and 13 hit the experimental ARC
constructor defect. Vector ABI and normalized archive matching subsequently
resolve the duplicated timer/radio interrupt wrappers: three exact bodies / 574
bytes and one modified 186-byte radio-TX role. The return-12 leaf remains
candidate-only.

## Current Cordio SMP-main identification increment

The retained G2 `smp_main.c` module is now source-identified across all twenty
linked functions / 3,076 code bytes in `[0x00537278,0x00537EEC)`. The one
remaining public API, `SmpDmGetLtk`, has no stock caller, pointer, or body and
is classified dead-stripped, leaving zero linked functions opaque within this
translation unit. Stock combines Packetcraft r20.05-family `keyReady` and
LESC behavior with AmbiqSuite 2.5.1's stale-AES queue cleanup. A tracked patch
over the authenticated Apache-2.0 r20.05c source reconstructs that combined
semantic candidate without claiming exact downstream text.

Lorelei compiled both the public and patched sources under `-Os` and `-O1`.
The two patched links retain code/BSS and close all 32 provider seams; the two
base links retained no code and are explicitly rejected as vacuous closure
evidence. The returned 5,247-byte archive and distilled ledgers are now
repository-owned and fail-closed. These bytes remain cut forward in
production: linked-function identification is 100%, while source recreation
and replacement remain 0% pending exact IAR/RTOS, logger, placement, and
relocation closure. See `docs/research/cordio-smp-main-source-recovery.md`.

## Current Cordio SMP secure-connections-main identification increment

The retained G2 `smp_sc_main.c` object is now source-identified across all 18
linked functions / 2,626 code bytes in `[0x0056CDC0,0x0056D8C4)`. Four public
definitions (`SmpScFree`, both peer-public-key accessors, and `SmpScSetOobCfg`)
have no stock body, caller, or stored pointer and are classified dead-stripped.
The remaining 194 bytes are bounded alignment and literal data.

Packetcraft r20.05 through r20.05c provides an invariant Apache-2.0 source
oracle. The stock event-name table includes `SMP_MSG_INT_CLEANUP` at `0x1F`,
which excludes the r19/AmbiqSuite 2.x message layout independently of adjacent
modules. The analyzer closes 111 exact-entry calls and rejects the only two
raw interior-looking byte windows as unaligned data overlaps. Production
ownership remains zero; see
`docs/research/cordio-smp-sc-main-source-recovery.md`.

## Current Cordio SMP secure-connections state-machine increment

The paired initiator/responder state-machine units now account for 2,431
identified bytes: 598 code bytes, 338 physical literal/pointer bytes, and 1,495
scattered interface/action/state-table bytes. The initiator object is
`[0x00537F14,0x005380DC)`; the responder object is
`[0x00538104,0x005382E4)`. All four source functions link and none is
dead-stripped.

Packetcraft r20.05--r20.05c is the exact public source oracle. Stock's
responder interface selects 55 actions and its API-pair-request table contains
the r20-only response-timeout and cleanup rows; r19/AmbiqSuite 2.x has 54
actions and neither row. The analyzer traverses and hashes all 80 state tables,
closes four exact callers, and finds no stored function entry or interior.
Production ownership remains zero; see
`docs/research/cordio-smp-sc-state-machines-source-recovery.md`.

## Current Cordio SMP common-action identification increment

The retained `smp_act.c` unit is now closed across all 25 definitions and the
full `[0x0056E5CC,0x0056F178)` object: 2,924 code bytes plus 64 bytes of owned
categories, literals, and alignment. The analyzer pins 78 direct calls and 62
stored action/callback entries and proves there is no stored strict-interior
address. No source definition is dead-stripped.

Packetcraft r20.05 through r20.05c supplies one invariant Apache-2.0 source
blob. Stock retains the r20-only security-request-timeout action and guarded
SC trace logic, independently excluding r19/AmbiqSuite 2.x. Production
ownership remains zero; see
`docs/research/cordio-smp-act-source-recovery.md`.

## Current Cordio SMP responder-action identification increment

The complete stock `smpr_act.c` object is now closed at
`[0x005E38C8,0x005E3D7C)`: all ten definitions contribute 1,160 code bytes
and three owned non-code ranges contribute 44 bytes. The legacy and Secure
Connections responder tables each retain all ten action entries. The only two
direct entry calls are intentional intra-TU helper calls; the whole-image scan
finds 20 exact stored entries and no strict-interior pointer.

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share one exact Apache-2.0 blob. Stock writes `keyReady=TRUE` at
`smpCcb_t+0x44` after storing the responder STK, selecting that source family
over r19/AmbiqSuite 2.x, whose body lacks the assignment. Production ownership
remains zero; see `docs/research/cordio-smpr-act-source-recovery.md`.

## Current Cordio SMP initiator-action identification increment

The complete stock `smpi_act.c` object is closed at
`[0x005E3118,0x005E3474)`: all ten definitions contribute 852 code bytes and
the owned `pSmpCfg`/`smpCb` island contributes eight bytes. Both initiator
action tables retain all ten entries, yielding 20 exact roots and no stored
strict-interior address. A lone raw BL-like hit is explicitly rejected as the
second halfword of a wide multiply.

Stock also writes `keyReady=TRUE` at `smpCcb_t+0x44` after deriving the
initiator STK. That r20 addition independently excludes r19/AmbiqSuite 2.x;
Packetcraft r20.05--r20.05c and the later R4.4.1 import share the selected
Apache-2.0 blob. Production ownership remains zero; see
`docs/research/cordio-smpi-act-source-recovery.md`.

## Current Cordio SMP Secure Connections role-action increment

The two role-specific SC action units are now fully closed. Initiator
`smpi_sc_act.c` occupies `[0x005E3474,0x005E38C8)` with all 16 definitions,
1,070 code bytes, and 38 owned tail bytes. Responder `smpr_sc_act.c` occupies
`[0x005E3D7C,0x005E4228)` with all 20 definitions, 1,162 code bytes, and 34
owned tail bytes. Their SC action tables provide 16 and 20 exact entry roots.
The responder's four direct entry calls are internal wrappers; neither unit
has exterior direct entry ingress or a genuine body-interior pointer.

Both stock DH-key-check paths write `keyReady=TRUE` at `smpCcb_t+0x44`. That
r20 addition independently excludes r19/AmbiqSuite 2.x. Packetcraft
r20.05--r20.05c and the later official R4.4.1 import share the selected exact
Apache-2.0 files. Production ownership remains zero; see
`docs/research/cordio-smpi-sc-act-source-recovery.md` and
`docs/research/cordio-smpr-sc-act-source-recovery.md`.

## Current Cordio SMP shared Secure Connections action increment

The complete shared `smp_sc_act.c` object is closed at
`[0x005E267C,0x005E3118)`: 20 linked definitions contribute 2,662 code bytes
and the owned F5/trace/literal tail contributes 54 bytes. The qualification-only
`SmpScEnableZeroDhKey` definition is compiled out by its default-false feature
guard. Nineteen direct calls and 26 stored pointer cells reach exact entries;
no genuine stored or branched address reaches a strict body interior.

Stock retains the `smpScProcPairing` no-input/no-output MITM branch present in
Packetcraft r19/AmbiqSuite 2.x and the later official R4.4.1 import, but removed
from Packetcraft r20.05--r20.05c. Combined with the already proven r20 message
and action-table ABI, this identifies an R4-style vendor hybrid rather than an
exact Packetcraft-r20 whole file. Production ownership remains zero; see
`docs/research/cordio-smp-sc-act-source-recovery.md`.

## Current Cordio SMP legacy state-machine increment

The two remaining legacy role state machines are closed. `SmpiInit` and
`SmprInit` contribute 44 code bytes inside two 40-byte physical initializer
objects. Their recovered interfaces traverse 52 action pointers, 29 state
pointers, and 31 terminated state tables, raising exact identified ownership
by 785 bytes. Both stock callers land at entries and no stored or direct
branch reaches an initializer interior.

The initiator tables are release-invariant. The responder's 27th action and
API-pair-request response-timeout/cleanup transitions independently select the
Apache-2.0 Packetcraft r20.05--r20.05c behavior over r19/AmbiqSuite 2.x. The
official R4.4.1 import is byte-identical later corroboration. Production
ownership remains zero; see
`docs/research/cordio-smp-legacy-state-machines-source-recovery.md`.

## Current Cordio non-SMP exclusion increment

The alternative three-function `smp_non.c` implementation is positively
configuration-excluded. The image has exactly two `L2cRegister` calls: ATT
owns CID 4 and linked `SmpHandlerInit` owns CID 6 with the already recovered
full-SMP data and control callbacks. There is no alternate CID-6 registration,
stored callback pointer, or non-SMP failure-response body.

This completes the source census for all 14 Packetcraft SMP translation units:
13 configured units are linked and mapped at function/table granularity, while
`smp_non.c` is the sole mutually exclusive source-only unit. Its r19 and r20/R4
definitions are identical; the selected optional public pin is Apache-2.0
Packetcraft r20.05c. Production ownership remains zero; see
`docs/research/cordio-smp-non-exclusion.md`.

## Current Ambiq Cordio HCI event-port increment

The proprietary Ambiq `hci_evt.c` boundary is now completely censused without
copying source. Stock links 79 of 80 definitions in
`[0x00569D4C,0x0056B7EC)`: 6,718 executable bytes plus 98 bytes of owned
alignment, literal, logger, and tail data. The only source-only definition is
`hciEvtGetStats`.

An 85-entry parser table roots 74 cells into 69 unique parser bodies; its
parallel 85-byte callback-size table, ten direct calls, retained path, and
absence of aligned strict-interior pointers close the remaining processors and
dispatchers. The exact 85-entry layout and retained diagnostic lines select
the later official AmbiqSuite R4.4.1 source family over R2.5.1's 67-entry
port. That later import is a proprietary reconstruction oracle, not a
historical producing-commit or reusable-source claim. Production ownership
remains zero; see `docs/research/cordio-hci-evt-source-recovery.md`.

## Current Ambiq Cordio HCI core increment

The adjacent proprietary `hci_core.c` boundary is also completely censused.
Stock links 22 of 24 definitions in `[0x0052A67C,0x0052AE38)`: 1,964 body
bytes plus a 16-byte literal pool. `hciCoreTxAclDataFragmented` and
`HciSetAclQueueWatermarks` are the only source-only definitions. Thirty-two
direct calls root every surviving entry; no aligned entry or strict-interior
pointer survives.

The 64-bit LE-feature API, three connection records, six CIS records, and
success-aware ACL transport select the later R4-era source family over
AmbiqSuite R2.5.1. Stock nevertheless omits both the later neuralSPOT send
delay and the still-later nsx priority/trace path, so no whole-file exact-text
claim is made. The file remains proprietary and contributes no production-
owned bytes. See `docs/research/cordio-hci-core-source-recovery.md`.

## Current Ambiq Cordio HCI platform-shim increment

The immediately following proprietary `hci_core_ps.c` object is now closed at
`[0x00530C00,0x00530D74)`. Nine linked definitions contribute 360 code bytes
and its literal pool contributes 12 bytes; eleven unused public getters are
source-only. Twenty-one direct calls root every linked entry, with no stored
entry or strict-interior pointer.

The handler's distinct ISO receive branch and the 64-bit LE-feature getter
independently exclude the 18-definition R2.5.1 source and select the
20-definition R4-era family. The later import remains a proprietary
reconstruction oracle, not a historical-commit pin or production source.
See `docs/research/cordio-hci-core-ps-source-recovery.md`.

## Current Ambiq Cordio HCI transport increment

The proprietary `hci_tr.c` transport object is now closed at
`[0x0053013C,0x00530364)`. Three linked definitions contribute 524 code bytes
and seven receive-state literals contribute 28 bytes; only
`hciTrReceivingPacket` is source-only. Four direct callers and six outbound
provider calls close the object without any stored entry or strict-interior
pointer.

The ACL sender returns the packet length or zero, the command sender returns
success, and neither frees or completes the transmit buffer. Those ownership
semantics plus the hardened receive length/type checks exclude AmbiqSuite
R2.5.1 and select the later R4-era source family. The later import remains a
proprietary behavioral oracle rather than a historical commit pin or
production source. See `docs/research/cordio-hci-tr-source-recovery.md`.

## Current Ambiq Cordio HCI command increment

The shared proprietary `hci_cmd.c` object is now completely censused at
`[0x0052AE38,0x0052B8A4)`. Fifty linked definitions contribute 2,654 code
bytes and one alignment/literal island contributes 14 bytes; the remaining
22 of the later 72-definition inventory are source-only. The linked command
surface includes legacy, data-length, privacy, vendor, and peer-SCA wrappers.

The analyzer pins every body hash, 156 direct ingress calls, all 127 direct
calls issued by the TU, the queue/timer control block at `0x20073A90`, and
the absence of legitimate stored entry or strict-interior pointers. Its one
interior-looking word is independently classified as packed non-code data.
The exact later AmbiqSuite R4.4.1 source inventory is a proprietary
reconstruction oracle, not a historical commit or reusable-source claim.
Production ownership remains zero; see
`docs/research/cordio-hci-cmd-source-recovery.md`.

## Current Ambiq Apollo3 HCI-driver increment

The controller-facing Apollo3 driver is now fully censused: 12 of 16 source
definitions link for 1,188 body bytes. Its main interval is
`[0x004B48A6,0x004B4D2C)`; `error_check` is separately retained at
`[0x004B47AE,0x004B47CC)`. Thirty direct ingress sites, all 66 outbound calls,
one intentional WSF handler pointer, and zero accepted strict-interior ingress
close the surviving surface. Four unused control APIs are source-only.

Stock is a mixed-version Ambiq implementation rather than an exact archived
file: the blocking transport and radio lifecycle follow the Apollo3 family,
the handler's null-message guard matches the later R3.1.1 import, and the VSC
tail uses later `0xFCC4`, `0xFC43`, and `0xFFF2` command semantics corroborated
by the R4.4.1 Cooper driver. The source carries an Ambiq BSD-style notice, but
the repository imports no implementation bytes and production ownership stays
zero. See `docs/research/cordio-hci-driver-source-recovery.md`.

The full vector-table follow-up corrects one earlier boundary assumption:
`HciDrvIntService` is retained but has no direct caller or stored/vector
pointer. Vector slot 75 is inside the OTA and instead reaches the Apollo510
`GPIO0_607F` handler below.

## Current product BLE-startup increment

The product startup boundary now closes twelve `app_ble.c` bodies plus one
interposed Apollo510 GPIO vector body, 3,236 code bytes in a 3,242-byte mixed
physical interval. The recovered prefix adds the exact DM/ATT/CCC forwarding
callbacks, delayed callback, product message state machine, and subsystem
initializer. The registered `_bleCommHandler`, handler/config initializer,
and stack-registration body close product dispatch, the runtime SMP config
pointer, connection client 3, and the six-entry CCC set.

`_bleExactleStackInit` initializes the 10,560-byte WSF pool, security, and the
HCI/DM/L2CAP/ATT/SMP/application/product/driver handler chain. The startup
wrapper performs radio shutdown, a 100-us delay, boot, stack/profile setup,
`DmDevReset`, and a 10-second delayed callback; the six-byte address getter
returns `0x200737BF`.

Nine direct entry calls, 267 outbound calls, seven stored pointers, and zero
strict-interior ingress are pinned. Ownership is intentionally discontinuous:
`[0x004B80BE,0x004B80EA)` is vector index 75 / external IRQ 59,
`GPIO0_607F_IRQn`, not product `app_ble.c` and not a BLE transport ISR. Two
unaligned interior-looking byte windows are rejected as packed data. The
R2.5.1 FIT radio task is only a semantic topology oracle; no exact product
source or historical commit is claimed. Four clean-room files now cover all
twelve product bodies / 3,192 stock code bytes and pass host plus freestanding
Thumb checks. The recovered `bleProcMsg` candidate includes its full event
switch, notification map, connection/CCC teardown, reconnect timers, security
forwarding, and delayed-start control path. The GPIO vector remains separately
owned. Production ownership remains zero while placement, logger bindings,
and redirects remain deferred.
See `docs/research/g2-app-ble-startup-recovery.md`.

## Current Ambiq HCI vendor reset-sequence increment

The adjoining vendor/reset object is closed at
`[0x00569B04,0x00569D4C)`: four linked functions contribute 546 code bytes
and a 38-byte alignment/literal tail; four trivial or bypassed hooks are
source-only. Five direct ingress calls and all 25 provider calls are pinned,
with no stored or branched strict-interior target.

The exact product chain is Reset plus custom BD-address update, followed on
completion by NVDS `0xFFF2`, RF power `0xFCC4` with parameter 6, standard
event masks and controller discovery, then four LE Random completions. This
order is a hybrid of the Apollo3 and later Cooper families and matches neither
official file wholesale. Production ownership remains zero. See
`docs/research/cordio-hci-vs-reset-sequence-recovery.md`.

## Current Cordio HCI PHY-command increment

The three-definition Apache `hci_cmd_phy.c` census is complete. Stock retains
only `HciLeSetPhyCmd` at `[0x00539E48,0x00539E94)`: 74 executable bytes plus
two alignment bytes. `HciLeReadPhyCmd` and `HciLeSetDefaultPhyCmd` are
source-only, matching the already closed DM PHY API census.

The sole `DmSetPhy` caller and exact `hciCmdAlloc(0x2032, 7)` / `hciCmdSend`
provider pair close the wrapper without stored or interior ingress. AmbiqSuite
R2.5.1 and Packetcraft r20.05c share exact definition bodies; the latter is
the safe public source route. Production ownership remains zero. See
`docs/research/cordio-hci-cmd-phy-source-recovery.md`.

## Current optional HCI command exclusion

The six modern command-only TUs `hci_cmd_ae/bis/cis/cte/iso/past.c` are now
excluded from stock with a complete 57-definition census. Every wrapper has
one mandatory `hciCmdAlloc` call; all 45 stock allocator callers are already
owned by the closed shared command object or `HciLeSetPhyCmd`. No unexplained
caller or retained source marker survives.

These findings classify the extended-advertising, broadcast/connected ISO,
CTE, ISO data-path/test, and PAST command surfaces as source-only while making
no claim about independently linked receive-event parsers. The files are
proprietary compatibility oracles and contribute no production bytes. See
`docs/research/cordio-hci-optional-command-exclusion.md`.

## Current Cordio ATT server-signing partial-inclusion increment

The retained `atts_sign.c` object is completely partitioned at
`[0x0052DA58,0x0052DBF0)`: four linked state/configuration functions contribute
370 code bytes, while 38 bytes hold alignment and owned trace/path/global
literals. The surviving three public APIs save or restore the peer CSRK,
CSRK-authentication flag, and sign counter through a 56-byte, three-record
control block at `0x2007335C`.

The signed-write CMAC worker, PDU processor, completion callback, and
`AttsSignInit` are dead-stripped. `AttsInit` leaves `signMsgCback` on
`attEmptyHandler`; the image has no later install, no signed-write CMAC call,
and none of the processing-only failure strings. This is a configuration-only
partial link, not active ATT signed-write verification.

Stock's 16-byte connection record and three-argument `AttsSetCsrk` match the
official later AmbiqSuite R4.4.1 authenticated-CSRK extension and exclude the
12-byte/two-argument Packetcraft r20 API. The later import is an Apache-2.0
reconstruction oracle, not a resolved historical producing commit. Production
ownership remains zero; see
`docs/research/cordio-atts-sign-source-recovery.md`.

## Current Cordio ATT indication/notification increment

The complete stock `atts_ind.c` object is now closed at
`[0x005338AC,0x00533EF4)`: thirteen linked functions contribute 1,552 code
bytes and three owned gaps contribute 56 category/literal bytes. The interface
table roots the control, message, and connection callbacks; the authenticated
IAR initializer independently populates method 15 with `attsProcValueCnf` in
the live SRAM ATT processor table. Twenty-two direct calls and three registered
entries land only at exact boundaries; the matching raw flash word is part of
the compressed initializer stream rather than a fourth runtime pointer cell.

Stock's nine 64-byte server CCBs, three-bearer loops, slot-aware timer/message
parameters, and client-change-awareness flow decisively select the Packetcraft
r20 EATT architecture over r19/AmbiqSuite 2.x. Packetcraft r20.05--r20.05c and
the later official AmbiqSuite R4.4.1 import share one exact Apache-2.0 source
blob. The two zero-copy public wrappers are the only source definitions
dead-stripped. Production ownership remains zero; see
`docs/research/cordio-atts-ind-source-recovery.md`.

## Current Cordio ATT server-owner/dispatcher increment

The complete stock `atts_main.c` object is now closed at
`[0x0053498C,0x00535488)`: seventeen linked functions contribute 2,710 code
bytes and six owned gaps contribute 102 category, alignment, and literal
bytes. All 21 source definitions are accounted; `AttsAuthorRegister`,
`AttsSetAttr`, `AttsGetAttr`, and `AttsErrorTest` have no standalone stock
body, caller, or stored entry. Forty-five direct calls and four callback-table
entries land only at exact boundaries.

The authenticated IAR scatter record reconstructs the complete 18-entry live
`attsProcFcnTbl` at `0x2000045C`; methods 1--12 and 16 route to linked request
processors, method 15 routes to `attsProcValueCnf`, and signed-write method 17
remains null. Stock also retains the later R4.4.1 ATT data-length hardening
absent from public r20.05c. The official later import is therefore the exact
behavioral oracle while Packetcraft r20.05c remains the public ancestry base.
Production ownership remains zero; see
`docs/research/cordio-atts-main-source-recovery.md`.

## Current Cordio common ATT server-processor increment

The complete stock `atts_proc.c` object is closed at
`[0x0056C550,0x0056CDC0)`: all nine source functions contribute 2,106 code
bytes and two owned gaps contribute 54 data bytes. Twenty-six direct calls
reach shared UUID, lookup, and permission helpers. Four additional live roots
enter the MTU, find-info, read, and read-multiple-variable processors through
methods 1, 2, 5, and 16 of the initialized SRAM dispatch table.

Packetcraft r20.05--r20.05c and the official later R4.4.1 import share one
exact Apache-2.0 blob. The EATT MTU gate and read-multiple-variable processor
exclude the smaller r19/AmbiqSuite 2.x source. No source definition is
dead-stripped and no strict-interior ingress survives. Production ownership
remains zero; see `docs/research/cordio-atts-proc-source-recovery.md`.

## Current Cordio ATT core increment

The complete stock `att_main.c` object is closed at
`[0x004B4DE0,0x004B5230)`: 21 linked definitions contribute 1,030 code
bytes and five owned gaps contribute 74 data/alignment bytes. Sixty-five
direct BL sites and 14 registered pointers reach exact entries; no decoded
branch reaches a strict interior. `attCcbByHandle` and public `AttMsgAlloc`
are the only two source-only APIs.

`AttHandlerInit` pins `attCb=0x200610AC`, the three-connection/three-bearer
layout, and exact legacy and enhanced default interfaces at `0x007851E0`
and `0x007851F0`. Message routing uses thresholds `0x20/0x40/0x60/0x80`,
excluding the r19 single-bearer source. Packetcraft r20.05c and the later
official R4.4.1 import have identical implementation text. Production
ownership remains zero; see `docs/research/cordio-att-main-source-recovery.md`.

## Current Cordio enhanced ATT server exclusion

The optional `atts_eatt.c` TU is absent: all twelve source definitions are
source-only/dead-stripped. The exact no-op EATT server interface installed at
`attCb+0x44` is never replaced, `attCcbByConnId` and the common handle-value
worker have no enhanced callers, and the separately closed L2CAP CoC census
has zero linked functions. This is a positive initialization/provider closure,
not a conclusion from missing names alone. See
`docs/research/cordio-atts-eatt-exclusion.md`.

## Current Cordio dynamic ATT service exclusion

The optional `atts_dyn.c` TU is absent: all seven definitions are
source-only/dead-stripped and its 1,280-byte private heap is not instantiated.
The exact `AttsAddGroup` and `AttsRemoveGroup` caller closures contain only
the linked static service/CSF paths, with no dynamic provider. Together with
the EATT exclusion, every ATT server TU in the selected source family is now
accounted. See `docs/research/cordio-atts-dyn-exclusion.md`.

## Current Cordio enhanced ATT core/client exclusion

The optional `att_eatt.c` and `attc_eatt.c` TUs are absent: all 26 core and
all 20 client definitions are source-only/dead-stripped. `EattInit` never
installs the handler, DM callback, or CoC transmit function at
`attCb+0x4C/+0x50/+0x54`; `EattcInit` never replaces the enhanced-client
default at `attCb+0x48`. The independently closed L2CAP CoC TU has zero linked
functions, and the exact ATT allocator/ATTC CCB provider sets contain no EATT
client callers. Together with the existing enhanced-server exclusion, no
enhanced bearer implementation survives despite the common r20/R4
multi-bearer ABI. See `docs/research/cordio-att-eatt-exclusion.md` and
`docs/research/cordio-attc-eatt-exclusion.md`.

## Current Cordio ATT UUID constant-object increment

The final unaccounted ATT-family TU, data-only `att_uuid.c`, is now completely
censused. Stock retains 11 of 152 two-byte UUID objects in the exact
source-ordered block `[0x0078F53A,0x0078F550)`, 22 bytes, while the other 141
objects are source-only/dead-stripped. A whole-image unaligned scan closes all
54 stored references to those 11 entries; every reference cell is naturally
four-byte aligned and no accidental window is accepted.

Packetcraft r20.05c and the later official R4.4.1 import share one exact
Apache-2.0 source blob. The legacy r19 source already contains every retained
object, so this TU is not independently release-discriminating even though
the surrounding ATT architecture proves r20/R4. Numeric UUID duplicates in
application service tables are explicitly excluded from TU ownership.
Production ownership remains zero; see
`docs/research/cordio-att-uuid-source-recovery.md`.

## Current Cordio optional ATT server-read increment

The complete stock `atts_read.c` object is closed at
`[0x0056D93C,0x0056E4F8)`: all seven source definitions contribute 2,984
code bytes and the owned UUID/global tail contributes 20 bytes. Nine direct
calls reach its two range helpers; methods 3, 4, 6, 7, and 8 of the decoded
live SRAM processor table root the five request processors. Fifty decoded
direct calls leave the TU, with three raw BL-like wide-instruction overlaps
explicitly excluded.

Stock retains the r20 CSF database-hash path and uses the subtraction-safe
fit-check topology found in the later official AmbiqSuite R4.4.1 source fix
for IAR high optimization. R4 is the closest behavioral oracle; its later
import is not claimed as the historical producer. No source definition is
dead-stripped and no accepted strict-interior ingress survives. Production
ownership remains zero; see
`docs/research/cordio-atts-read-source-recovery.md`.

## Current Cordio ATT server-write increment

The complete stock `atts_write.c` object is closed at
`[0x005A5D94,0x005A6260)`: four linked definitions contribute 1,220 code
bytes and the owned `attsCb`/configuration tail contributes eight bytes.
Methods 9 and 10 share the write processor; methods 11 and 12 root prepare
and execute write. The authenticated live table closes all four cells.

One source API, `AttsContinueWriteReq`, is dead-stripped. Stock can record an
`ATT_RSP_PENDING` callback result, but this product does not link the public
continuation entry. Twenty-eight decoded outbound calls, one internal helper
call, and the initializer-stream entry are closed without accepted interior
ingress. Packetcraft r20.05--r20.05c and the later R4.4.1 import share one
exact Apache-2.0 source blob. Production ownership remains zero; see
`docs/research/cordio-atts-write-source-recovery.md`.

## Current G2 BLE WSF-thread increment

The product `platform\threads\thread_ble_wsf.c` TU is now completely bounded
at `[0x004D0A4C,0x004D0D24)`: twelve linked functions contribute 656 code
bytes and the owned literal pool contributes 72 bytes. The aligned stored task
entry, 27 direct BL sites, 50 outbound calls, static CMSIS task attributes,
and every retained diagnostic are pinned; no accepted strict-interior ingress
survives.

The `ble_wsf` task uses a 16-KiB static stack and 112-byte CMSIS control block,
starts the already-closed product BLE wrapper, then runs `WsfOsDispatcher`
forever. A max-one, initially available semaphore implements transmit-ready
flow control with a twenty-iteration/400-ms diagnostic bound and duplicate
completion suppression.

The exact product source and historical generating commit remain unresolved.
CMSIS-FreeRTOS v10.5.1 authenticates provider ABIs and AmbiqSuite R2.5.1
supplies only a related WSF topology oracle. A three-file clean-room candidate
now covers all twelve entries, passes host behavioral tests, and compiles for
a freestanding Thumb target. Production integration remains zero while
placement, redirects, and retained logger bindings are deferred. See
`docs/research/g2-thread-ble-wsf-recovery.md`.

## Current G2 BLE message-thread increment

Both product BLE message-thread units are now completely bounded. The TX unit
`[0x00475290,0x00475FC0)` contains 21 bodies / 3,096 code bytes and 280 owned
data bytes; its existing clean-room replacement now has whole-object and
ingress closure. The RX unit `[0x0048EDB0,0x0048F3A4)` contains 13 bodies /
1,390 code bytes and 134 owned data bytes, ending exactly where nanopb begins.

Static task attributes, 150-entry queues, lifecycle state, queue/exit flags,
TX command types, eleven RX message classes, 163 direct entry sites, 283
outbound calls, and four genuine stored entries are pinned. All raw
strict-interior and unaligned lookalikes are rejected, including the sole RX
BL-like halfword overlap. TX ownership is unchanged. An independently
authored five-file RX candidate now covers all 13 entries and passes host and
freestanding Thumb compilation tests, but diagnostic parity and placement-
sensitive production routing remain pending; stock RX code still executes.
See
`docs/research/g2-thread-ble-message-recovery.md`.

## Current G2 NVDB buzzer increment

The complete first-party `service_nvdb_buzzer.c` object is now bounded at
`[0x0058F9D4,0x0058FAAC)`: five functions contribute 188 code bytes and its
owned literal tail contributes 28 bytes. Two stored initialization roots, five
direct entry calls, eleven outbound/internal calls, and zero accepted
strict-interior ingress close the object.

The twelve-byte `nvBuzzer` record is version 2 with boot defaults 4,000 Hz and
30% duty. Its default initializer computes CCITT-FALSE `0x9B1E` across the
first ten bytes. The exact missing/pre-v2 migration policy and its unusual
CRC-field comparison are now host-tested by a clean-room five-function
candidate that also compiles for freestanding Thumb. Production routing and
ownership remain zero pending placement, diagnostics, and guarded redirects.
See `docs/research/g2-nvdb-buzzer-recovery.md`.

## Current G2 NVDB product-mode increment

The adjacent `service_nvdb_product_mode.c` object is now closed at
`[0x004ABD90,0x004ABEC8)`: six functions / 270 code bytes and 42 owned data
bytes. Two stored roots, 54 direct entry calls, 18 provider/internal calls, and
zero strict-interior ingress are pinned. The four-byte version/mode/CRC record,
`0x2E3E` default checksum, migration policy, RAM-only setter, persistent
updater, and unvalidated read/import behavior all pass host and Thumb tests.
Production routing and ownership remain zero. See
`docs/research/g2-nvdb-product-mode-recovery.md`.

## Current G2 NVDB MAC increment

The retained `service_nvdb_mac.c` object is now closed at
`[0x005D9F48,0x005DA080)`: three functions contribute 280 code bytes and the
owned literal tail contributes 32 bytes. Two stored initialization roots, two
direct updater calls, eighteen provider/internal calls, and zero accepted
strict-interior ingress close the object.

The ten-byte `nvMAC` record is version 1. Its six-byte BLE static-random
address is device-dependent: the default builder processes little-endian
`CHIPID1 || CHIPID0`, uses reflected CRC-32 for the first four address bytes,
CCITT-FALSE for the last two, applies `(last & 0xFC) | 0xC0`, and checksums the
first eight record bytes. The exact missing/v0 migration policy is host-tested
by a clean-room three-function candidate that also compiles for freestanding
Thumb. Production routing and ownership remain zero pending placement,
diagnostics, provider binding, and guarded redirects. See
`docs/research/g2-nvdb-mac-recovery.md`.

## Current G2 NVDB advertising-magic increment

The anonymous three-function NVDB object immediately preceding the MAC helper
is now closed at `[0x005D9ED0,0x005D9F48)`: 110 code bytes and a ten-byte
alignment/literal tail. Two stored roots, two internal updater calls, six total
body calls, and zero accepted strict-interior ingress account for the complete
object.

Its four-byte `nvAdvMagic` record at `0x200038D4` is version 1 with default
magic `0x20`; initialization computes CCITT-FALSE `0x0A5C` over its first two
bytes. A clean-room three-function candidate preserves its missing/v0 rewrite
policy and unusual CRC-field comparison, passes host and Thumb tests, and
remains outside production routing. Because stock retains no path or function
name for this TU, attribution is limited to the exact key/record/table-root
closure. See `docs/research/g2-nvdb-adv-magic-recovery.md`.

## Current G2 NVDB sensor-calibration increment

The retained `service_nvdb_sensor_caldata.c` object is now completely bounded
at `[0x00509764,0x00509B48)`: eight functions contribute 900 code bytes and
96 alignment/literal bytes. Four stored initialization roots, ten direct entry
calls, fifty provider/internal calls, and no accepted strict-interior ingress
close the object.

The 92-byte `nvSCald` and 68-byte `nvSCaldAG` ABIs are pinned, including both
factory payloads, CRC offsets and initialized values (`0xD886` and `0x82FC`).
The primary non-importing v0 migration quirk, partial AG updates, direct AG
read/import path, and narrow matrix fallback pattern are host-tested by an
eight-function clean-room candidate that also compiles for freestanding Thumb.
Production routing and ownership remain zero. See
`docs/research/g2-nvdb-sensor-caldata-recovery.md`.

## Current G2 NVDB system-data increment

The retained `service_nvdb_sys_dt.c` object is now completely bounded at
`[0x004AEE28,0x004B03E0)`: thirteen functions contribute 5,084 code bytes and
seven split alignment/literal regions contribute 476 bytes. Two stored
initialization roots, 37 direct entry calls, 299 provider/internal calls, and
no accepted strict-interior ingress close the object.

The 172-byte `nvSysDt` record, exact initialized SRAM bytes, first-38-byte CRC
(`0x1DC7` after default initialization), thirteen indexed fields, 40-entry
legacy PSN table, parser, aging reset, and eight-slot OTP PSN journal are
pinned. Migration is correctly modeled as a non-importing audit: it runs the
legacy PSN scan, prefers the newest valid OTP PSN, and rewrites only missing or
pre-v2 CRC-mismatched data; it does not reset aging. A thirteen-function
clean-room candidate passes host and freestanding Thumb tests. Production
routing and ownership remain zero. See
`docs/research/g2-nvdb-sys-dt-recovery.md`.

## Current G2 KVDB temperature-unit increment

The retained `service_kvdb_temperature_unit.c` object is now completely
bounded at `[0x0049B014,0x0049B198)`: three functions contribute 338 code
bytes and the owned tail contributes 50 bytes. Two stored callback roots,
three direct entry calls, 21 provider/internal calls, and zero strict-interior
ingress close the object.

The twelve-byte `kvTemperatureUnit` factory record, version/CRC layout, default
checksum `0x76ED`, whole-record writer, and non-importing v0 migration policy
are pinned and host-tested. The candidate also compiles as exactly three
freestanding Thumb symbols. Production routing and ownership remain zero. See
`docs/research/g2-kvdb-temperature-unit-recovery.md`.

## Current G2 KVDB time-format increment

The immediately adjacent retained `service_kvdb_time_format.c` object is now
completely bounded at `[0x0049AE90,0x0049B014)`: three functions contribute
338 code bytes and the owned tail contributes 50 bytes. Two stored callback
roots, three direct entry calls, 21 provider/internal calls, and zero
strict-interior ingress close the object.

The twelve-byte `kvTimeFormat` factory record at `0x20003818`, version/CRC
layout, default checksum `0x76ED`, whole-record writer, and non-importing v0
migration policy are pinned and host-tested. The candidate also compiles as
exactly three freestanding Thumb symbols. Production routing and ownership
remain zero. See `docs/research/g2-kvdb-time-format-recovery.md`.

## Current G2 KVDB universal-setting increment

The retained `service_kvdb_universal_setting.c` object is completely bounded
at `[0x0049AD0C,0x0049AE90)`: three functions contribute 340 code bytes and
the owned tail contributes 48 bytes. Two stored roots, three direct entry
calls, 22 provider/internal calls, and zero strict-interior ingress close it.

The twenty-byte `kvUniversalSetting` record at `0x20003824` has version 3,
CRC at offset 18, initialized checksum `0xA967`, a whole-record writer, and a
non-importing pre-v3 migration policy. The host-tested candidate also compiles
as exactly three freestanding Thumb symbols. Production routing and ownership
remain zero. See `docs/research/g2-kvdb-universal-setting-recovery.md`.

## Current G2 primary KVDB setting increment

The retained `service_kvdb_setting.c` object is completely bounded at
`[0x004AEB20,0x004AECA4)`: three functions contribute 340 code bytes and the
owned tail contributes 48 bytes. Two stored roots, three direct entry calls,
22 provider/internal calls, and zero strict-interior ingress close it.

The 28-byte `kvSetting` record at `0x200037E0` has CRC at offset 24. Its
factory image is version 1 with initialized CRC `0xA288`; persistence upgrades
it to version 4 and CRC `0x4987`. The writer and non-importing pre-v4 migration
policy are host-tested, and the candidate compiles as exactly three Thumb
symbols. Production routing and ownership remain zero. See
`docs/research/g2-kvdb-setting-recovery.md`.

## Current G2 KVDB ALS-scale increment

The immediately adjacent retained `service_kvdb_als_scale.c` object is
completely bounded at `[0x004AECA4,0x004AEE28)`: three functions contribute
338 code bytes and the owned tail contributes 50 bytes. Two stored roots,
three direct entry calls, 21 provider/internal calls, and zero strict-interior
ingress close it.

The twelve-byte `kvAlsScale` record at `0x200037BC` has version 1 and CRC at
offset 8. Default initialization produces checksum `0xAA2D`; the writer copies
the whole record, forces version 1, and preserves the two CRC-excluded trailing
bytes. The non-importing v0 migration policy is host-tested, and the candidate
compiles as exactly three Thumb symbols. Production routing and ownership
remain zero. See `docs/research/g2-kvdb-als-scale-recovery.md`.

## Current G2 KVDB ALS-scale production routing

The ALS-scale candidate above is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 90-byte migration callback, 96-byte whole-record writer, with an
11-byte key-string read-only closure on each referencing leaf) plus three
`B.W` entry redirects replace the 338 stock body bytes
`[0x004AECA4,0x004AEDF6)`. Providers bind exactly to the retained CRC-16 at
`0x0049ACD4` and the blob read/write adapters at `0x004D956C`/`0x004D957E`;
the 50-byte literal tail and the fixed SRAM record at `0x200037BC` are
untouched, and both stored roots plus all three direct entry calls reach the
leaves through the redirects. Apple Clang 21 overlay/component/package pins
are `143227/3666623/4445117` (SHA-256 `200b0b33…`, `ad895f78…`, `62569df0…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins await
Linux toolchain regeneration. Ownership: 338 replaced stock body bytes. See
`docs/research/g2-kvdb-als-scale-recovery.md`.

## Current G2 NVDB sensor-calibration production routing

The sensor-calibration candidate is now production-routed under the reviewed
apple-clang profile: eight relocated overlay leaves (30-byte primary and AG
default initializers, 530-byte primary whole-record updater, 88-byte migration
callback, 4-byte AG migration callback compiled byte-identically to its stock
body, 370-byte AG selective updater, 284-byte suspicious-matrix checker
carrying the 36-byte default-matrix read-only closure, and 358-byte AG
reader) plus eight `B.W` entry redirects replace the 900 stock body bytes
across `[0x00509764,0x00509A3E)` and `[0x00509A40,0x00509AEA)`. Providers bind
exactly to the retained CRC-16 at `0x0049ACD4`, the NVDB blob read/write
adapters at `0x005105F0`/`0x00510602`, and the product predicate at
`0x0045A568`; the 96-byte alignment/literal island and the fixed SRAM records
at `0x200038F4`/`0x20003950` are untouched, and all four stored roots plus
all ten direct entry calls reach the leaves through the redirects. Apple
Clang 21 overlay/component/package pins are `144966/3668362/4446856` (SHA-256
`bf19ebb7…`, `7a4a3252…`, `e709d945…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 900 replaced stock body bytes. See
`docs/research/g2-nvdb-sensor-caldata-recovery.md`.

## Current G2 KVDB setting production routing

The primary setting candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 160-byte whole-record writer, and 64-byte migration callback,
with a 10-byte key-string read-only closure on each of the two referencing
leaves) plus three `B.W` entry redirects replace the 340 stock body bytes
`[0x004AEB20,0x004AEC74)`. Providers bind exactly to the retained CRC-16 at
`0x0049ACD4` and the blob read/write adapters at `0x004D956C`/`0x004D957E`;
the 48-byte literal tail and the fixed SRAM record at `0x200037E0` are
untouched, and both stored roots plus all three direct entry calls reach the
leaves through the redirects. Apple Clang 21 overlay/component/package pins
are `145242/3668638/4447132` (SHA-256 `8f891d52…`, `15ce61e3…`, `203ecd4c…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins await
Linux toolchain regeneration. Ownership: 340 replaced stock body bytes. See
`docs/research/g2-kvdb-setting-recovery.md`.

## Current G2 KVDB time production routing

The time candidate is now production-routed under the reviewed apple-clang
profile: three relocated overlay leaves (28-byte default initializer,
54-byte timestamp/timezone writer, and 100-byte migration callback, with a
7-byte `kvTime` key-string read-only closure on each of the two referencing
leaves and the writer body inlined into the migration callback by the
reviewed toolchain) plus three `B.W` entry redirects replace the 494 stock
body bytes `[0x00585618,0x00585806)`. Providers bind exactly to the retained
CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 58-byte literal tail and the fixed SRAM
record at `0x2000380C` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `145443/3668839/4447333` (SHA-256
`9e790387…`, `ecfbc642…`, `e0f3dc6b…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 494 replaced stock body bytes. See
`docs/research/g2-kvdb-time-recovery.md`.

## Current G2 KVDB time-format production routing

The time-format candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 96-byte whole-record writer, and 90-byte migration callback,
with a 13-byte `kvTimeFormat` key-string read-only closure on each of the
two referencing leaves and the writer body inlined into the migration
callback by the reviewed toolchain) plus three `B.W` entry redirects replace
the 338 stock body bytes `[0x0049AE90,0x0049AFE2)`. Providers bind exactly
to the retained CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 50-byte literal tail and the fixed SRAM
record at `0x20003818` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `145687/3669083/4447577` (SHA-256
`332daed3…`, `f345bff7…`, `432e69e1…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 338 replaced stock body bytes. See
`docs/research/g2-kvdb-time-format-recovery.md`.

## Current G2 KVDB temperature-unit production routing

The temperature-unit candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 96-byte whole-record writer, and 90-byte migration callback,
with an 18-byte `kvTemperatureUnit` key-string read-only closure on each of
the two referencing leaves and the writer body inlined into the migration
callback by the reviewed toolchain) plus three `B.W` entry redirects replace
the 338 stock body bytes `[0x0049B014,0x0049B166)`. Providers bind exactly
to the retained CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 50-byte literal tail and the fixed SRAM
record at `0x200037FC` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `145940/3669336/4447830` (SHA-256
`50e4865c…`, `72f6225b…`, `7b3301d8…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 338 replaced stock body bytes. See
`docs/research/g2-kvdb-temperature-unit-recovery.md`.

## Current G2 KVDB universal-setting production routing

The universal-setting candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 128-byte whole-record writer, and 92-byte migration callback,
with a 19-byte `kvUniversalSetting` key-string read-only closure on each of
the two referencing leaves and the writer body inlined into the migration
callback by the reviewed toolchain) plus three `B.W` entry redirects replace
the 340 stock body bytes `[0x0049AD0C,0x0049AE60)`. Providers bind exactly
to the retained CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 48-byte literal tail and the fixed SRAM
record at `0x20003824` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `146227/3669623/4448117` (SHA-256
`1701d7eb…`, `2042c3ea…`, `a65f3794…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 340 replaced stock body bytes. See
`docs/research/g2-kvdb-universal-setting-recovery.md`.

## Current G2 KVDB terminal-mode increment

The retained `service_kvdb_terminal_mode.c` object is completely bounded at
`[0x004B03E0,0x004B0560)`: three functions contribute 334 code bytes and the
owned tail contributes 50 bytes. Two stored roots, three direct entry calls,
21 provider/internal calls, and zero strict-interior ingress close it.

The four-byte `kvTerminalMode` record at `0x20003808` has version at byte zero,
mode at byte one, and CRC at offset two. Its external setter independently
confirms the mode field; default initialization produces checksum `0x2E3E`.
The whole-record writer and non-importing v0 migration policy are host-tested,
and the candidate compiles as exactly three Thumb symbols. Production routing
and ownership remain zero. See
`docs/research/g2-kvdb-terminal-mode-recovery.md`.

## Current G2 KVDB terminal-mode production routing

The terminal-mode candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 52-byte whole-record writer, and 94-byte migration callback,
with a 15-byte `kvTerminalMode` key-string read-only closure on each of
the two referencing leaves and the writer body inlined into the migration
callback by the reviewed toolchain) plus three `B.W` entry redirects replace
the 334 stock body bytes `[0x004B03E0,0x004B052E)`. Providers bind exactly
to the retained CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 50-byte literal tail and the fixed SRAM
record at `0x20003808` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `146433/3669829/4448323` (SHA-256
`bb69a3a6…`, `ab37d9c8…`, `6f226b26…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 334 replaced stock body bytes. See
`docs/research/g2-kvdb-terminal-mode-recovery.md`.

## Current G2 KVDB onboarding-config production routing

The onboarding-config candidate is now production-routed under the reviewed
apple-clang profile: six relocated overlay leaves (32-byte indexed live-byte
setter, 22-byte live-byte writer, 42-byte update-and-persist wrapper, 10-byte
scalar getter, 8-byte pointer getter, and 30-byte live-record loader, with a
19-byte `kvOnboardingConfig` key-string read-only closure on each of the
three referencing leaves and the setter, writer, and pointer-getter bodies
inlined into the composing leaves by the reviewed toolchain) plus six `B.W`
entry redirects replace the 286 stock body bytes `[0x004A777C,0x004A789A)`.
Providers bind exactly to the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 54-byte literal tail and the fixed one-byte
SRAM record at `0x20000040` are untouched, and all eighteen direct entry
calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `146645/3670041/4448535` (SHA-256
`4df8082f…`, `f464eb05…`, `4689b480…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 286 replaced stock body bytes. See
`docs/research/g2-kvdb-onboarding-config-recovery.md`.

## Current G2 KVDB ring production routing

The ring candidate is now production-routed under the reviewed apple-clang
profile: three relocated overlay leaves (28-byte default initializer,
262-byte whole-record writer, and 66-byte migration callback, with a 7-byte
`kvRing` key-string read-only closure on each of the two referencing leaves
and the writer called by the migration callback as a source-owned leaf) plus
three `B.W` entry redirects replace the 796 stock body bytes
`[0x005D9B6C,0x005D9E88)`. Providers bind exactly to the retained CRC-16 at
`0x0049ACD4` and the blob read/write adapters at `0x004D956C`/`0x004D957E`;
the 72-byte literal tail and the fixed 24-byte SRAM record at `0x200037C8`
are untouched, and both stored roots plus both direct entry calls reach the
leaves through the redirects. Apple Clang 21 overlay/component/package pins
are `147021/3670417/4448911` (SHA-256 `02c48ddc…`, `eee145e7…`, `21ba9d6c…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins await
Linux toolchain regeneration. Ownership: 796 replaced stock body bytes. See
`docs/research/g2-kvdb-ring-recovery.md`.

## Current G2 AT^NUS handler production routing

The pathless `AT^NUS` command handler is authored clean-room from the
recovered behavioral specification and production-routed under the reviewed
apple-clang profile: one relocated overlay leaf (the 18-byte
`open_cfw_at_nus_handler`) plus one `B.W` entry redirect with NOP fill
replace the complete sixteen-byte stock object `[0x005A5520,0x005A5530)`
(twelve body bytes plus the four-byte literal pool). The leaf passes the
retained `NUS+OK\r\n` response string at `0x0078A370` to the retained output
provider at `0x00541430` and returns one without reading its arguments; the
stored registration pointer `0x005A5521` at `0x006C92A8` — the only ingress —
reaches the leaf through the redirect. Apple Clang 21
overlay/component/package pins are `147042/3670438/4448932` (SHA-256
`b1a5bcd7…`, `76bc4a35…`, `a842e5e3…`). The leaf and redirect are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 16 replaced stock object bytes. See
`docs/research/g2-at-nus-recovery.md`.

## Current G2 eAT core/sensor cluster production routing

The pathless eAT core/sensor command cluster is authored clean-room from the
recovered behavioral specification and production-routed under the reviewed
apple-clang profile: twelve relocated overlay leaves (650 bytes plus sixteen
alignment bytes) plus twelve `B.W` entry redirects with NOP fill replace the
486 stock body bytes across `[0x005A5720,0x005A595E)`. The four owned
alignment/literal islands (126 bytes) stay retained stock, and the twelve
stored registration pointers in the 192-byte command table
`[0x006C92E0,0x006C93A0)` — the only ingress — reach the leaves through the
redirects. Recovered stock quirks are reproduced exactly (`SCRN_Y` accepts
zero through 192, the PSN error reports the required length, `ALS`
acknowledges unhandled values, `BRIGHTNESS` forwards unvalidated). Apple
Clang 21 overlay/component/package pins are `147708/3671104/4449598`
(SHA-256 `bcf40980…`, `d1793fce…`, `f3655acb…`). The leaves and redirects
are gated `apple-clang`; linux-clang leaf pins await Linux toolchain
regeneration. Ownership: 486 replaced stock body bytes. See
`docs/research/g2-eat-core-sensor-recovery.md`.

## Current G2 KVDB module-configuration production routing

The retained `service_kvdb_module_configure.c` closure is production-routed
under the reviewed apple-clang profile: six relocated overlay leaves (2,428
text bytes plus six 64-byte key-string read-only closures and one two-byte
alignment pad) plus six `B.W` entry redirects with NOP fill replace the
2,286 stock body bytes across `[0x004922F8,0x00492BE6)`. Provider binding is
exact: the retained blob read/write adapters at `0x004D956C`/`0x004D957E`,
the retained dashboard mode provider at `0x0045A570` (mode two skips the
database), the retained built-in menu item lookup at `0x00460450`, and the
retained snapshot synchronization providers at `0x0046018E`/`0x004601EA`.
The 206-byte alignment/literal tail stays retained stock, the SRAM scalars,
menu record, runtime array, and external-menu globals are untouched, and the
three stored reader roots at `0x00746D24...0x00746D2C` plus the three direct
writer entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `150522/3673918/4452412` (SHA-256
`f32aa018…`, `32413c15…`, `ab0f0b0a…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 2,286 replaced stock body bytes. See
`docs/research/g2-kvdb-module-configure-recovery.md`.

## Current G2 NVDB buzzer production routing

The retained `service_nvdb_buzzer.c` closure is production-routed under the
reviewed apple-clang profile: five relocated overlay leaves (168 text bytes
plus one two-byte alignment pad) plus five `B.W` entry redirects with NOP
fill replace the 188 stock body bytes across `[0x0058F9D4,0x0058FA90)`.
Provider binding is exact: the retained CRC-16 provider at `0x0049ACD4` and
the retained NVDB blob read/write adapters at `0x005105F0`/`0x00510602`;
the retained diagnostic hook stays the candidate's deliberate no-op. The
28-byte literal tail stays retained stock, the twelve-byte SRAM record at
`0x200038D8`, the `nvBuzzer` key, and the v2 4,000 Hz / 30% boot defaults
are untouched, and the two stored entry roots at
`0x006D1E84`/`0x0078F518` plus the five direct entry calls reach the
leaves through the redirects. Apple Clang 21 overlay/component/package pins
are `150692/3674088/4452582` (SHA-256 `58920545…`, `0b88c150…`,
`5d1efae3…`). The leaves and redirects are gated `apple-clang`; linux-clang
leaf pins await Linux toolchain regeneration. Ownership: 188 replaced stock
body bytes. See `docs/research/g2-nvdb-buzzer-recovery.md`.

## Current G2 NVDB product-mode production routing

The retained `service_nvdb_product_mode.c` closure is production-routed
under the reviewed apple-clang profile: six relocated overlay leaves (196
text bytes plus one two-byte alignment pad) plus six `B.W` entry redirects
with NOP fill replace the 270 stock body bytes across
`[0x004ABD90,0x004ABE9E)`. Provider binding is exact: the retained CRC-16
provider at `0x0049ACD4` and the retained NVDB blob read/write adapters at
`0x005105F0`/`0x00510602`; the retained diagnostic hook stays the
candidate's deliberate no-op. The 42-byte alignment and literal island
stays retained stock, the four-byte SRAM record at `0x200038F0`, the
`nvProdMode` key, and the version-0 boot defaults are untouched, and the
two stored entry roots at `0x006D1E94`/`0x0078F520` plus the 54 direct
entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `150890/3674286/4452780` (SHA-256
`21b94e54…`, `2ad978b4…`, `41064778…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 270 replaced stock body bytes. See
`docs/research/g2-nvdb-product-mode-recovery.md`.

## Current G2 NVDB MAC production routing

The retained `service_nvdb_mac.c` closure is production-routed under the
reviewed apple-clang profile: three relocated overlay leaves (252 text
bytes plus one two-byte alignment pad) plus three `B.W` entry redirects
with NOP fill replace the 280 stock body bytes across
`[0x005D9F48,0x005DA060)`. Provider binding is exact: the source-owned
MCUCTRL information provider at `0x00480D72` (the candidate's two-word
device-identifier seam is adapted onto its selector-one 64-byte
device-record ABI by the leaf's pinned `-DOPEN_CFW_NVDB_MAC_DEVICE_IDS_GET`
binding), the retained CRC-32 provider at `0x004D34C4`, the retained CRC-16
provider at `0x0049ACD4`, and the retained NVDB blob read/write adapters at
`0x005105F0`/`0x00510602`; the retained diagnostic hook stays the
candidate's deliberate no-op. The 32-byte literal tail stays retained
stock, the ten-byte SRAM record at `0x200038E4`, the `nvMAC` key, and the
version-1 boot defaults are untouched, and the two stored entry roots at
`0x006D1E8C`/`0x0078F51C` plus the two direct entry calls reach the leaves
through the redirects. Apple Clang 21 overlay/component/package pins are
`151144/3674540/4453034` (SHA-256 `33a5109d…`, `be32048d…`, `bec30ccb…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins
await Linux toolchain regeneration. Ownership: 280 replaced stock body
bytes. See `docs/research/g2-nvdb-mac-recovery.md`.

## Current G2 NVDB advertising-magic production routing

The retained advertising-magic NVDB closure immediately preceding
`service_nvdb_mac.c` is production-routed under the reviewed apple-clang
profile: three relocated overlay leaves (140 text bytes plus one two-byte
alignment pad before the migration callback) plus three `B.W` entry
redirects with NOP fill replace the 110 stock body bytes across
`[0x005D9ED0,0x005D9F3E)`. Provider binding is exact: the retained CRC-16
provider at `0x0049ACD4` and the retained NVDB blob read/write adapters at
`0x005105F0`/`0x00510602`. The ten-byte alignment and literal tail stays
retained stock, the four-byte SRAM record at `0x200038D4`, the
`nvAdvMagic` key, and the boot defaults are untouched, and the two stored
entry roots at `0x006D1E7C`/`0x0078F514` reach the leaves through the
redirects. Apple Clang 21 overlay/component/package pins are
`151286/3674682/4453176` (SHA-256 `d3087982…`, `8aac36ba…`, `5fd04249…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins
await Linux toolchain regeneration. Ownership: 110 replaced stock body
bytes. See `docs/research/g2-nvdb-adv-magic-recovery.md`.

## Current G2 NVDB system-data production routing

The retained `service_nvdb_sys_dt.c` closure is production-routed under the
reviewed apple-clang profile: thirteen relocated overlay leaves (4,338 text
bytes plus two 23-byte read-only string closures and twelve alignment pad
bytes) plus thirteen `B.W` entry redirects with NOP fill replace the 5,084
stock body bytes across `[0x004AEE28,0x004B03E0)`. Provider binding is
exact: the retained CRC-16 provider at `0x0049ACD4`, the retained NVDB blob
read/write adapters at `0x005105F0`/`0x00510602`, the source-owned
peripheral-power enable/disable entries at `0x0047F5B8`/`0x0047F7AE` and
CMSIS delay at `0x00449376` (through the pinned
`-DOPEN_CFW_NVDB_SYS_DT_OTP_BEGIN`/`_END` gate sequences), the retained OTP
INFOC word accessors at `0x0051381A`/`0x00513850`, and the retained
40-entry legacy-PSN table at `0x006D3358` (through the pinned
`-DOPEN_CFW_NVDB_SYS_DT_LEGACY_PSNS` seam); the fourteen-field parse
diagnostic sink is compiled out by the pinned
`-DOPEN_CFW_NVDB_SYS_DT_PARSED` no-op binding. The 476 split
alignment/literal bytes stay retained stock, the 172-byte SRAM record at
`0x20003994`, the `nvSysDt` key, and the factory defaults are untouched,
and the two stored entry roots at `0x006D1EAC`/`0x0078F52C` plus the 37
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `155682/3679078/4457572` (SHA-256
`3bb04fb7…`, `5160689a…`, `f66065fe…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 5,084 replaced stock body bytes. See
`docs/research/g2-nvdb-sys-dt-recovery.md`.

## Current G2 ULED display-preprocess production routing

The retained `driver/uled/display_preprocess.c` closure is production-routed
under the reviewed apple-clang profile: one relocated closure leaf (242 text
bytes plus the 28-byte GPU descriptor-template read-only closure and four
alignment pad bytes) plus one `B.W` entry redirect with NOP fill replace the
584 stock body bytes at `[0x0046C73C,0x0046C984)`. Provider binding is exact:
the retained GPU start provider at `0x004B092A`, the retained
destination-channel configure/mode/enable providers at
`0x004B0730`/`0x004B1A78`/`0x004B0748`, the retained source-configuration
provider at `0x004B1608`, the retained offset provider at `0x004B1B48`, and
the retained commit provider at `0x004B0C8A`. The assertion sink is compiled
out by the pinned `-DOPEN_CFW_ULED_ASSERT` no-op fail-stop binding and the
GPU-failure diagnostic binding stays inert. The discontiguous 64-byte IAR
literal/template pool at `[0x0046CA74,0x0046CAB4)` stays retained stock data,
and the sole direct call at `0x0046CA64` reaches the leaf through the
redirect. Routing required extending the reviewed rodata local-name class in
`tools/apollo_overlay.py` to admit Clang `.L__const.<function>.<variable>`
constant-aggregate locals alongside the existing `.L.str[.N]` string class.
Apple Clang 21 overlay/component/package pins are `164536/3687932/4466426`
(SHA-256 `a437e33e…`, `4fdb5af5…`, `cc1642fd…`). The leaf and redirect are
gated `apple-clang`; linux-clang leaf pins await Linux toolchain
regeneration. Ownership: 584 replaced stock body bytes. See
`docs/research/g2-uled-display-preprocess-recovery.md`.

## Current G2 KVDB time increment

The retained `service_kvdb_time.c` object is completely bounded at
`[0x00585618,0x00585840)`: three functions contribute 494 code bytes and the
owned tail contributes 58 bytes. Two stored roots, three direct entry calls,
31 provider/internal calls, and zero legitimate strict-interior ingress close
it. One unaligned packed-string byte window is explicitly qualified as data.

The twelve-byte `kvTime` record at `0x2000380C` contains version, timestamp,
signed timezone, four preserved reserved bytes, and CRC at offset ten. Default
initialization produces checksum `0x18F0`; persistence forces version 3 and
changes the factory-values checksum to `0xC67A`. The field-specific writer and
non-importing pre-v3 migration policy are host-tested, and the candidate
compiles as exactly three Thumb symbols. Production routing and ownership
remain zero. See `docs/research/g2-kvdb-time-recovery.md`.

## Current G2 KVDB onboarding-config increment

The retained `service_kvdb_onboarding_config.c` object is completely bounded
at `[0x004A777C,0x004A78D0)`: six functions contribute 286 code bytes and the
owned tail contributes 54 bytes. Eighteen direct entry calls, 20
provider/internal calls, no stored entry pointers, and zero strict-interior
ingress close it.

The `kvOnboardingConfig` record is one byte at `0x20000040`, initialized to
zero, with no version or CRC. Only index zero is writable; its null-value case
is a successful no-op. Both pointer-getter branches return the same record,
and reads import the stored byte directly while diagnosing only a zero backend
result. All six entry contracts are host-tested and the candidate compiles as
exactly six Thumb symbols. Production routing and ownership remain zero. See
`docs/research/g2-kvdb-onboarding-config-recovery.md`.

## Current G2 KVDB ring increment

The retained `service_kvdb_ring.c` object is completely bounded at
`[0x005D9B6C,0x005D9ED0)`: three functions contribute 796 code bytes and the
owned tail contributes 72 bytes. Two stored roots, two internal writer calls,
45 provider/internal calls, and zero strict-interior ingress close it.

The 24-byte `kvRing` record at `0x200037C8` contains version, MAC, a 14-byte
name, a preserved reserved byte, and CRC at offset 22. Default initialization
produces checksum `0x06D4`. The writer's distinct null/non-null name rules and
the non-importing v0 migration policy are host-tested; the candidate compiles
as exactly three Thumb symbols. Production routing and ownership remain zero.
See `docs/research/g2-kvdb-ring-recovery.md`.

## Current G2 KVDB module-configuration increment

The retained `service_kvdb_module_configure.c` object is completely bounded at
`[0x004922F8,0x00492CB4)`: six functions contribute 2,286 code bytes and the
owned alignment/literal region contributes 206 bytes. Three direct calls,
three stored reader roots, 115 provider/internal calls, and zero legitimate
strict-interior ingress close it. Eight raw interior-looking windows are
qualified as unaligned overlaps or, at `0x58ECC8`, the second halfword of a
valid 32-bit Thumb instruction.

The candidate preserves the one-byte language payload, four-byte dashboard
value and mode-two bypass, plus the 888-byte magic/count/menu-item record. It
pins the 44-byte stored and 52-byte runtime item layouts, built-in/custom load
rules, identical-write suppression, synchronization bracket, and the stock
lack of count and text clamps. Host tests and a six-symbol Thumb build pass;
production routing and ownership remain zero. See
`docs/research/g2-kvdb-module-configure-recovery.md`.

## Current G2 ULED display-preprocess increment

The retained `driver/uled/display_preprocess.c` linked object is closed as one
584-byte function at `[0x0046C73C,0x0046C984)` plus its separate 64-byte IAR
literal/template pool at `[0x0046CA74,0x0046CAB4)`. One direct caller, 23 real
provider calls, zero legitimate strict-interior ingress, two odd-byte raw
overlaps, and one explicitly excluded `sdiv` halfword close the object.

The candidate pins all nine assertions, the `0x619` 28-byte destination
descriptor, 16-byte region, width/offset halving, format nine, GPU result gate,
and six-call success sequence. Five candidate/analyzer host tests plus a
one-symbol Thumb build pass. Production routing and ownership remain zero. See
`docs/research/g2-uled-display-preprocess-recovery.md`.

## Current G2 BQ25180 charger-driver increment

The retained `driver/chg/drv_bq25180.c` object is completely bounded at
`[0x0053A670,0x0053AFC0)`: 28 functions contribute 2,268 code bytes and the
owned literal tail contributes 116 bytes. Fifty-six direct entry calls, 93
provider/internal calls, no stored entry pointers, and zero direct, `B.W`, or
raw strict-interior ingress close the object.

The candidate pins I2C bus 7/address `0x6A`, all register-field encodings,
runtime event/state offsets `0x14/0x16`, device-ID validation, and the exact
19-call initialization sequence. Starting from the reset fixture, defaults
produce register image `0000005a24241f4406002100f0`. Nine candidate tests,
four analyzer tests, and a 22-symbol freestanding Thumb build pass. Production
routing is live under the reviewed apple-clang profile: twenty-two relocated
leaves and twenty-two entry redirects replace 1,792 stock body bytes, bound
to the retained I2C read/write backends at `0x0050436E`/`0x005044B4` and the
retained `memset` provider at `0x0043C0E4`, with the assertion sink compiled
out by the pinned no-op fail-stop binding and the diagnostic binding inert.
See `docs/research/g2-chg-bq25180-recovery.md`.

## Current G2 BQ27427 fuel-gauge increment

The retained `driver/chg/drv_bq27427.c` object is completely bounded at
`[0x0053AFC0,0x0053C2A4)`: 37 functions contribute 4,440 code bytes and six
owned non-code intervals contribute 396 bytes. Eighty-eight direct entry
calls, 287 provider/internal calls, no stored entry pointers, and zero
legitimate direct, `B.W`, or raw strict-interior ingress close the object;
the one raw BL-looking interior window lies outside authenticated code.

The candidate pins I2C bus 7/address `0x55`, split little-endian register
I/O, the 36-byte data-memory block with its exact checksum and CFGUPDATE
flow, the initialized `0x80008000` unseal key, the seven live DM descriptors,
product defaults `{240,80,3100}`, and the telemetry record at `0x20073B18`.
Twelve candidate/analyzer host tests and a 33-symbol freestanding Thumb build
pass. Production routing is live under the reviewed apple-clang profile:
thirty-three relocated leaves and thirty-two entry redirects replace 3,938
stock body bytes, bound to the retained I2C read/write backends at
`0x0050436E`/`0x005044B4`, the retained millisecond delay wrapper at
`0x004910F4`, and the retained `memcpy`/`memset` providers at
`0x00439BE4`/`0x0043C0E4`, with the diagnostic binding inert by default. The
CFGUPDATE poll helper rides as an overlay-internal local-function sibling
leaf under the reviewed `allow_local_function`/
`allow_local_relocation_targets` contracts, and the DM-descriptor-table and
product-defaults constants ride as reviewed read-only closures. See
`docs/research/g2-chg-bq27427-recovery.md`.

## Current G2 charger-common increment

The retained `platform/service/charger/charger_common.c` object is completely
bounded at `[0x004ACE10,0x004AD9B8)`: 14 functions contribute 2,764 code bytes
and three owned non-code regions contribute 220 bytes. Twenty-five direct entry
calls, 157 provider/internal calls, no stored entry pointers, and zero
legitimate strict-interior ingress close it; six raw interior-looking values
are explicitly qualified instruction/data overlaps.

The candidate pins the 24-byte aggregate runtime, eight-byte local cache,
initial retry schedule, near-full SOC compensation, charging debounce, peer
aggregation, and twelve-byte service-`0x0105` message ABI. Six candidate tests,
four analyzer tests, and an 11-symbol freestanding Thumb build pass. Production
routing is live under the reviewed apple-clang profile: eleven relocated
leaves and eleven entry redirects replace 2,400 stock body bytes, with the
five file-static state cells bound to their retained stock SRAM cells through
the new reviewed `allow_bound_static_data` relocation contract. See
`docs/research/g2-charger-common-recovery.md`.

## Current G2 BQ27427 fuel-gauge increment

The retained `driver/chg/drv_bq27427.c` object is completely bounded at
`[0x0053AFC0,0x0053C2A4)`: 37 functions contribute 4,440 code bytes and six
owned non-code regions contribute 396 bytes. Eighty-eight direct entry calls,
287 provider/internal calls, no stored entry pointers, and zero legitimate
strict-interior ingress close it.

The candidate pins I2C bus 7/address `0x55`, 36-byte data-memory blocks, the
checksum/CFGUPDATE/chemistry protocol, initialized unseal key `0x80008000`,
seven descriptors, defaults `{240,80,3100}`, and runtime offsets at
`0x20073B18`. Candidate and analyzer tests plus a freestanding Thumb build
pass. Production routing and ownership remain zero. See
`docs/research/g2-chg-bq27427-recovery.md`.

## Current G2 common ULED MSPI increment

The retained `driver/uled/drv_mspi_uled_common.c` object is completely bounded
at `[0x0059C820,0x0059D244)`: 13 functions contribute 2,358 code bytes and the
owned alignment/literal region contributes 238 bytes. Thirty direct entry
calls (11 exterior), 151 provider/internal calls, one intentional stored
completion callback, and zero legitimate strict-interior ingress close it.

The analysis pins the 28-byte request and 24-byte HAL transfer layouts,
serial/quad control request `0x18`, interrupt mask `0x1A80`, blocking timeout
1,000,000, asynchronous semaphore timeout 3,000 ms, MSPI0, IRQ 20/priority
four, and the exact initialization sequence. Both panel template families and
all 11 exterior panel calls are now closed; a clean-room implementation still
requires independently named provider bindings and product-specific HAL
control validation. Production routing and ownership remain zero. See
`docs/research/g2-uled-mspi-common-recovery.md`.

## Current G2 JBD4010 ULED increment

The retained `driver/uled/jbd4010/drv_mspi_jbd4010.c` object is completely
bounded at `[0x00592658,0x005939A0)`: 24 functions contribute 4,588 code bytes
and eight owned alignment/literal regions contribute 348 bytes. Seventy-seven
direct entry calls, 289 provider/internal calls, 14 intentional stored entry
pointers in the external ULED manager table, and zero legitimate
strict-interior ingress close it.

The analysis pins four 28-byte request templates, the common-driver seam,
640x480 four-bit framebuffer geometry, partial and asynchronous refresh,
offset and brightness behavior, chip/die identification, power and recovery
flows, and the four accepted panel modes. Historical source remains
unavailable, so this is an analysis boundary rather than a clean-room source
candidate; production routing and ownership remain zero. See
`docs/research/g2-uled-jbd4010-recovery.md`.

## Current G2 Hongshi/A6N-G ULED increment

The retained `driver/uled/hongshi_a6ng/drv_mspi_a6ng.c` object is completely
bounded at `[0x005BBD48,0x005BD3A0)`: 22 functions contribute 5,276 code
bytes and nine owned alignment/literal regions contribute 444 bytes.
Ninety-nine intra-object entry calls, 366 genuine provider/internal calls, 15
intentional stored entry pointers in the external manager table, and zero
legitimate strict-interior ingress close it. Four raw BL-looking VFP windows
and two odd-byte interior overlaps are explicitly qualified.

The analysis pins four 28-byte request templates, the 50-byte configuration
stream, eight-byte status preamble, common-driver seam, 640x480 four-bit
framebuffer geometry, brightness and offset behavior, chip/serial reads,
power/recovery flows, and the two intentional exported stubs. Historical
source remains unavailable, so this is an analysis boundary rather than a
clean-room source candidate; production routing and ownership remain zero.
See `docs/research/g2-uled-a6ng-recovery.md`.

## Current G2 ULED manager increment

The retained `driver/uled/drv_mspi_uled.c` object is completely bounded at
`[0x004C9D44,0x004CA6F8)`: 14 functions contribute 2,332 code bytes and two
alignment halfwords plus its literal pool contribute 152 bytes. Eighteen
direct entry calls (17 exterior), 97 genuine provider/internal calls, one
startup termination pointer, one runtime framebuffer-callback materialization,
and zero legitimate strict-interior ingress close it. Fifteen raw
multiply/VFP windows and one odd-byte overlap are explicitly qualified.

The analysis pins the two-entry operations linker list, type-one A6N-G and
type-zero JBD4010 selection rule, active-record pointer, complete 64-byte
callback layout, wrapper offsets, and nibble-preserving 640x480 framebuffer
clear helper. All five retained-path ULED translation units are now bounded.
Historical source remains unavailable, so this is an analysis boundary rather
than a clean-room source candidate; production routing and ownership remain
zero. See `docs/research/g2-uled-manager-recovery.md`.

## Current G2 buzzer-driver increment

The retained `driver/buzzer/drv_buzzer.c` object is completely bounded at
`[0x005026BC,0x00502D58)`: 17 bodies contribute 1,520 code bytes and four
alignment/constant/literal regions contribute 172 bytes. Thirty-five direct
entry calls (18 exterior), 88 genuine provider/internal calls, one stored
one-shot timer callback, and zero legitimate strict-interior ingress close the
object. Eleven odd-byte address overlaps are explicitly qualified as data or
instruction windows.

The analysis pins the 96 MHz PWM basis, two 28-byte pitch-reload tables, nine
50-byte predefined voice records, note/tone/beat interpreter, repeat and timer
state, queued input-thread events, single-note scratch script, and direct
start/stop path. Historical source remains unavailable, so this is an
analysis boundary rather than a clean-room source candidate; production
routing and ownership remain zero. See
`docs/research/g2-drv-buzzer-recovery.md`. Its compact watchdog follow-on is
closed below.

## Current G2 watchdog-driver increment

The retained `driver/wdt/watchdog.c` object is completely bounded at
`[0x0052F2E0,0x0052F38C)`: two exact-named bodies contribute 140 bytes and the
literal pool contributes 32 bytes. Two direct entry calls (one exterior), 13
body calls, no stored entry pointers, and zero direct, stored, or `B.W`
strict-interior ingress close it.

`watchdog_init` calls `watchdog_enable`; enable invokes the lower provider only
when selector-zero returns byte value one. Historical source remains
unavailable, so this is analysis-only with zero production ownership. See
`docs/research/g2-watchdog-recovery.md`. Its retained eAT buzzer consumer is
closed below.

## Current G2 eAT buzzer-command increment

The retained `platform/service/eAT/at_buzzer.c` object is completely bounded
at `[0x005A4FD0,0x005A5488)`: exact-named `_atBuzzerTest` contributes 1,014
code bytes and its alignment/literal pool contributes 194 bytes. The handler
has no direct caller; the sole ingress is the odd Thumb pointer in the
sixteen-byte `AT^BUZZER` command record. Seventy-six direct body calls, one
stored entry pointer, and zero direct, stored, or `B.W` strict-interior ingress
close the topology.

The analysis pins `note`, `play`, `start`, and `stop`, their exact parser
formats and range checks, retained help/error/success text, and calls into all
four corresponding bounded buzzer-driver APIs. It also preserves the stock
quirk that the AT layer accepts play types 0-10 while the nine-record driver
later rejects 9 and 10. Historical source remains unavailable, so this is
analysis-only with zero production ownership. See
`docs/research/g2-at-buzzer-recovery.md`. The adjacent command-table entry is
`AT^AUDIO` at `0x005A5488`; its retained `at_codec.c` handler is closed below.

## Current G2 eAT audio-control increment

The retained `platform/service/eAT/at_codec.c` object is completely bounded
at `[0x005A5488,0x005A5520)`: exact-named `_atAudioCtrl` contributes 118 code
bytes and its alignment/literal pool contributes 34 bytes. Its only ingress is
the stored odd Thumb pointer in the `AT^AUDIO` command record. Ten body calls
and zero direct, stored, or `B.W` strict-interior ingress close the topology.

A leading `1` invokes provider `0x0054F380` with selector seven; a leading `0`
invokes `0x0054F50E` with selector seven. Every path emits `AUD_AUDIO+OK` and
returns one. Historical source remains unavailable, so this is analysis-only
with zero production ownership. See `docs/research/g2-at-codec-recovery.md`.
Its retained `at_fs.c` neighbor is closed below.

## Current G2 eAT filesystem-command increment

The retained `platform/service/eAT/at_fs.c` object is completely bounded at
`[0x005A5530,0x005A5720)`: four bodies contribute 416 code bytes and the pool
contributes 80 bytes. Three stored command pointers register `AT^RM`, `AT^LS`,
and `AT^MKDIR`; two internal calls reach the recursive listing helper. The 33
body calls and absence of exterior direct or strict-interior ingress close the
topology.

The analysis pins filesystem-ready word `0x200746A8`, remove/mkdir providers,
recursive dot-entry filtering, child-path construction, directory and
byte/integer-KiB file reports, and exact success/error responses. Historical
source remains unavailable, so this is analysis-only with zero production
ownership. See `docs/research/g2-at-fs-recovery.md`. The next retained eAT
frontier, `at_tp.c`, is closed below.

## Current G2 eAT touch-panel increment

The retained `platform/service/eAT/at_tp.c` object is completely bounded at
`[0x005A5984,0x005A5D94)`: two bodies contribute 898 code bytes and the
alignment/pool regions contribute 142 bytes. The stored `AT^TP` handler
pointer and two internal helper calls are the complete entry set. Seventy body
calls and zero exterior direct or strict-interior ingress close the topology.

The analysis pins difference capture, debug flag `0x20075017`, proximity
baseline read/save, gesture configuration read/write, 1-65,535-ms threshold
validation, 100-ms write/readback verification, and every retained response.
Historical source remains unavailable, so this is analysis-only with zero
production ownership. See `docs/research/g2-at-tp-recovery.md`. All four
retained eAT source paths are now bounded. The intervening pathless cluster is
closed below.

## Current G2 pathless eAT core/sensor increment

The twelve registered handlers between `at_fs.c` and `at_tp.c` are completely
bounded at `[0x005A5720,0x005A5984)`: 486 code bytes and 126 owned
alignment/literal bytes. The table `[0x006C92E0,0x006C93A0)` registers the
commands from `AT^INFO` through `AT^BRIGHTNESS_READ`; those twelve odd Thumb
pointers are the complete entry set. Forty-nine body calls and zero direct or
strict-interior ingress close the topology.

The analysis pins the S200/product/build report, reset and 14-byte PSN
contracts, IMU raw/Euler operations, screen-X stub, screen-Y machine range,
ALS read/enable/scale behavior, and brightness write/read behavior. It also
preserves the stock quirks that screen Y accepts zero despite its 1-192 error
text and unsupported ALS values are still acknowledged. No retained path
partitions the cluster, so historical source inventory and licensing remain
unknown. This is analysis-only with zero production ownership; see
`docs/research/g2-eat-core-sensor-recovery.md`.

## Current G2 pathless eAT NUS increment

The standalone `AT^NUS` object between `at_codec.c` and `at_fs.c` is bounded
at `[0x005A5520,0x005A5530)`: a twelve-byte handler plus one four-byte
literal. Its command record supplies the only entry. The handler emits
`NUS+OK`, returns one, and has no direct or strict-interior ingress. No
retained path or historical symbol survives, so this remains analysis-only
with zero production ownership; see `docs/research/g2-at-nus-recovery.md`.

## Current G2 pathless eAT bond/connect increment

The `AT^CLEANBOND` / `AT^BLE_KEEPCONNECT` pair immediately before retained
`at_buzzer.c` is completely bounded at `[0x005A4FA4,0x005A4FD0)`: 34 code
bytes plus ten alignment/literal bytes. Two command pointers are the complete
entry set. The handlers call providers `0x004B46CE` and `0x0046F2DC`, emit
their retained acknowledgements, and return zero. No historical path or
symbols survive, so the pair remains analysis-only with zero production
ownership; see `docs/research/g2-eat-bond-connect-recovery.md`.

## Current G2 complete eAT registry increment

An exhaustive structural scan now proves that `[0x006C9260,0x006C93B0)` is
the complete stock eAT registry: exactly 21 sixteen-byte records, 336 bytes,
with no valid `AT...` record elsewhere in the image. Every record is assigned
to one of the seven closed analyses above; there are no unassigned registered
handlers. See `docs/research/g2-eat-registry-recovery.md`. This closes the
registered eAT runtime surface while leaving pathless historical source
inventories and production replacements as separate future work.

## Current G2 protobuf-service frontier census

All 15 retained `platform\protocols\pb_service_*` paths are now ranked against
the authenticated 7,370-function corpus. They anchor 119 discovered bodies /
40,844 body bytes. The completed health closure separately restores one
Ghidra-missed wrapper beyond that anchor census. The five smallest closures, `pb_service_translate.c`,
`pb_service_glasses_case.c`, `pb_service_ring.c`, `pb_service_conversate.c`,
and `pb_service_teleprompt.c`, are complete below; the Even-AI, terminal, and
device-configuration, health, setting, and onboarding closures are complete
too; notification is next.
See `docs/research/g2-pb-service-frontier-ranking.md`; the counts are lower
bounds and do not infer pathless functions or production ownership.

## Current G2 translate protobuf-service increment

The retained `pb_service_translate.c` object is completely bounded at
`[0x0059F53C,0x0059FAE0)`: four exact-named bodies / 1,324 code bytes and a
120-byte pool. Eight direct entries, 74 body calls, nanopb decode/encode
buffers, status codes, 3,000-ms duplicate suppression, message subtypes 5/6/7,
and master-gated BLE send/notify paths are pinned. Historical source remains
unavailable, so this is analysis-only with zero production ownership. See
`docs/research/g2-pb-service-translate-recovery.md`.

## Current G2 glasses-case protobuf-service increment

The retained `pb_service_glasses_case.c` object is completely bounded at
`[0x00510A0C,0x00510FD8)`: four exact-named bodies / 1,360 code bytes and a
124-byte pool. Four exact-start entries, 86 body calls, nanopb RX/TX buffers,
status codes, the command-1/nested-selector-3 message layout, five case-state
bytes, notification sequence behavior, and service-`0x81` BLE send/notify
paths are pinned. Historical source remains unavailable, so this is
analysis-only with zero production ownership. See
`docs/research/g2-pb-service-glasses-case-recovery.md`. The next bounded
protobuf-service frontier was `pb_service_ring.c`, now closed below.

## Current G2 ring protobuf-service increment

The retained `pb_service_ring.c` object is completely bounded at
`[0x005CE1DC,0x005CE7C4)`: four exact-named bodies / 1,362 code bytes and a
150-byte alignment/pool tail. Three internal exact-start calls, one stored
relay callback, 82 body calls, nanopb status/buffer contracts, bounded
six-byte MAC copying, event ID/parameter behavior, and service-`0x91` BLE
transmit are pinned. The only raw interior candidate is proven to be the
second halfword of `SDIV`, leaving zero real interior ingress. Historical
source remains unavailable, so this is analysis-only with zero production
ownership. See `docs/research/g2-pb-service-ring-recovery.md`; conversate is
the next retained protobuf-service frontier, now closed below.

## Current G2 conversate protobuf-service increment

The retained `pb_service_conversate.c` object is completely bounded at
`[0x005B1B4C,0x005B22BC)`: six exact-named bodies / 1,776 code bytes and a
128-byte pool. Ten exact-start entries, 96 body calls, caller-owned RX decode,
the 3,000-ms duplicate filter, the shared 0xFAC-byte TX message, and five
command/tag envelopes over service `0x0B` are pinned with zero stored or
strict-interior ingress. Historical source remains unavailable, so this is
analysis-only with zero production ownership. See
`docs/research/g2-pb-service-conversate-recovery.md`; teleprompt is closed
below.

## Current G2 teleprompt protobuf-service increment

The retained `pb_service_teleprompt.c` object is completely bounded at
`[0x005885B4,0x00588D74)`: seven exact-named bodies / 1,854 code bytes and a
130-byte alignment/literal tail. Eleven exact-start entries, 98 body calls,
caller-owned RX decode with 3,000-ms replay filtering, the shared 0xF58-byte
TX message, and six command/tag envelopes over service 6 are pinned. The
only raw interior candidate is the second halfword of a valid `MUL`, leaving
zero real strict-interior ingress. Historical source remains unavailable, so
this is analysis-only with zero production ownership. See
`docs/research/g2-pb-service-teleprompt-recovery.md`; Even-AI is closed below.

## Current G2 Even-AI protobuf-service increment

The retained `pb_service_even_ai.c` object expands from seven initial anchors
to a complete 25-function object at `[0x004E31CC,0x004E54C8)`: 8,404 code
bytes plus 552 distributed alignment/pool bytes. Twenty-six exact-start
entries, 494 body calls, 23 assertion records, the immediate one-byte replay
filter, ten command/tag pairs, three notification variants, and the shared
0x20C-byte message over service 7 are pinned. There is zero direct or stored
exact-entry interior ingress. Historical source remains unavailable, so this
is analysis-only with zero production ownership. See
`docs/research/g2-pb-service-even-ai-recovery.md`; terminal is closed below.

## Current G2 terminal protobuf-service increment

The retained `pb_service_terminal.c` object is completely bounded at
`[0x005CE7C4,0x005CF2B4)`: 13 exact-named bodies / 2,554 code bytes and a
246-byte alignment/literal tail. Thirty-three exact-start entries, 130 body
calls, caller-owned RX decode with 3,000-ms replay filtering, eleven supported
tag layouts, ten notify envelopes plus the command response, and the shared
0x850-byte message over service `0x30` are pinned. Direct and `B.W`
strict-interior ingress and stored exact-entry pointers are zero; 15 raw
interior-looking byte windows are retained as accidental collision evidence.
Historical source remains unavailable, so this is analysis-only with zero
production ownership. See
`docs/research/g2-pb-service-terminal-recovery.md`; device configuration is
closed below.

## Current G2 device-config protobuf-service increment

The retained `pb_service_dev_config.c` object is completely bounded at
`[0x004D83D8,0x004D8F4C)`: three exact-named bodies / 2,646 code bytes and
286 distributed gap/pool bytes. Three exact-start entries, 172 body calls, a
14-command dispatcher, the error-code classifier, the command-10/tag-9 error
response, and the shared 0xD0-byte message over service `0x80` are pinned.
Direct and `B.W` strict-interior ingress and stored exact-entry pointers are
zero. Historical source remains unavailable, so this is analysis-only with
zero production ownership. See
`docs/research/g2-pb-service-dev-config-recovery.md`; health is closed below.

## Current G2 health protobuf-service increment

The retained `pb_service_health.c` object is completely bounded at
`[0x0055A558,0x0055B2A4)`: eight exact-named bodies / 3,092 code bytes and
312 distributed alignment/pool bytes. The closure restores the Ghidra-missed
`PB_RxHealthMultHighlight` body at `0x0055AF14`, pins eight exact-start
entries, 180 body calls, eight assertion records, four RX helper contracts,
four command/tag transmit envelopes, and the shared 0x31C-byte message over
service `0x0E`. Direct and `B.W` strict-interior ingress and stored exact-entry
pointers are zero. Historical source remains unavailable, so this is
analysis-only with zero production ownership. See
`docs/research/g2-pb-service-health-recovery.md`; setting is closed below.

## Current G2 setting protobuf-service increment

The retained `pb_service_setting.c` object expands from nine corpus anchors to
11 exact-named functions at `[0x0049B198,0x0049C070)`: 3,466 code bytes plus
334 distributed alignment/pool bytes. Two missed wrappers at `0x0049BA58`
and `0x0049BEAC`, 23 exact-start entries, 221 body calls, duplicate-magic
suppression, full device-status construction, response/local-data serializers,
and device/recalibration/silent-mode notifications over service 9 are pinned.
Direct and `B.W` strict-interior ingress and stored exact-entry pointers are
zero. Historical source remains unavailable, so this is analysis-only with
zero production ownership. See
`docs/research/g2-pb-service-setting-recovery.md`; onboarding is closed below.

## Current G2 onboarding protobuf-service increment

The retained `pb_service_onboarding.c` object is completely bounded at
`[0x004A78D0,0x004A8560)`: nine exact-named bodies / 3,024 code bytes and
192 distributed alignment/pool bytes. Nine exact-start entries, 181 body
calls, eight assertion records, configuration/heartbeat/event command pairs,
two notification encoders, heartbeat readiness states, and the shared
16-byte message over service `0x10` are pinned. Direct and `B.W`
strict-interior ingress and stored exact-entry pointers are zero; three raw
interior-looking byte windows are retained as accidental collision evidence.
Historical source remains unavailable, so this is analysis-only with zero
production ownership. See
`docs/research/g2-pb-service-onboarding-recovery.md`; notification is closed
below.

## Current G2 notification protobuf-service increment

The retained `pb_service_notification.c` object is completely bounded at
`[0x004D6BA8,0x004D798C)`: nine exact-named bodies / 3,318 code bytes and
238 distributed alignment/pool bytes. Ten exact-start entries, 202 body
calls, seven assertion records, control and whitelist command pairs, the
generic response, allocated app-not-whitelisted notification, CRC status
mapping, and the shared 76-byte message over service 4 are pinned. Direct and
`B.W` strict-interior ingress and stored exact-entry pointers are zero; three
raw interior-looking byte windows are accidental collisions. Historical
source remains unavailable, so this is analysis-only with zero production
ownership. See `docs/research/g2-pb-service-notification-recovery.md`;
`pb_service_dev_setting.c` is closed below.

## Current G2 device-setting protobuf-service increment

The retained `pb_service_dev_setting.c` object is completely bounded at
`[0x00542DC4,0x00543C48)`: ten exact-named bodies / 3,432 code bytes and
284 distributed alignment/pool bytes. Ten exact-start entries, 222 body calls,
20 assertion records, five receive/transmit command pairs, factory-reset and
heartbeat effects, the five-byte time cache, caller-owned nanopb storage, and
service-`0x80` transport are pinned. Direct and `B.W` strict-interior ingress
and stored exact-entry pointers are zero; one raw interior-looking byte window
is an accidental collision. Historical source remains unavailable, so this is
analysis-only with zero production ownership. See
`docs/research/g2-pb-service-dev-setting-recovery.md`; quicklist is closed
below.

## Current G2 quicklist protobuf-service increment

The retained `pb_service_quicklist.c` object is completely bounded at
`[0x0055894C,0x005597F0)`: ten exact-named bodies / 3,468 code bytes and
280 distributed alignment/pool bytes. Ten exact-start entries, 199 body calls,
eight assertion records, item/multi-item/event command pairs, separate 0x1238
decode/transmit objects, the 0x400-byte nanopb buffer, notification sequence,
and service-`0x0C` transport are pinned. Direct and `B.W` strict-interior
ingress and stored exact-entry pointers are zero; one raw interior-looking byte
window is an accidental collision. Historical source remains unavailable, so
this is analysis-only with zero production ownership. See
`docs/research/g2-pb-service-quicklist-recovery.md`; `pb_service_pair_mgr.c` is
closed below.

## Completed G2 pair-manager and protobuf-service frontier

The retained `pb_service_pair_mgr.c` object expands from 17 path-correlated
anchors to 20 linked functions at `[0x004BB3DC,0x004BD054)`: 6,564 code bytes
and 724 distributed alignment/pool bytes. Twenty-five exact-start entries, 418
body calls, 23 assertion records, six command/tag pairs, security-auth state,
ring connection policy, BLE parameter control, disconnect/unpair cleanup, and
service-`0x80` transport are pinned. Six stored Thumb pointers intentionally
target the ring-connect notification wrapper; direct and `B.W` strict-interior
ingress remain zero and the sole other raw candidate is an accidental
collision.

This closes every retained `pb_service_*` path. The original 119-function /
40,844-byte lower-bound census now reconciles to 143 linked functions, 47,644
body bytes, and 51,744 physical object bytes across all 15 services. Historical
source-only inventory remains unavailable and none is production-routed, so
OpenCFW claims zero ownership. See
`docs/research/g2-pb-service-pair-mgr-recovery.md` and the pinned complete
closure manifest.

## Current G2 EFS-service and first-party frontier increment

The retained `platform\protocols\efs_service\efs_service.c` object is now
completely bounded at `[0x00456722,0x00458DF0)`. Six retained anchors plus six
restored pathless functions contribute 9,276 code bytes; 658 owned pool/gap
bytes bring the physical object to 9,934 bytes. Thirty-five exact-start direct
calls, 559 body calls, ten intra-body wide branches, frame IDs `0xC4..0xC7`,
the 0x78-byte transfer state, separate 4-KiB import/export buffers, and all
import/export type and CRC contracts are pinned. Real strict-interior and
stored-entry ingress are zero. Historical source remains unavailable and the
object is not production-routed.

The reproducible first-party census now partitions all 234 retained paths: 68
closed and 166 open. Closed paths anchor 361 functions / 142,762 body bytes;
open paths anchor 869 / 342,512, with no cross-status function. Complete-object
records total 183,126 body bytes, while 67 records report 199,124 known
physical bytes. These are lower-bound retained-path metrics, not whole-image
source coverage. See `docs/research/g2-efs-service-recovery.md` and
`docs/research/g2-first-party-frontier-census.md` and
`docs/research/g2-ota-service-recovery.md`.

The smallest genuinely open retained-path object,
`app\gui\PdtDistortionTest\pdt_distortion_test.c`, is now closed at
`[0x005CF2B4,0x005CF634)`: four functions / 850 body bytes / 896 physical
bytes. The audit restored a four-byte always-true predicate missed by Ghidra,
authenticated its pointer-table entry, closed the screen-ID `0x110` descriptor,
and pinned the event-2 LVGL object tree and adjacent gray-screen boundary. It
remains analysis-only with no historical source or package ownership; see
`docs/research/g2-pdt-distortion-test-recovery.md`.

The adjacent `app\gui\PdtGrayScreen\pdt_gray_screen.c` object is closed too:
three pointer-routed functions / 340 body bytes / 372 physical bytes, including
the second restored always-true predicate and the exact eight-band symmetric
grayscale pattern. See `docs/research/g2-pdt-gray-screen-recovery.md`.

The contiguous production-screen family endpoint,
`app\gui\ProductionTest\production_test.c`, is also closed: three functions /
286 body bytes / 316 physical bytes, its screen-ID `0x10B` registration, and
the exact 3×3 white-dot grid are pinned in
`docs/research/g2-production-test-screen-recovery.md`.

The retained `platform\ble\profiles\gatt\profile_gatt.c` object is no longer
opaque first-party glue. All six bodies / 322 bytes map to Packetcraft Cordio
`gatt_main.c`; exact r20.05c source/header blobs are admitted under Apache-2.0,
and the only local delta is an EasyLogger expansion before `GattDiscover`'s
unchanged upstream call. See `docs/research/cordio-gatt-profile-source-recovery.md`.

The adjacent `platform\ble\profiles\ancc\profile_ancc.c` object is also
upstream-founded rather than opaque product glue. Its complete
`[0x004BEA04,0x004BF990)` boundary has 21 bodies / 3,712 code bytes / 3,980
physical bytes. AmbiqSuite's 17-definition ANCC source explains 12 stock
functions; nine bounded functions are G2 message, synchronization, whitelist,
callback, and logging extensions. Exact 2.5.1 source/header blobs are admitted
at selected public commit `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`.
The implementation is source-identical from authenticated 2.2.0 through 2.5.1
imports, so no unique historical producing commit is claimed. See
`docs/research/ambiqsuite-ancc-profile-source-recovery.md`.

The immediately preceding EUS/ESS/EFS/NUS profile group is now authenticated
as first-party Cordio integration rather than hidden upstream code. Its four
contiguous objects occupy `[0x004BDE4C,0x004BEA04)`, with 21 bodies / 2,374
code bytes / 3,000 physical bytes. The common four-byte state, connection/CCC
events, send events `0xA8..0xAB`, provider handles `0x0844..0x08A4`, direct
call topology, and retained-path pointers are pinned. AmbiqSuite lacks these
profiles, and Nordic's NUS implementation has a different API/event model.
See `docs/research/g2-ble-transport-profiles-recovery.md`.

The final OTA and Ring paths complete the retained BLE-profile directory. OTA
occupies 700 physical bytes with seven functions / 620 body bytes: four retain
AmbiqSuite's stable AMOTA CCC/A0/A1/handler skeleton and three are Even-local
actions. Exact 2.5.1 application/API sources are admitted at selected public
commit `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`, while the generating checkout
remains unobservable across four compatible release imports. Ring occupies
1,580 physical bytes with seven G2-local functions / 1,446 body bytes,
including 128-bit service discovery and epoch-qualified delayed CCC writes.
See `docs/research/g2-ble-ota-ring-profiles-recovery.md`.

The retained `ota_service.c` object is now completely bounded at
`[0x004448F4,0x004488EC)`: 25 linked functions / 15,394 body bytes plus 982
owned gap/pool bytes. The `0xC0..0xC3` frame routes, 0x70-byte transfer state,
0x60-byte export state, 4-KiB chunk/sector behavior, MRAM/filesystem/external
flash backends, CRC and read-after-write verification, filesystem healing,
107 exact-entry direct calls, and zero strict-interior ingress are pinned.
Historical source and license remain unavailable; production ownership is zero.

The retained `service_codec_host.c` object is now completely bounded at
`[0x0057BA88,0x0057DC40)`: 26 linked functions / 7,318 body bytes plus 1,314
owned gap/pool bytes. The 14-byte `BUXX` header, CRC fields, 16-byte body cap,
sequence byte, UART staging buffers, command/retry behavior, 83 exact-entry
calls, and zero real strict-interior ingress are pinned. Twenty-three exact
names survive; three pathless leaves retain semantic labels. Historical source
and license remain unavailable, so production ownership is zero. See
`docs/research/g2-service-codec-host-recovery.md`.

The adjacent retained `service_codec_dfu.c` object is now completely bounded
at `[0x00577D7C,0x0057A46C)`: 16 linked functions / 9,052 body bytes plus 916
owned gap/pool bytes. Its `FWPK` package header and 16-byte record layout,
boot/main image allocation and CRC checks, 230,400-baud two-stage boot
download, 256-byte chunking, 8-KiB flash scratch, conditional version check,
34 exact-entry calls, and zero real strict-interior ingress are pinned.
Historical source and license remain unavailable, so production ownership is
zero. See `docs/research/g2-service-codec-dfu-recovery.md`.

The retained `service_touch_dfu.c` object is now completely bounded at
`[0x0055FCB4,0x00561810)`: 32 linked functions / 6,430 body bytes plus 574
owned gap/pool bytes. Its `/firmware/touch.bin` `FWPK` package and type-3
record, framed command/reply checksum contract, 32-byte packets, 128-byte
program blocks, version-gated update sequence, 60 exact-entry calls, and zero
real strict-interior ingress are pinned. Twelve exact names survive and twenty
pathless leaves retain semantic labels. Historical source and license remain
unavailable, so production ownership is zero. See
`docs/research/g2-service-touch-dfu-recovery.md`.

The retained `terminal_pb_msg_handler.c` object is now completely bounded at
`[0x005E8178,0x005EA224)`: 27 linked functions / 7,688 body bytes plus 676
owned gap/pool bytes. Ten retained anchors and 17 pathless restorations close
the object. Its 13-slot event dispatcher, 12 action pointers, callback ingress,
session/state gates, 2-second tool-start suppression, 56 exact-entry calls,
and zero real strict-interior ingress are pinned. The lone raw interior-call
candidate is the second halfword of a valid `UXTAB`. Nineteen exact diagnostic
names survive; historical source and license remain unavailable, so production
ownership is zero. See
`docs/research/g2-terminal-pb-msg-handler-recovery.md`.

The retained `service_whitelist.c` object is now completely bounded at
`[0x004D5930,0x004D6BA8)`: seven linked functions / 4,310 body bytes plus 418
owned gap/pool bytes. Five retained anchors and two pathless helpers close the
object. Its 8,002-byte state, five enable flags, 100 records with 64-byte IDs
and 16-byte names, filesystem/CRC cache, built-in identifiers, fail-open
disable policy, nine exact-entry calls, and zero strict-interior ingress are
pinned. Historical source and license remain unavailable, so production
ownership is zero. See `docs/research/g2-service-whitelist-recovery.md`.

The retained `teleprompt_page_data.c` object is now completely bounded at
`[0x0058A8E0,0x0058BCE0)`: 21 linked functions / 4,728 body bytes plus 392
owned gap/pool bytes. Nine retained anchors and twelve restored helpers close
the object. Its 20-slot `0x414`-stride ring, 1,036-byte page copy contract,
four-page visible window, 14-page ensure band, 500-ms debounce, 5-second
loading retry, 2.5-second preload timer, 81 exact-entry calls, and zero real
strict-interior ingress are pinned. Historical source and license remain
unavailable, so production ownership is zero. See
`docs/research/g2-teleprompt-page-data-recovery.md`.

The retained `imu_icm45608.c` object is now completely bounded at
`[0x004A35B0,0x004A6644)`: 53 linked functions / 11,674 body bytes plus 762
owned gap/pool bytes. Eleven retained anchors and 42 raw Thumb-restored entries
close the object. Its stored bus-read, bus-write, and FIFO callback entries,
20-slot `0x70` sample ring, vector/quaternion/event processing, raw-CSV capture,
two-minute automatic stop, 72 exact-entry calls, and zero external
strict-interior ingress are pinned. Historical source and license remain
unavailable, so production ownership is zero. See
`docs/research/g2-imu-icm45608-recovery.md`.

The TinyFrame version boundary is now narrower than behavior-only comparison
allowed. Ten retained `TF_Error` `__LINE__` arguments select the exact
`TinyFrame.c`/`.h` blobs introduced by official commit `eb75483e`; repository
head `a29167a` retains the same two blobs and changes only demo content. The
reusable core source is therefore pinned to `eb75483e`, while the historical
checkout remains the honest two-commit interval `eb75483e…a29167a`. Release
2.3.0 and `44ecc068` are excluded from the minimum-patch core baseline. A
negative sweep of all 113 public upstream forks found no G2 magic/config
match. The exact upstream core, MIT license, G2 config, short-enum ABI,
`0x7158` pristine size, and `0x7160` magic-extended layout are now vendored and
verified offline. The bookended G2 boundary is now production source-owned;
only golden-packet hardware validation remains.
All 31 linked functions / 2,994 code bytes are now exactly spanned and hashed;
the intervening 124-byte pool is non-executable, and thirteen unused upstream
APIs are dead-stripped. This accounts for every byte in the 3,118-byte linked
translation unit. The routine at `0x00491838` is corrected to upstream-private
`renew_id_listener`, not `TF_DeInit`. See
`docs/research/tinyframe-send-version-recovery-audit.md` and
`docs/research/third-party-utility-gap-priority.md`.

The TinyFrame source-admission boundary is now executable and target-checked
without changing the authenticated upstream files. Stock has one dynamically
allocated instance in slot `0x200749C4`; role 1 selects master/peer bit 1 and
role 2 selects slave/peer bit 0. All application consumers treat the pointer as
opaque, permitting the adapter to return the pristine core
at allocation base `+4` inside the recovered `magic | core | magic` layout.
Host tests cover send/receive, listener and timeout callback pointer identity,
transport timeout 100, logger delivery, and bookend survival; Cortex-M55
static assertions close `0x7158`/`+4`/`+0x715C`/`0x7160`. A companion concrete
port candidate uses source-owned `heap_4` and retains the authenticated
first-party sync wrapper `[0x00541790,0x005417A4)`; exact target sections and
relocations are pinned. The stateless boundary removes the writable port table,
selects explicit no-op logging, and atomically production-routes all eight
stock-facing roots over the exact 14-function live graph. Apple and Linux
complete overlay/component/package roots and manifest ownership are pinned;
only hardware frames remain. See
`docs/research/tinyframe-source-admission-boundary-audit.md`.

The complete linked CMSIS-FreeRTOS wrapper object is now authenticated at
`[0x0044900E,0x00449ED2)`: 43 functions / 3,758 executable bytes plus 22
literal bytes account for all 3,780 physical bytes. The map separates 38
public APIs from five private helpers, closes 831 external BL callers and 41
internal calls, proves the sole stored entry is `TimerCallback`, and records
33 public APIs as dead-stripped. Three live version discriminators exclude
v10.4.6-era source, while the missing later thread-flags re-notification fix
excludes `bb8a350a` and descendants for that linked body. The maintained
baseline remains v10.5.1 commit `d213f261`; its exact `cmsis_os2.c` blob first
appeared at `13acfbef`. The new offline analyzer and six mutation/CLI tests
make this a source-admission boundary, not a production-ownership claim. See
`docs/research/cmsis-freertos-linked-function-census.md`.

The first four census-ranked CMSIS leaves are now production source-owned:
private `IRQ_Context`, `osKernelGetTickCount`, `osThreadGetId`, and
`osMessageQueueGetCapacity`. Their complete 88 stock bytes redirect atomically
to 84 Apache-2.0 source bytes plus four alignment bytes. The closure reuses the
already integrated scheduler, tick, and opaque current-task providers and the
authenticated Queue_t length offset, so it reads no TCB field and is unaffected
by the 112-byte vendor extension. Apple Clang 21 and Linux Clang 22.1.8 both
produce pinned complete overlays and packages. CMSIS production ownership is
now six public APIs plus one private helper; 32 public APIs and four private
helpers remain. See
`docs/research/cmsis-freertos-core-leaves-source-boundary-audit.md`.

The next two census-ranked leaves are also production source-owned:
`osSemaphoreGetCount` and `osMessageQueueGetCount`. Both stock entries are 36
bytes and compile from one selector-isolated Apache-2.0 adapter to identical
36-byte unrelocated target bodies. They reuse the source-owned IRQ helper and
normal/ISR queue-count providers, inspect no TCB field, and close seven
external calls. Apple and Linux complete-package pins pass. CMSIS production
ownership is now eight public APIs plus one private helper; 30 public APIs and
four private helpers remain. See
`docs/research/cmsis-freertos-count-leaves-source-boundary-audit.md`.

`osMessageQueueDelete` was the ninth source-owned public CMSIS wrapper. Its
complete 40-byte stock entry redirects to a 36-byte source body whose only
calls are the source-owned IRQ classifier and `vQueueDelete`; six external
callers are closed without reading Queue_t or TCB state. The next atomic
tranche promotes `osThreadYield`, `osKernelGetState`, `osMutexDelete`, and
`osTimerIsRunning`, all dependency-closed over already source-owned providers.
At that four-leaf milestone, CMSIS production ownership reached thirteen
public APIs plus private `IRQ_Context`; 25 public APIs and four private helpers
remained stock-backed.
Apple and Linux component and package replays are fail-closed. See
`docs/research/cmsis-freertos-message-queue-delete-source-boundary-audit.md`
and `docs/research/cmsis-freertos-thread-yield-source-candidate-audit.md`.
`osKernelGetState` calls the source-owned scheduler-state provider and reads
the authenticated CMSIS `KernelState` word at `0x20074384`; future source
admission of the wrapper-state writers remains a coupled review boundary.

The CMSIS mutex census also had one semantic label error: the linked 44-byte
entry at `0x0044986E` is `osMutexDelete`, not `osMutexGetOwner`. Its body
clears the recursive tag bit and calls `vQueueDelete`; the getter is the
dead-stripped API. The map, dead-strip ledger, family table, and analyzer are
corrected and all six mutation/CLI tests pass. A 38-byte production source
leaf now closes this wrapper over the same source-owned IRQ/delete providers.

`osTimerIsRunning` is the fourth dependency-closed candidate in this pass.
Its 26-byte target calls only source-owned IRQ classification and the already
production-integrated timer-active provider. ISR, null, inactive, and active
behavior is host-tested; production routing shares the aggregate-repin block.

The next synchronization tranche is also production source-owned:
`osMutexAcquire`, `osMutexRelease`, and `osSemaphoreRelease` replace 270 stock
bytes across 292 external callers with 220 source bytes plus two alignment
bytes. The earlier semaphore-take blocker was stale: its FreeRTOS V10.5.1
provider had already been promoted under the historical
`open_cfw_freertos_queue_semaphore_take_upstream_candidate` name. All six
unique fixed callees are source-owned, including the task/ISR give split and
PendSV request. Apple closes at `131980/3655376/4433870`; Linux closes at
`133848/3657244/4435738`. CMSIS production ownership is now sixteen public
APIs plus private `IRQ_Context`; 22 public APIs and four private helpers remain
stock-backed. See
`docs/research/cmsis-freertos-sync-ops-source-candidate-audit.md`.

The timer-operation tranche is now production source-owned as well:
`osTimerStart`, `osTimerStop`, and `osTimerDelete` replace 220 stock bytes
across 46 external callers with 234 source bytes plus four alignment bytes.
Their only fixed dependencies are the already source-owned IRQ,
timer-command/state/context, and heap-free providers. Apple closes at
`132218/3655614/4434108`; Linux closes at `134086/3657482/4435976`.
CMSIS production ownership is now nineteen public APIs plus private
`IRQ_Context`; 19 public APIs and four private helpers remain stock-backed.
See `docs/research/cmsis-freertos-timer-ops-source-candidate-audit.md`.

The complete event-flags quartet is production source-owned: constructor,
set, clear, and wait replace 388 stock bytes across 38 external callers with
334 source bytes plus four alignment bytes. All constructor, task/ISR event
group, and PendSV dependencies were already source-owned. Apple closes at
`132556/3655952/4434446`; Linux closes at `134424/3657820/4436314`.
CMSIS production ownership is now twenty-three public APIs plus private
`IRQ_Context`; 15 public APIs and four private helpers remain stock-backed.
See `docs/research/cmsis-freertos-event-flags-source-candidate-audit.md`.

`osTimerNew` and its private `TimerCallback` are now production source-owned as
one ABI unit. The 232-byte public stock entry has 12 callers; the adjacent
24-byte private callback is retained as inert authenticated evidence because
the source constructor stores only the source callback. The adapter preserves
the 44-byte `StaticTimer_t` threshold, 8-byte callback record, bit-zero dynamic
allocation tag, mixed static/dynamic record mode, and selective failure
cleanup. Apple closes at `132792/3656188/4434682`; exact-root Linux closes at
`134672/3658068/4436562`. CMSIS ownership is now 24 public APIs plus two
private helpers; 14 public APIs and three private memory-pool helpers remain.
See `docs/research/cmsis-freertos-timer-new-source-candidate-audit.md`.

`osMemoryPoolNew` is now production source-owned from the same authenticated
v10.5.1 source blob. Its complete 298-byte stock entry redirects to a 254-byte
Apple leaf (250 bytes under exact-root Linux), with all IRQ, heap_4, and static
counting-semaphore edges already source-owned. Tests preserve the recovered
116-byte control block, 32-bit allocation-size wrap, allocation flags, mixed
static/dynamic modes, and upstream v10.5.1 undersized-buffer quirks. Apple
closes at `133046/3656442/4434936`; exact-root Linux closes at
`134922/3658318/4436812`. CMSIS ownership is now 25 public APIs plus two
private helpers; 13 public APIs and three private pool helpers remain. See
`docs/research/cmsis-freertos-memory-pool-new-source-candidate-audit.md`.

The previously opaque FreeRTOS 112-byte TCB delta is now a verified minimal
source patch over authenticated V10.5.1. One 32-bit creation stack-depth word
is inserted after `pcTaskName[32]`, mirrored in `StaticTask_t`, and assigned by
`prvInitialiseNewTask`. The patch applies cleanly to pristine `tasks.c` and
`FreeRTOS.h`; a Cortex-M55 compile proves total size `0x70` and all later
trace, mutex, notification, and allocation offsets. Four stock functions and
six mutation/applicability/layout tests pin the boundary. The original vendor
identifier and private patch commit are unobservable, but no unexplained code
remains in this layout delta. See
`docs/research/freertos-g2-tcb-vendor-patch-audit.md`.

The FreeRTOS read-side ISR queue closure is now production source-owned from
Kernel V10.5.1 commit `def7d2df2b0506d3d249334974f51e427c17a41c`.
`xQueueReceiveFromISR` at `[0x00441DA6,0x00441E66)` and private
`prvCopyDataFromQueue` at `[0x00441F5E,0x00441F88)` redirect to authenticated
MIT adapters. Their queue-lock saturation, waiter wake, semaphore/null-buffer,
interrupt-mask, trace, and assertion paths are host-tested. This closes the
`xSemaphoreTakeFromISR` macro dependency used by CMSIS rather than inventing a
separate provider.

`osSemaphoreAcquire` and the complete memory-pool operation family are now
production source-owned from CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Public
`osMemoryPoolAlloc`/`osMemoryPoolFree` and private `CreateBlock`, `AllocBlock`,
and `FreeBlock` close every remaining private wrapper helper. The subsequent
FreeRTOS send and task-receive closures admit both `osMessageQueuePut` and
`osMessageQueueGet`; `osDelay` and its task-delay provider follow as the next
closed pair. Adding the priority-set pair and the complete
`eTaskGetState`/`prvDeleteTCB`/`vTaskDelete`/`osThreadTerminate` closure raises
CMSIS ownership to 33 of 38 linked public APIs and all five private helpers.
The following notification/thread-flags closure raises that to 35/38 while
preserving the stock pre-`bb8a350a` wait behavior; only kernel initialize,
kernel start, and thread creation remain. The Apple component is `3660486`
bytes / SHA-256
`9185ee131fcd2a40f6a3742cce0689b75a6c362e7a6f871ecf136f9125f99087`;
the package is `4438980` bytes / SHA-256
`807f1bec20e8b45e5469a0ca83ca2178ce1d2877f44fccfeb226f5adc7bad069`.
Package ownership is 137,783 source bytes, 98,034 generated bytes, and
4,203,163 opaque/cut-forward bytes. Two flash records remain unresolved;
none of this work signs, flashes, or operates hardware.

## CMSIS-FreeRTOS thread creation is production source-owned

The complete 200-byte `osThreadNew` stock entry now redirects to a strict
Apache-2.0 source leaf. Its behavior and provenance are pinned to
CMSIS-FreeRTOS v10.5.1 tag commit `d213f261`; the exact `cmsis_os2.c` blob was
first introduced by `13acfbef`. The wrapper retains authenticated FreeRTOS
V10.5.1 task creators and preserves the independently recovered `0x70` G2
static TCB threshold plus the 16-bit dynamic stack-depth cast. Seven hosted
tests cover validation, static/dynamic creation, malformed attributes,
defaults, failure, and truncation.

Apple now closes at overlay/component/package roots
`137260/3660656/4439150`; Linux closes at `139138/3662534/4441028`. Exact
canonical package ownership is 137,945 source, 98,242 generated, and
4,202,963 opaque bytes. CMSIS coverage is 36/38 public APIs and 5/5 private
helpers. Only writer-coupled `osKernelInitialize` and `osKernelStart` remain.

## CMSIS-FreeRTOS kernel lifecycle completes production wrapper ownership

The final writer-coupled `osKernelInitialize` and `osKernelStart` pair is now
source-owned. Both leaves share the authenticated CMSIS `KernelState` word at
`0x20074384` with the earlier get-state leaf, use source-owned IRQ and
scheduler-state providers, and preserve the write-to-running operation before
calling retained `vTaskStartScheduler`. The stock `SVC_Setup` is exactly the
two-byte no-op `bx lr`; no invented provider is needed.

Apple now closes at overlay/component/package roots
`137368/3660764/4439258`; Linux closes at `139248/3662644/4441138`.
Canonical package ownership is 138,051 source, 98,388 generated, and
4,202,819 opaque bytes. CMSIS production coverage is complete at 38/38 public
APIs and 5/5 private helpers. Remaining FreeRTOS work starts below the CMSIS
wrapper boundary at scheduler-global and Apollo port seams. The retained
`vTaskStartScheduler` core is subsequently source-recreated and dual-profile
qualified; it remains production-excluded until those globals and port seams
can be admitted atomically.

## FreeRTOS scheduler-start core is source-qualified

The complete retained `[0x00454CEC,0x00454D7C)` scheduler-start algorithm is
now represented by a bounded MIT V10.5.1 adaptation. The eight focused tests
pin the sole CMSIS caller, all six stock outgoing calls, static idle memory
(`0x20071E30`, `0x2005F154`, depth `0x400`), four scheduler globals, success
and failure ordering, both target objects, and all 20 relocations. Apple emits
a 156-byte function; Linux emits 160 bytes. Production remains deliberately
unchanged pending atomic global binding and Apollo scheduler-port validation.

The following port tranche closes the exact V10.5.1 `xPortStartScheduler`
algorithm and the downstream Apollo timer setup as two more production-excluded
candidates. The port preserves both SHPR3 priority writes and the four stock
tail calls. Timer setup authenticates 32 counts/tick, 1,024 Hz, maximum
suppression `0x07FFFFFB`, IRQ 32, compare A, and configuration `0x103` against
AmbiqSuite 5.1.0. Both candidates pass Apple/Linux object and relocation gates;
the elapsed-tick ISR and tickless/power path remain.

Those final two bounded STIMER algorithms are now closed by subsequent
production-excluded candidates. The IRQ/vector candidate preserves the stock
wrap formula without `+1`, four volatile tick-rate reads, compare re-arm, and
PendSV aggregation. The tickless candidate closes abort, clamp, pre/post power
hooks, optional WFI, wake re-arm, and capped `vTaskStepTick`. Their 14 focused
tests pass on both compiler profiles. No bounded STIMER algorithm remains
opaque; real timing/sleep validation and atomic production admission remain.

## FreeRTOS context switching and G2 trace ring are source-qualified

The complete 206-byte `vTaskSwitchContext` stock body now has a separate
production-excluded V10.5.1 candidate. Nine focused tests pin both callers,
both outgoing calls, seven fixed global literals, all 13 false interior-word
candidates, the 20-byte list and 112-byte TCB seams, generic priority descent,
sentinel-skipping round robin, every stack-guard word, trace ordering/wrap,
and the assertion path. Apple and Linux emit 266-byte target functions with
only the expected stack-overflow-hook and interrupt-mask relocations.

This closes the bounded scheduler-selection and G2 external trace-ring
algorithms without changing production. Atomic kernel/port admission and
on-device preemption, stack-overflow, trace-concurrency, timer, and sleep
validation remain mandatory.

## LVGL Ambiq subtree provenance and global ABI are closed

The eleven linked `src/draw/ambiq` translation units are no longer an opaque
vendor-source family. Retained paths and line diagnostics identify exact Git
subtree `1e774257495fa43177e04fc5c8a42a77c2d7d619` in AmbiqMicro/LVGL. The
preferred default-branch commit is `5be8e0ae5077aa3880aba8a322b1487d6bc73c07`;
replay `67fd93e268f86b2ce90d4f1b14b53e36bf49ddd0` has identical subtree bytes,
so the historical commit object is deliberately left two-way ambiguous. The
next commit `6770071c…` is excluded by vector-font/letter line numbers.

Ambiq commits `d4dcd26b…` and `925470dd…` introduce and wire `clear_cb` and
`copy_cb`. Stock proves three 32-byte handler tables and all 24 callback
assignments. Combining that 24-byte ABI addition with
`LV_DRAW_SW_COMPLEX=0`, custom allocation, span, built-in object IDs, and the
previously recovered feature set reproduces `lv_global_t==0x1EC` and every
stock field offset. Six new provenance/compile tests and the existing LVGL
suite pass locally. The old unexplained 12-byte ABI delta is closed; the next
section records the now-identified Nema dependency and narrower production
gates.

## NemaGFX/NemaVG and Ambiq GPU dependency identity are closed

The hardware renderer below the recovered Ambiq LVGL subtree is now pinned to
an exact reproducible public package. The independent AmbiqSuite 5.1.0
revision `release_sdk5p1p0-634f7c117b` and Ambiq's public repository share the
same 50-file, 3,913,845-byte `NemaGFX_SDK` tree
`e690768a6e7b4d6a8d526fc75e8278a2764deff3`. Commit `b853fded…` is the first
public commit with that complete tree; `c6f54a95…` first publishes the exact
Apollo5 Nema archive and `e3eec7f3…` first publishes the exact GPU-patch
archive/header.

Stock calls the sectored-circular command-list API and retains its new error
token, independently forcing the NemaGFX 1.4.12 floor. The package supplies
NemaGFX 1.4.12 and NemaVG 1.1.8. Exact source/caller correlation maps nine
Nema command/power entries plus out-of-line Ambiq gradient and dash-line patch
bodies. It also recovers `LV_USE_DRAW_AMBIQ=1`, `LV_USE_AMBIQ_VG=1`, a
102,400-byte command list split into 100 x 1,024-byte sectors, and retained-
context GPU wake. Eight new tests authenticate stock spans, version evidence,
the 11-export/6-required GPU-patch census, manifest mutation rejection, and
the complete external SDK tree including one-byte negative mutation.

The public archives retain GCC 13.2.1 Cortex-M55 DWARF, while stock has IAR
code generation. Production therefore remains fail-closed on the original
IAR/private-source boundary, clean-room-candidate admission, stock
bare-metal HAL candidate admission, atomic integration, and Apollo510 hardware
validation. The third-party family, versions, public artifact origins, and
reproduction commit are no longer opaque.

## All 11 Ambiq GPU-patch functions are source-qualified

The exact 51,902-byte `gpu_patch.a` retains full per-function DWARF and
function sections. All 11 exports / 4,232 section bytes now have
production-excluded, independently named clean-room candidates. The
accessor sections are 16, 24, and 28 bytes at original source lines 301, 313,
and 326. Private DWARF fixes the paint (`0xE0`), path (`0x88`), vbuf (`0x60`),
bbox (`0x50`), and paint-texture (`0x30`) layouts.

Eight focused accessor tests pass, including the non-LUT branch that writes a
null palette, exact untransformed AABB selection, all four vbuf fields,
Cortex-M55 layout assertions, and relocation-free target bodies. The optional
full-SDK analyzer now parses GNU ar/ELF32 itself and authenticates these exact
sections. Seven more tests qualify the 144-byte public dash-line section and
138-byte stock IAR body, exact float truncation, and all Nema effects. All six
GPU-patch calls required by the recovered Ambiq LVGL subtree are thus
behaviorally source-transparent. A further six-test glyph candidate closes
one-to-four-byte decoding and the public 36-byte font-record lookup. Six shadow
tests pin odd/even margins, unequal horizontal/vertical sample counts, width-one
behavior, exact 668-byte section evidence, and relocation-free target output.
An exact Cortex-M55 emulation oracle plus seven tests close G2's two-stop
gradient boundary, including implicit endpoints, descending fallback,
equal-stop infinities, endpoint overwrites, and the 1,416-byte public/stock
bodies. Additional trace suites close the A8 corner mask, two-pass L8/L4
conversion, VG radial-shadow state restoration, and all four bitmap-glyph
rendering paths. No GPU-patch export remains binary-only; atomic HAL
integration, production admission, and hardware validation remain.

The adjacent stock Nema HAL is now separately closed as 18 contiguous
functions / 614 bytes at `[0x00513F34,0x0051419A)`. The exact IRQ-28 vector,
`0x40090000` register base, 1,000 ms semaphore wait, 100-command ring, three
heap descriptors, alignment/cache policy, and all 83 direct call sites are
authenticated. Public Ambiq history first exposes the related register-facing
Zephyr port on the package lineage at `4e7d4276…`; its blob and the later
`b853fded…` package port are exact provenance oracles, not claims of stock
source identity. A focused candidate/test suite closes the behavior while
leaving atomic board integration and hardware validation fail-closed.

## G2 BLE central-role and RingLink policy are object-closed

The retained `platform\ble\app_ble_central.c` path is no longer an opaque
first-party frontier item. Its initial 24 path anchors expand to a complete
44-function / 14,288-body-byte object at
`[0x0049F828,0x004A35B0)` (15,752 physical bytes). Twenty pathless functions
are admitted by Ghidra, direct-call, stored-pointer, prior-G2, and recursive
Thumb evidence; six bodies missed by the baseline sweep have pinned return and
literal-pool boundaries. The object owns scan/RPA selection, application events
`0xAE` through `0xB4`, seven RingLink states, retry escalation, dominant-hand
switching, unpair cleanup, and scene reconnect.

This is G2-local policy over already admitted Cordio DM/ATT/WSF providers, not
a remaining third-party source family. The prior G2 decompilation supplies 21
stable names and topology only; current bytes and boundaries are independently
authenticated, and the private producing commit remains unavailable. The
first-party retained-path frontier is now 71 closed / 163 open, with 389 closed
path anchors and 200,822 complete-object body bytes. Production routing remains
disabled.

## G2 BLE connection-parameter policy is object-closed

The retained `platform\ble\app_connect_params.c` path now owns the complete
`[0x00476CBC,0x004787A4)` object: 14 functions / 6,336 body bytes and eight
pool/alignment regions / 552 bytes, for 6,888 physical bytes. Ten bodies carry
the path directly; four externally rooted state/scheduling helpers preserve the
prior-G2 order. Thirty-nine direct entries, three stored `_connectParamReq`
pointers, 345 body calls, four source-path cells, both adjacent boundaries, and
all retained names are pinned. The two raw decodes to strict function interiors
are proven second-halfword artifacts within four-byte `sdiv`/`udiv`
instructions.

This is G2-local fast/slow connection policy over Cordio DM/WSF and the G2
event loop, not an additional third-party source dependency. The prior corpus
authenticates 14 stable names and one older-only log formatter but cannot reveal
the private producing commit. The aggregate retained-path frontier is now 72
closed / 162 open, with 399 closed anchors, 207,158 complete-object body bytes,
and 226,000 known physical bytes. Production routing remains disabled.

## G2 BLE peripheral-role policy is object-closed

The retained `platform\ble\app_ble_peripheral.c` object is now complete at
`[0x0046DB04,0x0046F4A4)`: 31 functions / 5,888 body bytes and 18 pool or
alignment regions / 672 bytes, for 6,560 physical bytes. Nineteen functions do
not carry the path themselves; seven of those were missing from baseline
Ghidra and are now admitted through direct-call or stored-pointer roots with
pinned returns. The complete graph has 44 direct entry sites, eight stored
Thumb pointers, 374 linked-image body calls, no strict-interior decode, and no
unrecovered direct target inside the object.

The object owns advertising payload/version policy, MTU and security handling,
events `0xAD`/`0xB5`/`0xB6`/`0xB7`, unpair and automatic restart, plus command
and left/right role decisions. Its external Cordio seam terminates at the
already admitted AmbiqSuite 2.5.1 application framework commit
`de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`; no additional opaque third-party
definition remains in this interval. The aggregate frontier is now 73 closed /
161 open, with 411 closed anchors, 213,046 complete-object body bytes, and
232,560 known physical bytes. Production routing remains disabled.

## G2 multipart transport protocol is object- and provider-closed

The retained
`platform\protocols\transport_protocol\transport_protocol.c` object is now
complete at `[0x004B892C,0x004B9A80)`: 13 functions / 4,134 body bytes plus
four literal/alignment regions / 302 bytes, for 4,436 physical bytes. The
310-byte `_rxNextPacketTimeout` body missed by baseline Ghidra is recovered
from its stored callback pointer and pinned return. The complete graph has 26
direct entry sites, two stored callbacks, 193 body calls, no strict-interior
decode, and no unrecovered direct target.

The dependency result is stronger than the earlier shorthand: this is a
separate G2 `0xAA` multipart protocol, not TinyFrame. Its only checksum target
is the already source-owned first-party CRC-16/CCITT-FALSE leaf at
`0x0049ACD4`, called three times. It has zero calls or stored pointers into the
authenticated TinyFrame object. Remaining upstream relationships terminate at
already admitted CMSIS-FreeRTOS v10.5.1 commit `d213f261…`, Packetcraft Cordio
WSF message definitions (exact from r19.02 `86372d84…`, selected oracle ceiling
r20.05c `3656312d…`), EasyLogger 2.2.99, and TLSF v3.1 behind G2 wrappers.
There is no opaque third-party definition inside the object.

The aggregate frontier is now 74 closed / 160 open, with 418 closed anchors,
217,180 complete-object body bytes, and 236,996 known physical bytes. See
`docs/research/g2-transport-protocol-recovery.md`. Production routing remains
disabled.

## G2 settings service is object- and provider-closed

The retained `platform\service\settings\service_settings.c` object is now
complete at `[0x0046B0EC,0x0046C73C)`: 31 functions / 5,146 body bytes plus
19 literal/alignment regions / 566 bytes, for 5,712 physical bytes. Eleven
functions missing from baseline Ghidra are recovered through recursive Thumb
decoding, direct ingress, and the stored battery callback. The closed graph has
117 direct entry sites, 340 in-image body calls, one stored Thumb pointer, no
strict-interior decode, and no unrecovered direct target. Two apparent
out-of-image calls are authenticated second-halfword artifacts inside `udiv`
and `mul` instructions.

The object owns settings/version synchronization, a 28-byte settings record
with CRC over 24 bytes, KV save checks, ALS Q10 persistence, brightness and
luminance conversion, auto-brightness, terminal mode, head-up control, and
battery status propagation. It embeds no third-party definition. Its upstream
edges terminate at exact CMSIS-FreeRTOS v10.5.1 commit `d213f261…`, EasyLogger
2.2.99-equivalent `cd93d9c…a596b264`, and the already known family-level IAR
DLIB boundary. The 13 IAR memory/string calls add no exact release or archive
discriminator, so EWARM 9.20+ / leading 9.60.2 remains the honest limit.

The aggregate retained-path frontier is now 75 closed / 159 open, with 431
closed anchors, 222,326 complete-object body bytes, and 242,708 known physical
bytes. See `docs/research/g2-service-settings-recovery.md`. Production routing
remains disabled.

## G2 tracepoint settings is object- and provider-closed

The retained `app\gui\tracepoint\tracepoint_setting.c` object is now complete
at `[0x005EDADC,0x005EF0B0)`: 21 functions / 5,100 body bytes plus eight
pool/alignment regions / 488 bytes, for 5,588 physical bytes. Four bodies
missing from baseline Ghidra are recursively recovered and complete delete-all,
BLE-command, and common-data dispatch. The graph has 42 direct entry sites,
294 body calls, one stored callback, no strict-interior decode, and no
unrecovered direct target.

The object owns `/log/tp`, `tp_%u.bin`, sorted left/right file inventory, and
protobuf heartbeat, file-list, delete-file, and delete-all policy. It embeds no
third-party definition. Its provider edges terminate at EasyLogger 2.2.99,
nanopb compatible with 0.4.7 through 0.4.9.1 (selected 0.4.9 commit
`98bf4db6…`), source-owned wrappers over littlefs v2.10.1 commit `0494ce71…`,
and the existing family-level IAR DLIB seam. Neither nanopb nor DLIB calls add
an exact stock-version discriminator.

The aggregate retained-path frontier is now 76 closed / 158 open, with 440
closed anchors, 227,426 complete-object body bytes, and 248,296 known physical
bytes. See `docs/research/g2-tracepoint-setting-recovery.md`. Production routing
remains disabled.

## G2 product RTOS hooks and Ambiq HAL lineage are closed

The retained `product\s200\app\config\rtos.c` object is complete at
`[0x0046D67C,0x0046D8A0)`: 13 functions / 512 body bytes and two pool/alignment
regions / 36 bytes, for 548 physical bytes. Its single path anchor expands to
the complete 32-slot task-vote policy plus pre-sleep, post-sleep, idle,
malloc-failed, and stack-overflow hooks. Nineteen direct entry sites, 24 body
calls, both adjacent boundaries, and the absence of stored/interior targets
are pinned.

This closure resolves a previously open vendor seam. The complete stock
`am_hal_sysctrl_sleep` provider contains two `WFI` operations. Official
Apollo510 HAL 5.0.0 commit `392042e3…` contains one, whereas 5.1.0 commit
`5efc0228…` contains the same two-stage internal-timer retry behavior as
stock. The embedded build time, `2025-04-28T13:29:15Z`, predates the public
5.1.0 import on 2025-08-14, so 5.1.0 is an exact source-lineage/replay result
but the actual private pre-release commit remains unavailable. The watchdog
restart source is compatible across both releases and supplies no independent
version discriminator.

The CMSIS current-task calls land on source-owned CMSIS-FreeRTOS v10.5.1
`osThreadGetId` at commit `d213f261…`; the IRQ primitive is already
source-owned; EasyLogger and IAR DLIB are known provider seams. No opaque
third-party definition remains in the object.

The aggregate retained-path frontier is now 77 closed / 157 open, with 441
closed anchors, 227,938 complete-object body bytes, and 248,844 known physical
bytes. See `docs/research/g2-product-rtos-recovery.md`. Production routing
remains disabled.

## G2 copied Goodix application-error utility is source-closed

The retained `utils\assert\util_error_check.c` object is complete at
`[0x00509B48,0x00509C1C)`: one 178-byte handler and 34 bytes of alignment and
literals, for 212 physical bytes. Its 103 external callers, eight provider
calls, single path pointer, adjacent boundaries, and absence of stored or
strict-interior entry targets are pinned.

The handler's out-of-line `[0x006C8E60,0x006C8FB8)` table has 43 exact Goodix
SDK rows / 344 bytes. The table strings, 512-byte automatic buffer, format
strings, and control flow select the byte-exact GR551x SDK 1.7.0
`app_error.c` blob `d5027735…`; SDK V1.00 has older wording and a 1,024-byte
buffer, while 2.0.1 and official 2.0.2 use 46 rows and a static buffer. The
selected `854c43e0…` commit is the earliest located public carrier, not an
official Goodix release or Even generating commit. The copied helper does not
prove that the Apollo image links a Goodix BLE stack.

The aggregate dependency ledger is corrected to 23 families / 22 selected
source commits or baselines, with no locally actionable bounded third-party
functional gap. The retained-path frontier is now 78 closed / 156 open, with
442 closed anchors, 228,116 complete-object body bytes, and 249,056 known
physical bytes. See
`docs/research/g2-util-error-check-goodix-recovery.md`. Production routing
remains disabled.

## G2 logger settings is recursively object- and provider-closed

The retained `app\gui\logger\logger_setting.c` path was not an 84-byte
micro-object. Its repeated path pointers and recursively recovered direct-call
roots close the full `[0x00458DF0,0x0045A558)` translation unit: eight
functions / 5,574 function-envelope bytes, including 5,466 reachable
instruction bytes and 108 embedded compiler-data bytes, plus 418 outer pool
bytes, for 5,992 physical bytes. Five functions were absent from baseline
Ghidra. The graph has nine direct entry sites, one stored callback, 346
reachable body calls, zero strict-interior BL decodes, and zero unrecovered
direct object targets.

The object owns BLE-log switch/level policy, a bounded 20-entry `/log`
inventory, single/all-file deletion, role-qualified `L:/log/` and `R:/log/`
validation, compressed-log filename simplification, nanopb command IDs
`0..2,4..6`, and peer events `0x0B/0x0C`. It embeds no third-party definition.
All 338 external calls terminate at admitted EasyLogger 2.2.99, nanopb
0.4.7–0.4.9.1, littlefs v2.10.1-backed wrappers, FreeRTOS V10.5.1, known IAR
DLIB primitives, and first-party routing seams. No dependency family or exact
version discriminator is added.

The retained-path frontier is now 79 closed / 155 open, with 443 closed
anchors, 233,690 complete-object body bytes, and 255,048 known physical bytes.
See `docs/research/g2-logger-setting-recovery.md`. Production routing remains
disabled.

## G2 UX system status is recursively object- and provider-closed

The retained `app\ux\ux_system\ux_system.c` path expands from one 88-byte
baseline anchor to a complete eleven-function object at
`[0x0047CE90,0x0047D9C4)`: 2,668 reachable instruction/body bytes and one
200-byte compiler pool, for 2,868 physical bytes. The recovered 2,232-byte
`UX_LocalSystemStatusSyncHandler` is rooted by the sole stored callback. The
graph has 51 exact-entry BL sites, 163 body calls, zero strict-interior BL
decodes, and zero unrecovered object targets.

The object owns six status messages and a packed state byte for self/peer OTA,
BLE, ring, and ring-MAC state. It embeds no third-party definition. Its 95
third-party calls are diagnostics into the admitted EasyLogger 2.2.99 source-
equivalent core at selected commit `a596b264…`; all other external calls are
bounded first-party providers. No family or version discriminator is added.

The retained-path frontier is now 80 closed / 154 open, with 444 closed
anchors, 236,358 complete-object body bytes, and 257,916 known physical bytes.
See `docs/research/g2-ux-system-recovery.md`. Production routing remains
disabled.

## G2 health mutex and common-event policy is object-closed

The retained `app\gui\health\health.c` path expands from one 94-byte baseline
anchor to four functions at `[0x004FFBD8,0x004FFE14)`: 504 reachable body bytes
plus a 68-byte terminal pool, for 572 physical bytes. Two baseline-missed
functions recover the lazy mutex initializer and stored
`Health_common_data_handler`. The graph has 58 exact-entry BL sites, one
stored callback, 34 body calls, and no interior or unrecovered target.

The mutex operations land exactly on the production-source-owned
CMSIS-FreeRTOS v10.5.1 `osMutexNew`, `osMutexAcquire`, and `osMutexRelease`
wrappers at commit `d213f261…`. EasyLogger accounts for 25 diagnostics; health
protobuf, role/display, and service-send behavior remains bounded first-party
policy. No third-party definition or new version discriminator is present.

The retained-path frontier is now 81 closed / 153 open, with 445 closed
anchors, 236,862 complete-object body bytes, and 258,488 known physical bytes.
See `docs/research/g2-health-recovery.md`. Production routing remains disabled.

## G2 quicklist mutex and common-event policy is object-closed

The neighboring `app\gui\quicklist\quicklist.c` path expands from one 94-byte
anchor to four functions / 310 body bytes plus a 50-byte pool, for 360 physical
bytes. Its recovered initializer and stored common-event callback complete 25
exact-entry BL sites, 22 body calls, and the no-interior/no-unknown closure.

The three mutex calls land on production-source-owned CMSIS-FreeRTOS v10.5.1
commit `d213f261…`; diagnostics land on admitted EasyLogger, and event parsing
stops at bounded first-party quicklist providers over admitted nanopb. No
third-party body or new version discriminator is present.

The retained-path frontier is now 82 closed / 152 open, with 446 closed
anchors, 237,172 complete-object body bytes, and 258,848 known physical bytes.
See `docs/research/g2-quicklist-recovery.md`. Production routing remains
disabled.

## G2 dashboard watchface manager is object- and provider-closed

The retained `app\gui\dashboard\dashboard_watchface_manager.c` path expands
from one 98-byte anchor to a complete 17-function object at
`[0x00500410,0x00500824)`: 956 reachable body bytes and an 88-byte terminal
pool, for 1,044 physical bytes. Eight functions missed by baseline Ghidra,
24 exact-entry BL sites, 34 direct calls, 15 register-indirect calls, one
stored selector pointer, and the adjacent boundaries are fail-closed.

Four 15-word operation tables implement watchface kinds 1 through 4 with
15, 15, 11, and nine non-null Thumb targets. Every indirect call therefore
terminates in pinned first-party watchface code. Thirty direct calls reach the
admitted EasyLogger 2.2.99-equivalent commit `a596b264…`; the only other
external direct call is a bounded first-party dashboard-state getter. No
third-party definition, CMSIS-FreeRTOS call, dependency family, or new version
discriminator is present.

The retained-path frontier is now 83 closed / 151 open, with 447 closed
anchors, 238,128 complete-object body bytes, and 259,892 known physical bytes.
See `docs/research/g2-dashboard-watchface-manager-recovery.md`. Production
routing remains disabled.

## G2 EvenAI text-stream service is recursively object-closed

The retained `app\gui\EvenAI\text_stream_service.c` path expands from one
116-byte capacity helper to `[0x00552B30,0x005537CC)`: 26 functions / 3,188
reachable body bytes plus three pools / 40 bytes, for 3,228 physical bytes.
Eighteen functions missed by baseline Ghidra include the 340-byte
`animate_text` timer callback, whose Thumb address is formed PC-relatively at
`0x00552FD0`. Sixty-five direct entry sites, 144 direct calls, seven indirect
caller-callback sites, and all adjacent boundaries are fail-closed.

The 48-byte service owns two initially 512-byte growable UTF-8 buffers and
emits one complete 1-, 2-, 3-, or 4-byte code point per 100-tick timer period.
All 113 external direct calls terminate at admitted CMSIS-FreeRTOS v10.5.1,
LVGL 9.3-compatible, nanopb, TLSF-wrapper, EasyLogger, IAR DLIB, or bounded
first-party generic-animation seams. No dependency family, hidden utility
body, or new exact-version discriminator is present.

The retained-path frontier is now 84 closed / 150 open, with 448 closed
anchors, 241,316 complete-object body bytes, and 263,120 known physical bytes.
See `docs/research/g2-text-stream-service-recovery.md`. Production routing
remains disabled.

## G2 terminal core is object- and provider-closed

The retained `app\gui\terminal\terminal.c` path expands from one 122-byte
display-request anchor to `[0x005E42EC,0x005E47CC)`: nine functions / 1,144
body bytes plus a 104-byte pool, for 1,248 physical bytes. Eight baseline-
missed functions recover the action mutex, display exit path, command
dispatcher, and three stored callbacks. The graph has 68 exact-entry BL sites,
73 body calls, no indirect body call, and no interior or unknown direct target.

The object role-gates eight-byte message `0x30`, normalizes six input event
IDs, and dispatches 13 terminal command IDs. Its utility edges are 30 admitted
EasyLogger calls, the exact CMSIS-FreeRTOS v10.5.1 mutex trio at `d213f261…`,
and three bounded IAR memory calls. The other 29 calls are first-party terminal
protobuf/UI providers. No hidden utility body, dependency family, or new
version discriminator is present.

The retained-path frontier is now 85 closed / 149 open, with 449 closed
anchors, 242,460 complete-object body bytes, and 264,368 known physical bytes.
See `docs/research/g2-terminal-core-recovery.md`. Production routing remains
disabled.

## G2 RTC driver utility/HAL provenance is exact and production-routed

The retained `driver\rtc\drv_rtc.c` path closes the complete 130-byte
`DRV_RtcSetTime` body and its 22-byte diagnostic pool, for 152 physical bytes.
The sole exterior caller, all 56 instructions, seven direct calls, adjacent
RTC initializer/getter boundaries, and absence of stored or interior entries
are pinned.

The two functional providers are exact AmbiqSuite sources:
`am_util_time_computeDayofWeek` from `utils/am_util_time.c` and
`am_hal_rtc_time_set` from the Apollo510 RTC HAL. The selected source replay is
SDK 5.1.0 revision `release_sdk5p1p0-366b80e084` at public commit
`5efc022…`; exact 5.0.0 and 5.1.0 source sizes, SHA-256 values, and Git blobs
are recorded. Their executable logic is unchanged across those releases, so
the separate two-WFI sleep proof remains the 5.1.0 discriminator.

OpenCFW already production-routes the stock wrapper to
`open_cfw_rtc_time_set`, whose source and existing host tests preserve the
calendar predicate, validation, BCD packing, RTC MMIO order, diagnostics, and
return convention. Remaining risk is Apollo510 hardware validation, not opaque
third-party functionality.

The retained-path frontier is now 86 closed / 148 open, with 450 closed
anchors, 242,590 complete-object body bytes, and 264,520 known physical bytes.
See `docs/research/g2-drv-rtc-recovery.md`.

## G2 teleprompt file-list storage is object-closed

The retained `app\gui\teleprompt\teleprompt_file_list.c` path expands from one
144-byte update anchor to three functions / 166 body bytes plus a 34-byte pool,
for 200 physical bytes. The two baseline-missed helpers return and zero the
global record. Six exterior entry sites, twelve body calls, both adjacent
retained-path boundaries, and the absence of stored or interior targets are
pinned.

The object owns one `0xF52`-byte record at `0x201093D4`: update copies the
complete record after a null guard, get returns the live address, and reset
zeros it. Its only providers are ten admitted EasyLogger calls and bounded IAR
`memcpy`/`memset`. No direct nanopb definition, dependency family, or version
discriminator appears. The object is not production-routed.

The retained-path frontier is now 87 closed / 147 open, with 451 closed
anchors, 242,756 complete-object body bytes, and 264,720 known physical bytes.
See `docs/research/g2-teleprompt-file-list-recovery.md`.

## G2 EvenAI tick timers are object-closed

The retained `app\gui\EvenAI\even_ai_timer.c` path expands from two anchors /
152 bytes to thirteen functions / 856 body bytes plus a 100-byte pool, for 956
physical bytes. Ten additional source-order bodies recover the common and
heartbeat start/check/process helpers and three aggregate wrappers. Twenty-eight
BL entries, all 57 body calls, both adjacent object boundaries, and the absence
of indirect/stored/interior targets are pinned.

Both timers are private 12-byte deadline records over wrap-safe unsigned tick
subtraction. They do not use CMSIS or FreeRTOS software timers. The only RTOS
dependency is four exact, already source-owned CMSIS-FreeRTOS v10.5.1
`osKernelGetTickCount` calls at commit `d213f261…`; 30 calls reach admitted
EasyLogger and one reaches bounded IAR `memset`. The remaining ten calls are
first-party role, sync, and EvenAI service policy. No opaque third-party code
or new commit discriminator remains, and the object is not production-routed.

The retained-path frontier is now 88 closed / 146 open, with 453 closed
anchors, 243,612 complete-object body bytes, and 265,676 known physical bytes.
See `docs/research/g2-even-ai-timer-recovery.md`.

## G2 BLE-status callback facade is object-closed

The retained `platform\service\callback_mgr\cb_ble_status.c` path closes as
three functions / 168 body bytes plus a 34-byte pool, for 202 physical bytes.
The two exact diagnostic-named register/unregister anchors are followed by a
pathless 14-byte notification dispatcher. Ten exterior BL entries, all 13
body calls, both adjacent boundaries, and the absence of indirect, stored, or
strict-interior targets are pinned.

Ten calls reach admitted EasyLogger and three reach first-party generic
callback-manager register, unregister, and invoke providers over the
`BLE_STATUS` list at `0x20073F6C`. There is no CMSIS-FreeRTOS, Cordio, IAR,
allocator, or protobuf edge, no embedded upstream body, and no new version
discriminator. The object is not production-routed.

The retained-path frontier is now 89 closed / 145 open, with 455 closed
anchors, 243,780 complete-object body bytes, and 265,878 known physical bytes.
See `docs/research/g2-cb-ble-status-recovery.md`.

## G2 Conversate menu page is object-closed

The single 218-byte `conversate_ui_menu_page.c` anchor expands to eight
functions / 1,492 body bytes plus a 100-byte pool, for 1,592 physical bytes.
Six baseline-missed source-order functions restore page creation, BLE/focus/UI
callbacks, styling, and scroll policy. Five stored callback pointers, seven BL
entries, 102 calls, and both boundaries are pinned.

The 101 external calls resolve to 35 admitted EasyLogger calls, 34 LVGL
9.3-compatible calls at selected commit `344c7c3…`, and 32 first-party
Conversate/animation/page providers. No opaque third-party definition or new
version discriminator remains. The object is not production-routed.

The retained-path frontier is now 90 closed / 144 open, with 456 closed
anchors, 245,272 complete-object body bytes, and 267,470 known physical bytes.
See `docs/research/g2-conversate-ui-menu-page-recovery.md`.

## G2 legal/regulatory UI is object-closed

The 234-byte event handler and 194-byte regional legal-content pool close at
428 physical bytes. Multi-entry compiler-shared diagnostic tails are pinned,
and the immediately following function is proven to belong to the separately
audited EasyLogger async sink. Ten EasyLogger, one LVGL, two IAR, and two
first-party calls exhaust the provider graph; no opaque third-party body or
new version discriminator remains.

The retained-path frontier is now 91 closed / 143 open, with 457 closed
anchors, 245,506 complete-object body bytes, and 267,898 known physical bytes.
See `docs/research/g2-legal-regulatory-recovery.md`.

## G2 Conversate tag page is object-closed

The single 238-byte `conversate_ui_tag_page.c` path anchor expands to eleven
functions / 2,910 body bytes plus a 146-byte pool, for 3,056 physical bytes.
Eleven stored callback pointers, three BL entries, one alternate interior
entry, 204 body calls, both neighboring boundaries, and zero indirect calls
are pinned directly against the authenticated stock image.

The 202 external calls resolve to 40 admitted EasyLogger diagnostics, 113 LVGL
9.3-compatible UI calls at selected commit `344c7c3…`, two exact
CMSIS-FreeRTOS v10.5.1 tick calls at selected commit `d213f26…`, four bounded
IAR DLIB clear/copy calls, and 43 first-party Conversate/UI providers. No
opaque third-party definition or new version discriminator remains. The
object is not production-routed.

The retained-path frontier is now 92 closed / 142 open, with 458 closed
anchors, 248,416 complete-object body bytes, and 270,954 known physical bytes.
See `docs/research/g2-conversate-ui-tag-page-recovery.md`.

## G2 exit prompt is object-closed

The two retained `exit_prompt.c` anchors / 276 bytes expand to five functions /
782 body bytes plus a 118-byte pool, for 900 physical bytes. Three missed
source-order callbacks restore the hold, fade-start, and show sequence.
Seventeen BL entries, three stored callback pointers, 56 calls, both adjacent
boundaries, and zero indirect or strict-interior targets are pinned.

The 53 external calls resolve to 35 admitted EasyLogger diagnostics, 15 LVGL
9.3-compatible animation/object calls at selected commit `344c7c3…`, and
three first-party `fade_anim.c` calls. No opaque utility definition or new
version discriminator remains. The object is not production-routed.

The retained-path frontier is now 93 closed / 141 open, with 460 closed
anchors, 249,198 complete-object body bytes, and 271,854 known physical bytes.
See `docs/research/g2-exit-prompt-recovery.md`.

## G2 eAT core is object-closed

The two path-anchored `at_core.c` bodies / 302 bytes expand to five functions /
666 body bytes plus a 58-byte pool, for 724 physical bytes. The closure pins
85 direct entries, 21 direct calls, four exact indirect callback sites, both
boundaries, and no stored or strict-interior entries.

The 20 external calls resolve to 10 admitted EasyLogger diagnostics, six
bounded/source-owned IAR DLIB memory/string/format calls, and four private eAT
parser calls. Exact `AT_CoreInit` / `AT_Handler` searches found no indexed
public implementation, so no third-party origin/version/commit is claimed.
The object is not production-routed.

The retained-path frontier is now 94 closed / 140 open, with 462 closed
anchors, 249,864 complete-object body bytes, and 272,578 known physical bytes.
See `docs/research/g2-at-core-recovery.md`.

## G2 HAL I2C is object-closed

The single 308-byte `hal_i2c.c` anchor expands to nine functions / 1,584 body
bytes plus a 40-byte pool, for 1,624 physical bytes. Thirty-five BL entries,
the exact vector-table ISR pointer, 65 body calls, both boundaries, and zero
indirect or strict-interior BL targets are pinned.

Twenty-one calls map to the Apollo510 GPIO/IOM API family in AmbiqSuite 5.1.0
public replay commit `5efc0228…`; 15 reach exact source-owned CMSIS-FreeRTOS
wrappers, and the rest stop at admitted EasyLogger/nanopb/IAR or first-party
delay seams. Hardware validation and production routing remain.

The retained-path frontier is now 95 closed / 139 open, with 463 closed
anchors, 251,448 complete-object body bytes, and 274,202 known physical bytes.
See `docs/research/g2-hal-i2c-recovery.md`.

## G2 ring-battery service is object-closed

The two path-anchored `service_ring_battery.c` bodies / 306 bytes expand to
five functions / 352 body bytes plus a 44-byte pool, for 396 physical bytes.
Nine direct entries, 19 body calls, three path-pointer references, both object
boundaries, and zero stored, indirect, or strict-interior entries are pinned.

Fifteen calls reach admitted EasyLogger, two reach bounded IAR `memset`, and
two reach private first-party service-record transport. Exact public searches
for the two retained `SVC_RingBattery_*` symbols and source path returned no
source. No opaque third-party definition or new version discriminator remains.

The retained-path frontier is now 96 closed / 138 open, with 465 closed
anchors, 251,800 complete-object body bytes, and 274,598 known physical bytes.
See `docs/research/g2-service-ring-battery-recovery.md`.

## G2 OPT3007 register map is object- and specification-closed

The single exact-symbol `ti_opt3007_assignRegistermap` body is 340 bytes plus
a 20-byte pointer pool, for 360 physical bytes. Two entries, five EasyLogger
calls, both boundaries, and the absence of stored, indirect, or strict-interior
entries are pinned.

The analyzer reconstructs all 57 output bytes from the stock instruction
stream. They form 19 register-field triples that exactly match TI's official
SBOS864 OPT3007 register map, including manufacturer/device ID registers
`0x7E` and `0x7F`. Exact public implementation searches found no source, so
the data origin is TI's August 2017 specification while the code remains
private G2 construction; no source commit is applicable.

The retained-path frontier is now 97 closed / 137 open, with 466 closed
anchors, 252,140 complete-object body bytes, and 274,958 known physical bytes.
See `docs/research/g2-opt3007-registers-recovery.md`.

## G2 codec UART-porting seam is object-closed

The two exact-symbol `uart_init` / `uart_close` bodies total 342 bytes plus a
72-byte pointer pool, for 414 physical bytes. Seven entries, 24 calls, four
path references, both boundaries, and zero stored, indirect, or strict-interior
targets are pinned.

Twenty calls reach admitted EasyLogger and three reach first-party UART3
lifecycle/callback service. The remaining call is the exact
production-source-owned AndersKaloer `ring_buffer_init`; it remains compatible
from `cda00e1…` through selected `190e30b…` and adds no narrower discriminator.
No opaque codec-vendor implementation occurs in this porting object.

The retained-path frontier is now 98 closed / 136 open, with 468 closed
anchors, 252,482 complete-object body bytes, and 275,372 known physical bytes.
See `docs/research/g2-service-codec-porting-recovery.md`.

## G2 notification thread is object-closed

Three path anchors / 374 bytes expand to eleven functions / 702 body bytes and
114 bytes in two pools, for 816 physical bytes. Two restored bodies are the
stored thread entry and packed creation callback. Nine BL entries, two stored
pointers, 56 calls, six path references, both boundaries, and zero indirect or
strict-interior targets are pinned.

Seven calls land on exact, production-source-owned CMSIS-FreeRTOS v10.5.1
thread, flags, delay, and queue wrappers at `d213f261…`. Thirty calls reach
admitted EasyLogger and eleven reach first-party state/record/whitelist policy.
No opaque utility body or new version discriminator remains.

The retained-path frontier is now 99 closed / 135 open, with 471 closed
anchors, 253,184 complete-object body bytes, and 276,188 known physical bytes.
See `docs/research/g2-thread-notification-recovery.md`.

## G2 GX8002B host driver is object- and provider-closed

Three path anchors / 424 bytes expand to twelve functions / 1,028 body bytes
plus a 144-byte pool, for 1,172 physical bytes. Three restored bodies are
CMSIS-Core NVIC helpers; the closure also recovers the stored I2S ISR, both I2S
lifecycle functions, the DMA-buffer/timestamp helper, and a stored audio-thread
callback. Eighteen BL entries, two stored pointers, 79 calls, nine raw path
references, both boundaries, and zero indirect or strict-interior targets are
pinned.

Thirteen calls map to twelve Apollo510 I2S APIs in AmbiqSuite 5.1.0 source file
`am_hal_i2s.c`, revision `release_sdk5p1p0-366b80e084`, at public replay
commit `5efc0228…`. The source is equivalent but the later public import cannot
be the historical private generating commit. NationalChip's GX8002B/LVP SDK is
an external device dependency and contributes no linked code to this object.
Four calls reach exact CMSIS-FreeRTOS `osDelay`, 45 reach admitted EasyLogger,
and 12 reach first-party board/audio providers.

The retained-path frontier is now 100 closed / 134 open, with 474 closed
anchors, 254,212 complete-object body bytes, and 277,360 known physical bytes.
See `docs/research/g2-drv-gx8002b-recovery.md`.

## G2 FlashDB service adapter is object- and provider-closed

Five path anchors / 462 bytes expand to eleven functions / 908 body bytes plus
a 132-byte pool, for 1,040 physical bytes. Two missed Ghidra functions and
four additional unanchored object members restore all four FAL callbacks,
three mutex functions, both blob wrappers, the database accessor, and service
initialization. Twenty-three BL entries, six stored callback pointers, 60
calls, nine raw path references, both boundaries, and zero indirect or
strict-interior targets are pinned.

Two calls map exactly to FlashDB 2.1.1 `fdb_kv_get_blob` and
`fdb_kv_set_blob` at authenticated source baseline `714d6159…`; seven calls
reach exact CMSIS-FreeRTOS v10.5.1 tick/mutex wrappers at `d213f261…`, and 45
reach admitted EasyLogger. The object embeds no third-party definition and
adds no historical-commit discriminator. It does prove a first-party safety
seam: stock FAL callbacks return zero on device failure while FlashDB maps only
negative callback results to errors. A writable OpenCFW port must use negative
error mapping and remain gated on golden-flash and non-destructive mount
validation.

The retained-path frontier is now 101 closed / 133 open, with 479 closed
anchors, 255,120 complete-object body bytes, and 278,400 known physical bytes.
See `docs/research/g2-service-db-api-recovery.md`.

## G2 EvenAI UI is object- and provider-closed

Two path anchors / 346 bytes expand to 43 functions / 8,004 function-interval
bytes / 8,424 physical bytes. The object includes 8,000 decoded instruction
bytes, 420 bytes in 15 outer pools, and one four-byte inline literal. Twenty-
eight missed functions restore text-stream lifecycle, scroll/layout caching,
dialog construction, input forwarding, automatic refresh, and page lifecycle.
The closure pins 131 BL entries, one stored callback, 512 calls, 21 path
references, every pool, both boundaries, and no strict-interior ingress.

All 413 external calls close over 182 admitted LVGL 9.3-compatible calls at
selected ceiling `344c7c31…`, 105 EasyLogger diagnostics, 22 bounded IAR DLIB
memory/string calls, one exact CMSIS-FreeRTOS v10.5.1 tick call, and 103
first-party EvenAI/UI providers. The audit composes the already closed
text-stream and timer objects. No third-party implementation or new version
discriminator is embedded; remaining work is first-party reconstruction and
target UI/lifecycle validation.

The retained-path frontier is now 102 closed / 132 open, with 481 closed
anchors, 263,124 complete-object body bytes, and 286,824 known physical bytes.
See `docs/research/g2-ui-even-ai-recovery.md`.

## G2 time service is object- and provider-closed

Two retained-path anchors / 438 bytes expand to eleven primary functions /
1,308 body bytes plus a 76-byte trailing pool, for 1,384 physical bytes. The
closure restores the missing leading epoch-to-calendar function and preserves
one externally called alternate compiler entry inside it without
double-counting the body. Sixty-four exact BL entry sites, six stored pointers,
45 direct body calls, both boundaries, and the retained path cell are pinned.

Eight external calls terminate at bounded IAR DLIB memory helpers and sixteen
at first-party RTC, configuration, transport, and logging providers. There are
no direct CMSIS-FreeRTOS calls and no embedded third-party definitions. The
object begins after the two alignment bytes following the already closed CMSIS
object, making the ownership boundary explicit rather than introducing a new
RTOS or utility gap.

The retained-path frontier is now 103 closed / 131 open, with 483 closed
anchors, 264,432 complete-object body bytes, and 288,208 known physical bytes.
See `docs/research/g2-service-time-recovery.md`.

## G2 audio thread is object- and provider-closed

Three retained-path anchors / 394 bytes expand to 31 functions / 2,954 body
bytes / 3,258 physical bytes. Nineteen restored functions recover thread and
resource initialization, queue dispatch, watchdog policy, codec/PDM handlers,
peer synchronization, and exit. The closure pins 1,101 instructions, 203
direct calls, 43 BL entries, three stored entries, 24 path references, all
pools and boundaries, and one bounded runtime callback dispatch.

Twenty calls terminate at fourteen exact CMSIS-FreeRTOS v10.5.1 wrappers from
`d213f261…`, with FreeRTOS-Kernel V10.5.1 `def7d2df…` and CMSIS_5 5.9.0
`2b7495b…` pinned as dependencies. One call is bounded IAR `memset`, 120 are
EasyLogger diagnostics, and nineteen compose the already closed codec DFU,
codec-host, and GX8002B objects. No third-party body or NationalChip LVP code
is embedded.

The retained-path frontier is now 104 closed / 130 open, with 486 closed
anchors, 267,386 complete-object body bytes, and 291,466 known physical bytes.
See `docs/research/g2-thread-audio-recovery.md`.

## G2 compact-log core is object- and provider-closed

Two retained-path anchors / 520 bytes expand to eight functions / 2,300
contiguous executable bytes. The closure restores the missing force-sync entry,
pins 898 instructions, 78 direct calls, 5,726 whole-image BL entries, six raw
path references, and zero indirect, stored-entry, or strict-interior ingress.
Twenty-three post-body literal cells are authenticated separately because
three EasyLogger accessors are interleaved between the body and its pool; no
physical-object byte total is overclaimed.

The high-volume entry at `0x0043CE9E` is now correctly classified as a
G2-private compact-record hook backed by a private 44-byte encoder, not as
upstream EasyLogger `elog_output`. The latter remains the separately admitted
G2-adapted body at `0x0043D574`, selected from EasyLogger commit `a596b264…`.
The core's external calls close over 13 bounded IAR DLIB calls, 30 EasyLogger
control/output calls, 14 FreeRTOS kernel/port calls, two exact CMSIS-FreeRTOS
tick calls, and eight first-party providers. It embeds no third-party body and
adds no version discriminator.

The retained-path frontier is now 105 closed / 129 open, with 488 closed
anchors, 269,686 complete-object body bytes, and 291,466 known physical bytes.
See `docs/research/g2-compress-log-core-recovery.md`.

## G2 compact-log port is object- and provider-closed

Three retained-path anchors / 680 bytes expand to twelve functions / 1,324
body bytes plus 140 bytes of modes, alignment, and pool data, for 1,464
physical bytes. The closure restores the stored export-timeout callback and
pins 526 instructions, 68 calls, 23 direct BL entries, one stored odd Thumb
entry, all data regions, both boundaries, and zero strict-interior or indirect
ingress.

The port owns a five-file ring with 512,000-byte files, a 12-byte manager
record with magic `0x4C4D4752`, a fixed firmware-version header, and a
120,000-tick export timeout. All eighteen file-runtime calls already reach
production source-owned OpenCFW wrappers over littlefs v2.10.1-equivalent
commit `0494ce71…`; all three delayed-callback calls are production source-
owned too. The remaining reusable seam is two bounded IAR `snprintf` calls.
No third-party body or new version discriminator is embedded.

The retained-path frontier is now 106 closed / 128 open, with 491 closed
anchors, 271,010 complete-object body bytes, and 292,930 known physical bytes.
See `docs/research/g2-compress-log-port-recovery.md`.

## G2 shared file runtime is path-, provider-, and production-closed

Five retained-path anchors / 746 bytes expand to eighteen functions / 2,266
executable bytes plus 138 bytes of alignment, file-mode literals, and pool
data, for 2,404 physical bytes. The closure pins 864 instructions, 132 calls,
644 whole-image BL entries, three stored entries, nine path references, both
boundaries, and zero indirect or strict-interior ingress.

All eighteen file, directory, synchronized-heap, and initialization entries
already have exact OpenCFW production redirects. Their provider graph closes
over 36 exact CMSIS-FreeRTOS mutex calls, fourteen first-party adapters over
littlefs v2.10.1-equivalent commit `0494ce71…`, three exact production TLSF
calls at `deff9ab5…`, six bounded IAR string calls, and already closed logging,
errno, and assertion seams. No third-party definition or new version
discriminator is embedded.

The retained-path frontier is now 107 closed / 127 open, with 496 closed
anchors, 273,276 complete-object body bytes, and 295,334 known physical bytes.
See `docs/research/g2-file-runtime-recovery.md`.

## G2 compact audio estimator is object- and provider-closed

Two retained-path anchors / 656 bytes expand to ten functions / 1,712 body
bytes plus 136 bytes of literal-pool data, for 1,848 physical bytes. The
closure pins 574 instructions, 43 direct calls, fifteen whole-image BL entries,
all boundaries and path references, and zero indirect, stored-entry, or
strict-interior ingress.

The first-party estimator consumes 800 interleaved signed-16 stereo frames,
forms ten rolling energy windows, searches relative lags from -10 through +10,
and converts the result to a signed angle. Its provider graph closes over ten
bounded IAR calls (`memset`, `asin`, signed-64-to-double, and `sqrt`), six calls
to a source-owned 64-bit division helper, and fifteen known logging calls. No
NationalChip LVP or other DSP-library body is linked and no new third-party
version discriminator exists. Compatibility work must account for a stock
hazard: aligned non-null input sizes below 3,200 bytes can pass validation even
though the algorithm unconditionally reads the complete 3,200-byte block.

The retained-path frontier is now 108 closed / 126 open, with 498 closed
anchors, 274,988 complete-object body bytes, and 297,182 known physical bytes.
See `docs/research/g2-service-algo-recovery.md`.

## G2 UART synchronization object is path- and provider-closed

Two retained-path anchors / 688 bytes expand to five functions / 758 body
bytes plus 114 bytes of shared pool data, for 872 physical bytes. Three helpers
are restored through adjacency, pool ownership, two stored Thumb pointers, and
whole-image ingress. The closure pins 297 instructions, 63 direct calls, four
direct BL entries, one bounded indirect call, both stored entries, all path
references, and zero strict-interior ingress.

The object creates one mutex, one event-flags object, and a 24,576-byte receive
stream. Its worker explicitly handles receive, send, and TinyFrame-tick bits;
receive dispatch uses 1,024-byte chunks with a 32-iteration / `0x7FFF` byte
guard. Reusable edges terminate at exact CMSIS-FreeRTOS v10.5.1, TinyFrame
`eb75483e…a29167a`, EasyLogger `a596b264…`, bounded IAR, and the first-party
UART adapter over the AmbiqSuite SDK 5.1.0 compatibility baseline `5efc0228…`.
No third-party body or new version discriminator is embedded. One initializer
through RAM slot `0x20000658` remains a bounded first-party runtime seam.

The retained-path frontier is now 109 closed / 125 open, with 500 closed
anchors, 275,746 complete-object body bytes, and 298,054 known physical bytes.
See `docs/research/g2-uart-sync-recovery.md`.

## G2 factory NV service is object- and FlashDB-closed

Two retained-path anchors / 882 bytes expand to five functions / 930 body
bytes plus 122 alignment/pool bytes, for 1,052 physical bytes. The closure
restores the database-index-one read/write wrappers and nine-node default-table
descriptor, then pins 379 instructions, 60 calls, twenty BL entries, eight path
references, both boundaries, and zero indirect, stored, or interior ingress.

Four calls reach the authenticated FlashDB 2.1.1 core at commit `714d6159…`,
nine reach first-party database-object adapters, two reach bounded IAR memory /
string helpers, and two reach first-party serial-number policy. No third-party
body is embedded. The recovered binding is `factory@NVdb`, external-flash
offset `0x01FF8000`, length `0x8000`, with nine explicit-length defaults and
magic `nvMagic=0x55550022`. Missing or mismatched magic performs wholesale
`fdb_kv_set_default`. The stock FAL zero-on-driver-failure hazard and destructive
reset policy remain explicit gates pending a read-only golden capture.

The retained-path frontier is now 110 closed / 124 open, with 502 closed
anchors, 276,676 complete-object body bytes, and 299,106 known physical bytes.
See `docs/research/g2-service-nvdb-recovery.md`.

## G2 production microphone test is object- and provider-closed

Five retained-path anchors / 646 bytes expand to six functions / 898 body
bytes plus 102 alignment/pool bytes, for 1,000 physical bytes. The missing
252-byte `production_pcm_callback_stereo` is restored through its exact symbol
string, path reference, stored odd Thumb pointer, complete disassembly, shared
pool, and boundary. The closure pins 359 instructions, 64 calls, eight BL
entries, both callback pointers, and zero indirect or interior ingress.

The stereo and single callbacks use bounded 400-byte scratch buffers and either
forward PCM directly or perform first-party channel extraction before dispatch.
Codec mode zero and PDM mode one share listener `0x10B` but retain distinct
power/unregister/cleanup paths. The only reusable calls are five bounded IAR
memory helpers and 35 known logging calls; 24 other edges are first-party audio
providers. No direct CMSIS-FreeRTOS, NationalChip LVP, or other DSP body is
linked.

The retained-path frontier is now 111 closed / 123 open, with 507 closed
anchors, 277,574 complete-object body bytes, and 300,106 known physical bytes.
See `docs/research/g2-production-mic-recovery.md`.

## G2 audio manager is object- and provider-closed

Four retained-path anchors / 984 bytes expand to seven functions / 1,554 body
bytes plus 174 alignment/pool bytes, for 1,728 physical bytes. The complete
410-byte peer-message handler and 132-byte initializer missing from Ghidra are
restored through exact symbols, retained-path references, contiguous boundaries,
internal topology, and ingress. The closure pins 595 instructions, 112 calls,
38 BL entries, one stored callback pointer, and zero indirect or interior
ingress.

The object owns an eight-slot application table, role-two first-acquire and
last-release hardware transitions, and a four-message one-byte peer handshake
on common-data frame `0x010C`. Eighty calls reach admitted logging, one reaches
bounded IAR `memset`, and twenty reach first-party product-role, audio-power,
and transport providers. No CMSIS-FreeRTOS, DSP, or other third-party body is
embedded and no new version discriminator exists.

The retained-path frontier is now 112 closed / 122 open, with 511 closed
anchors, 279,128 complete-object body bytes, and 301,834 known physical bytes.
See `docs/research/g2-service-audio-manager-recovery.md`.

## G2 system KVDB is object-closed and resolves the boot counter

Two retained-path anchors / 1,256 bytes expand to seven functions / 1,384 body
bytes plus 156 alignment/pool bytes, for 1,540 physical bytes. Five non-anchor
helpers close the database-zero blob adapters, twelve-node descriptor,
migration dispatcher, and magic invalidator. The closure pins 550 instructions,
88 direct calls, 32 BL entries, one bounded indirect site with eleven exact
targets, and zero stored or interior ingress.

The object composes exact FlashDB 2.1.1 commit `714d6159…`, twelve calls to the
closed G2 database adapters, the closed onboarding record, and eleven separately
closed first-party migration functions. The reset-called IAR zero scatter
proves `kvbooCount@0x20074988` starts at zero; initialization reads, increments,
and persists it. That former FlashDB residual is retired. Golden media, schema,
non-destructive mount policy, and the stock zero-on-driver-failure hazard remain
explicit production gates.

The retained-path frontier is now 122 closed / 112 open, with 538 closed
anchors, 299,774 complete-object body bytes, and 324,134 known physical bytes.
See `docs/research/g2-service-kvdb-recovery.md`.

The next closed seam is `app\ux\ux_battery_sync\ux_battery_sync.c`: one
836-byte `UX_BatterySyncHandler` body plus its 84-byte literal pool. The stored
callback table binds it to record `0x105`; the handler validates twelve-byte
messages and dispatches IDs 1..6 across already closed charger/ring-battery
providers. Forty-five EasyLogger calls are its only third-party edge, with no
new source/version discriminator. See
`docs/research/g2-ux-battery-sync-recovery.md`.

Following that callback edge closes the formerly zero-anchor
`platform\service\callback_mgr\cb_ring_battery.c` record as five functions /
122 body bytes / 152 physical bytes. Four bodies were missed by Ghidra; the
facade owns callback list `0x20073F90` and has only admitted EasyLogger plus
first-party provider calls. See
`docs/research/g2-cb-ring-battery-recovery.md`.

The zero-anchor `cb_charge.c` and `cb_msg_notif.c` siblings are now closed as
parallel five-function / 224-physical-byte facades. Their `BAT_INFO` and
`MSG_COUNT` lists use the same first-party generic callback ABI and admitted
EasyLogger source, with no RTOS or new third-party body. See
`docs/research/g2-callback-facades-recovery.md`.

The generic `callback_manager.c` provider is closed as eight functions / 1,240
body bytes / 1,360 physical bytes. Its only dynamic call is bounded by nodes
created through registration; all direct utility edges terminate at admitted
EasyLogger or production-source-owned TLSF heap wrappers. See
`docs/research/g2-callback-manager-recovery.md`.

`app\gui\Silent_Mode\silent_mode.c` expands from four anchors / 622 bytes to
ten functions / 2,488 body bytes / 2,696 physical bytes. Its 70 LVGL, 70
EasyLogger, one exact `vTaskDelay`, and one bounded IAR `memset` calls expose no
new dependency lineage; three stored callbacks and common-data record `0x10A`
are pinned. See `docs/research/g2-silent-mode-recovery.md`.

`app\gui\onboarding\onboarding_data_manager.c` closes as seven functions / 826
body bytes plus a 106-byte owned pool, for `[0x0047E2D0,0x0047E674)`. The two
pathless helpers own the mutex-protected three-byte process record and deferred
flag-update/event policy. Its reusable graph terminates at admitted EasyLogger,
exact CMSIS-FreeRTOS mutex/event wrappers, bounded IAR `memset`, the closed
FlashDB-backed onboarding KVDB leaf, and the closed nanopb-backed onboarding
encoder. No new dependency body, version discriminator, or generating commit
is exposed. See `docs/research/g2-onboarding-data-manager-recovery.md`.

The adjacent `app\gui\onboarding\onboarding.c` controller expands from four
anchors / 2,518 bytes to twelve functions / 4,136 body bytes / 4,476 physical
bytes. Five pre-anchor helpers and three stored callbacks close recursive LVGL
color transforms, common-data dispatch, BLE disconnect/reconnect state, and UI
lifecycle. Its 165 EasyLogger, 32 LVGL, exact `osMutexNew`, and two bounded IAR
calls terminate in already selected sources; all other reusable paths reach
the closed onboarding/KVDB/protobuf/callback objects. See
`docs/research/g2-onboarding-controller-recovery.md`.

`ui_onboarding_main_page.c` expands from seven anchors / 3,648 bytes to 52
functions / 9,234 body bytes / 9,776 physical bytes. Fifteen source-order
helpers and 17 stored pointers close its UI graph. All 453 external calls are
accounted for by selected LVGL, EasyLogger, CMSIS-FreeRTOS, mpaland, bounded IAR
DLIB, the closed onboarding protobuf service, or first-party sibling-page
policy. See `docs/research/g2-onboarding-main-page-recovery.md`.

`ui_onboarding_stock_page.c` expands from ten anchors / 6,624 bytes to 17
functions / 7,500 body bytes / 7,864 physical bytes. Its complete 629-call
graph terminates at selected LVGL and EasyLogger sources, exact
CMSIS-FreeRTOS mutex wrappers, bounded IAR DLIB, or already bounded first-party
onboarding/UI seams. No embedded third-party definition or new version
discriminator remains. The retained-path frontier is now 123 closed / 111
open, with 548 closed anchors, 307,274 complete-object body bytes, and 331,998
known physical bytes. See
`docs/research/g2-onboarding-stock-page-recovery.md`.

The onboarding family now also closes `ui_onboarding_news_page.c`: nineteen
anchors expand to 35 functions / 9,346 body bytes / 10,640 physical bytes.
Two raw interior-looking BL patterns are proven overlapping decodes inside
four-byte `uxtab` instructions, leaving zero qualified interior ingress. All
470 external calls terminate at selected LVGL/EasyLogger, exact
CMSIS-FreeRTOS mutex wrappers, bounded IAR DLIB, the routed ARM EABI division
helper, the closed time service, or bounded first-party providers. The frontier
is now 124 closed / 110 open, with 567 closed anchors, 316,620 complete-object
body bytes, and 342,638 known physical bytes. See
`docs/research/g2-onboarding-news-page-recovery.md`.

`app\gui\common\lvgl_font_manager.c` is now closed as eight functions / 2,590
body bytes / 2,972 physical bytes. The object confirms the two exact LVGL
FreeType adapter entries over FreeType 2.9.1 commit `86bc8a950…`, with all
other edges reaching admitted EasyLogger, bounded IAR DLIB, the closed MSPI
lock pair, or production-routed TLSF-backed heap wrappers. The frontier is now
125 closed / 109 open, with 574 closed anchors, 319,210 complete-object body
bytes, and 345,610 known physical bytes. See
`docs/research/g2-lvgl-font-manager-recovery.md`.

`app\gui\EvenHub\common_list_container.c` expands from six anchors / 6,746
bytes to fourteen functions / 7,342 body bytes / 8,588 physical bytes. Its two
indirect selection calls are bounded through both constructor sites to the
single `0x004949C0` callback. All 419 direct external calls terminate at
selected EasyLogger/LVGL sources, bounded IAR DLIB, production-routed
TLSF-backed heap wrappers, or bounded first-party providers. The frontier is
now 126 closed / 108 open, with 580 closed anchors, 326,552 complete-object
body bytes, and 354,198 known physical bytes. See
`docs/research/g2-common-list-container-recovery.md`.

`app\gui\EvenHub\common_text_container.c` expands from nine Ghidra anchors /
4,648 bytes to thirteen functions / 6,966 body bytes / 7,740 physical bytes.
Three missed functions restore 2,318 body bytes and two additional retained-
path anchors. All four indirect navigation calls resolve through both
constructor sites to the single `0x00494A78` `evenhub_ui.c` callback. All 426
direct external calls terminate at selected EasyLogger/LVGL sources, bounded
IAR DLIB, production-routed TLSF-backed heap wrappers, or bounded first-party
providers. The frontier is now 127 closed / 107 open, with 589 closed Ghidra
anchors, 333,518 complete-object body bytes, and 361,938 known physical bytes.
See `docs/research/g2-common-text-container-recovery.md`.

`app\gui\EvenHub\evenhub_ui.c` expands from nine anchors / 3,682 bytes to
26 functions / 14,296 body bytes / 15,568 physical bytes. Sixteen Ghidra-
missed functions recover the complete side-specific construction, parsing,
container, and callback surface. Both indirect sites are bounded to three
internal targets. All 823 direct external calls terminate at selected
EasyLogger/LVGL/nanopb sources, bounded IAR DLIB, production-routed
TLSF-backed heap wrappers, closed LZ4 adapters, or first-party providers. The
frontier is now 128 closed / 106 open, with 598 closed anchors, 347,814
complete-object body bytes, and 377,506 known physical bytes. See
`docs/research/g2-evenhub-ui-recovery.md`.

`app\gui\EvenHub\evenhub_data_parser.c` expands from twelve anchors / 8,136
bytes to nineteen functions / 10,336 executable bytes / 10,874 physical bytes.
Two Ghidra-missed functions and six inline table islands complete the parser
inventory. All 541 direct external calls terminate at selected EasyLogger,
nanopb, CMSIS-FreeRTOS, and LVGL sources; bounded IAR DLIB; production-routed
TLSF-backed heap wrappers; or first-party providers. There is no indirect
dispatch. The frontier is now 129 closed / 105 open, with 610 closed anchors,
358,150 complete-object body bytes, and 388,380 known physical bytes. See
`docs/research/g2-evenhub-data-parser-recovery.md`.

`framework\sync\sync_framework.c` expands from 23 retained-path anchors /
10,954 bytes to 43 functions / 16,816 executable bytes / 18,180 physical
bytes. Twenty missed callback and listener entries recover the generic
trampoline, two direct-entry synchronization functions, and ten TinyFrame
multipart handlers. All 1,051 external direct calls terminate at the admitted
EasyLogger, CMSIS-FreeRTOS, FreeRTOS, TinyFrame, AmbiqSuite, and nanopb
sources; bounded IAR DLIB; production-routed TLSF-backed heap wrappers; or
first-party providers. Fourteen indirect sites are bounded first-party
listener/callback seams. The frontier is now 130 closed / 104 open, with 633
closed anchors, 374,966 complete-object body bytes, and 406,560 known physical
bytes. See `docs/research/g2-sync-framework-recovery.md`.

The adjacent `framework\sync\sync_interface_api.c` is closed as thirteen
functions / 6,136 body bytes / 6,432 physical bytes. Its 333 external direct
calls terminate at admitted EasyLogger, CMSIS-FreeRTOS, and FreeRTOS sources;
bounded IAR DLIB; production-routed TLSF-backed heap wrappers; or the
first-party role provider. It has no indirect call or embedded third-party
definition. The frontier is now 131 closed / 103 open, with 646 closed
anchors, 381,102 complete-object body bytes, and 412,992 known physical bytes.
See `docs/research/g2-sync-interface-api-recovery.md`.

`framework\sync\display_thread.c` expands from fourteen anchors / 8,442
bytes to 27 functions / 9,100 body bytes / 9,834 physical bytes. Thirteen
restored functions include the already production-routed stored display
callback. All 522 external direct calls terminate at admitted EasyLogger,
CMSIS-FreeRTOS, FreeRTOS, and LVGL sources; bounded IAR DLIB; a production
runtime helper; or first-party providers. The main command loop and callback
are source-routed. The frontier is now 132 closed / 102 open, with 660 closed
anchors, 390,202 complete-object body bytes, and 422,826 known physical bytes.
See `docs/research/g2-display-thread-recovery.md`.

`driver\flash\drv_mx25u25643g.c` expands from 21 retained-path anchors /
5,420 bytes to forty functions / 6,726 body bytes / 7,360 physical bytes.
All 297 external calls terminate at admitted EasyLogger, AmbiqSuite Apollo510,
CMSIS-FreeRTOS, or shared-initializer sources; bounded IAR DLIB; or source-owned
runtime and delay providers. This reuses the selected AmbiqSuite `5efc0228…`,
CMSIS-FreeRTOS `d213f261…`, FreeRTOS-Kernel `def7d2df…`, and nanopb-compatible
`98bf4db6…` commits without introducing another dependency. The frontier is
now 133 closed / 101 open, with 681 closed anchors, 396,928 complete-object
body bytes, and 430,186 known physical bytes. See
`docs/research/g2-drv-mx25u25643g-recovery.md`.

`app\gui\MessageNotify\ui_msg_notif_list.c` expands from eighteen anchors /
5,392 bytes to fifty functions / 10,808 body bytes / 11,686 physical bytes.
Thirteen functions missed across the Ghidra shard boundary complete the UI
constructor, stored callbacks, and string helpers. All 599 external direct
calls terminate at selected EasyLogger, LVGL, CMSIS-FreeRTOS, and TLSF sources;
bounded IAR DLIB; or first-party providers. The frontier is now 134 closed /
100 open, with 699 closed anchors, 407,736 complete-object body bytes, and
441,872 known physical bytes. See
`docs/research/g2-ui-msg-notif-list-recovery.md`.

The misspelled stock `ui_DashBaord_Main_Screen.c` path expands from eight
anchors / 3,458 bytes to 31 functions / 9,040 body bytes / 9,896 physical
bytes. Its complete provider boundary reuses selected EasyLogger, LVGL, and
CMSIS-FreeRTOS sources plus bounded IAR and first-party dashboard widgets. The
audit distinguishes seven real interior callback pointers from six unaligned
word coincidences inside 32-bit instructions. The frontier is now 135 closed /
99 open, with 707 closed anchors, 416,776 complete-object body bytes, and
451,768 known physical bytes. See
`docs/research/g2-dashboard-main-screen-recovery.md`.

`app\gui\teleprompt\teleprompt_ui.c` expands from eight anchors / 3,034
bytes to 55 functions / 12,228 body bytes / 13,120 physical bytes. Thirty-eight
restored bodies complete the 4-by-19 mode/event table and screen/text/scroll
policy. All reusable calls terminate at selected EasyLogger and LVGL sources
or bounded IAR/first-party providers. The frontier is now 136 closed / 98
open, with 715 closed anchors, 429,004 complete-object body bytes, and 464,888
known physical bytes. See `docs/research/g2-teleprompt-ui-recovery.md`.

`platform\service\DFU\service_em9305_dfu.c` closes as seven functions /
2,802 body bytes / 2,826 physical bytes. Despite the filename it has zero
direct EM9305/Packetcraft vendor-code calls: all 152 external calls terminate
at selected EasyLogger, source-owned file/TLSF runtime, bounded IAR, the shared
zero initializer, or first-party DFU providers. The frontier is now 137 closed
/ 97 open, with 721 closed anchors, 431,806 complete-object body bytes, and
467,714 known physical bytes. See
`docs/research/g2-service-em9305-dfu-recovery.md`.

`app\gui\conversate\conversate_tag_data.c` expands from nine anchors /
2,562 bytes to twelve functions / 2,726 body bytes / 2,876 physical bytes. It
has no nanopb, JSON, or serialization-library edge; every external call is
EasyLogger, a production TLSF wrapper, or bounded IAR DLIB. The frontier is
now 138 closed / 96 open, with 730 closed anchors, 434,532 complete-object
body bytes, and 470,590 known physical bytes. See
`docs/research/g2-conversate-tag-data-recovery.md`.

`app\gui\dashboard\dashboard_watchface_layout4.c` expands from three anchors /
2,524 bytes to 23 functions / 4,184 body bytes / 4,606 physical bytes. The
audit corrects `0x005BBD10` from a false function start to object data and
recovers the stored MSPI cleanup callback at `0x005BBD48`. All reusable edges
terminate at selected EasyLogger, LVGL, and AmbiqSuite sources or bounded IAR
and first-party providers. The frontier is now 139 closed / 95 open, with 733
closed anchors, 438,716 complete-object body bytes, and 475,196 known physical
bytes. See `docs/research/g2-dashboard-watchface-layout4-recovery.md`.

`app\gui\dashboard\dashboard_ext.c` expands from six anchors / 2,498 bytes to
sixteen functions / 5,904 body bytes / 7,806 physical bytes. Ten restored
routines complete peer-role dashboard transfer, file lifecycle, protobuf
record handling, and resource lookup. Its dependencies are the already
selected EasyLogger, littlefs, nanopb, and FreeRTOS sources plus bounded IAR
and first-party providers. The frontier is now 140 closed / 94 open, with 739
closed anchors, 444,620 complete-object body bytes, and 483,002 known physical
bytes. See `docs/research/g2-dashboard-ext-recovery.md`.

`platform\protocols\dashboard_service\dashboard_data_process.c` expands from
seven anchors / 2,492 bytes to fourteen functions / 5,706 body bytes / 6,202
physical bytes. Four restored bodies and a separately pinned switch-dispatch
island close protobuf record processing and dashboard state policy. Its
reusable edges are the selected EasyLogger, nanopb, CMSIS-FreeRTOS, and
FreeRTOS sources plus bounded IAR providers. The frontier is now 141 closed /
93 open, with 746 closed anchors, 450,326 complete-object body bytes, and
489,204 known physical bytes. See
`docs/research/g2-dashboard-data-process-recovery.md`.

`platform\display_mgr\displaydrv_manager.c` expands from twelve anchors /
2,438 bytes to nineteen functions / 2,796 body bytes / 3,070 physical bytes.
Seven restored routines complete its lifecycle and stored callback set. All
external calls terminate at selected EasyLogger and CMSIS-FreeRTOS sources,
bounded IAR, or first-party ULED/thread/display providers; there are zero
direct LVGL or AmbiqSuite calls. The frontier is now 142 closed / 92 open, with
758 closed anchors, 453,122 complete-object body bytes, and 492,274 known
physical bytes. See `docs/research/g2-displaydrv-manager-recovery.md`.

`driver\npmx_driver_transplant\src\npmx_main_driver.c` expands from eleven
anchors / 2,290 bytes to thirty functions / 6,560 body bytes / 7,102 physical
bytes. Its 72 direct nPMX calls identify 42 linked Nordic entries. The stock
ADC result-register rewrite includes official commit `e1aaec53…`, while the
double-promoted logarithm excludes its adjacent successor `53de7af4…`, uniquely
selecting public state `v1.0.1-1-ge1aaec5`. A byte-identical 38-file compact
driver snapshot is now admitted. The frontier is 143 closed / 91 open, with
769 closed anchors, 459,682 complete-object body bytes, and 499,376 known
physical bytes. PMIC production routing remains gated on the nPM1300 ADK and
configuration, Apollo510 I2C/interrupt integration, G2 power policy, and
hardware validation. See `docs/research/g2-npmx-main-driver-recovery.md`.

`app\gui\navigation\navigation_data_handler.c` is now closed as 22 functions /
8,076 reachable code bytes / 8,556 physical bytes. The restored dispatcher
crosses a Ghidra shard boundary and contains two explicitly separated inline
literal pools. All 423 external calls terminate at admitted EasyLogger,
nanopb, CMSIS-FreeRTOS, bounded IAR/runtime, or first-party providers; no new
third-party implementation or version discriminator is present. The frontier
is now 144 closed / 90 open, with 776 closed anchors, 467,758 complete-object
body bytes, and 507,932 known physical bytes. See
`docs/research/g2-navigation-data-handler-recovery.md`.
### Google liblc3 source/version admission

The `platform\audio\service_audio.c` frontier exposed four linked public
Google liblc3 entries at `0x00590E64`, `0x00590F78`, `0x00591374`, and
`0x0059138A`, reached by five direct calls. Stock's SNS `FLT_MAX` fingerprint
proves commit `bb85f7d…` or later, while its encoder fields at offsets 0/1/2
exclude the `ltpf_bypass` layout introduced by `9f1e206…`. Official v1.1.3
commit `96a3af0…` is now the selected tagged baseline; the complete 38-file
Apache-2.0 source tree is admitted byte-identically under `third_party/liblc3`.
The linked surface cannot distinguish the spelling-only, dead-stripped change
at compatible successor `1de85e2…`, so the exact producing checkout remains
explicitly unclaimed. The focused verifier and four tests pass, and the
aggregate ledger now closes 25 families with 24 selected source baselines and
zero locally actionable third-party gaps. See
`docs/research/g2-liblc3-source-recovery.md`.

`platform\audio\service_audio.c` is now closed as fourteen functions / 2,676
body bytes / 2,884 physical bytes. All 104 external direct calls terminate at
admitted EasyLogger, CMSIS-FreeRTOS, Google liblc3, IAR, littlefs/file-runtime,
closed `service_algo`, or first-party notification providers. Its sole indirect
call is resolved through three static registrations to the two already closed
production-microphone callbacks at `0x0058F4E4` and `0x0058F5E0`. The next PDM
object begins at `0x0057B444`, preventing its inline CMSIS helpers from being
misclassified as audio literal data. The frontier is now 145 closed / 89 open,
with 783 closed anchors, 470,434 complete-object body bytes, and 510,816 known
physical bytes. See `docs/research/g2-service-audio-recovery.md`.

`driver\pdm\drv_pdm_production.c` is now closed as six functions / 610 body
bytes / 704 physical bytes despite having no baseline Ghidra path anchor. Its
13 HAL calls cover 12 public Apollo510 PDM APIs and independently select the
same AmbiqSuite 5.1.0 replay commit `5efc0228…`; the exact public
`am_hal_pdm.c` blob is `23a440bf…`. The object also contains three CMSIS-Core
NVIC helper definitions and no indirect or interior ingress. The frontier is
now 146 closed / 88 open, with 471,044 complete-object body bytes and 511,520
known physical bytes. See
`docs/research/g2-drv-pdm-production-recovery.md`.

The adjacent zero-anchor `driver\pdm\drv_pdm.c` object is now closed as seven
functions / 794 body bytes / 900 physical bytes. Startup cell `0x00438100`
proves its PDM0 IRQ handler, and 19 calls cover 14 APIs in the same exact
Apollo510 `am_hal_pdm.c` blob; interrupt service/status are the two APIs added
beyond the production wrapper. The frontier is now 147 closed / 87 open, with
471,838 complete-object body bytes and 512,420 known physical bytes. See
`docs/research/g2-drv-pdm-recovery.md`.

`platform\service\message_notify\service_ancc.c` is now closed as twelve
functions / 2,340 body bytes / 2,890 physical bytes. Its 129 external calls are
85 admitted EasyLogger, 17 exact CMSIS-FreeRTOS v10.5.1 mutex, ten bounded IAR,
and 17 closed first-party edges; it embeds and calls no Ambiq ANCC implementation
body. Three stored interior callbacks and six data-only pseudo-`BL` patterns are
explicitly pinned. The frontier is now 148 closed / 86 open, with 789 closed
anchors, 474,178 complete-object body bytes, and 515,310 known physical bytes.
See `docs/research/g2-service-ancc-dependency-boundary.md`.

`driver\sensor\als\als.c` is now closed as 38 functions / 3,858 body bytes /
4,232 physical bytes. Twenty-nine functions were restored beyond the nine path
anchors. Its reusable edges are admitted EasyLogger, exact CMSIS-FreeRTOS
v10.5.1 delay, bounded runtime, closed first-party policy, and six calls to the
clean-room TI OPT3007 adapter; no public OPT3007 software commit exists. One
stored callback and the bounded display-driver indirect dispatch are pinned,
and the apparent interior branch at `0x004AE09C` is an unaligned pseudo-`BL`.
The frontier is now 149 closed / 85 open, with 798 closed anchors, 478,036
complete-object body bytes, and 519,542 known physical bytes. See
`docs/research/g2-als-dependency-boundary.md`.

`platform\threads\thread_ble_production.c` is now closed as 14 functions /
2,140 body bytes / 2,368 physical bytes. A stored literal proves the previously
hidden task body at `0x005382E4`; two further restored bodies create and
terminate the CMSIS thread. The object makes 15 exact CMSIS-FreeRTOS v10.5.1
calls, three exact FreeRTOS V10.5.1 assertion-mask calls, and no embedded Cordio
calls. Its static task attributes, three-entry queue, three-block 0x104-byte
pool, production-frame header/checksum, all ingress, and two unaligned raw-value
lookalikes are pinned. The frontier is now 150 closed / 84 open, with 804 closed
anchors, 480,176 complete-object body bytes, and 521,910 known physical bytes.
See `docs/research/g2-thread-ble-production-dependency-boundary.md`.

`platform\product_test\pt_protocol_procsr.c` is now closed as 73 functions /
32,866 body bytes / 35,524 physical bytes. Sixty-nine retained-path anchors
expand through three pathless Ghidra functions and a hidden externally called
handler at `0x0056F92C`. The object's sole indirect call is bounded by a
66-entry aligned Thumb handler table. Its 1,526 external direct calls comprise
1,280 admitted EasyLogger calls, seven exact CMSIS-FreeRTOS v10.5.1 calls, one
exact FreeRTOS V10.5.1 `xTaskGetTickCount`, one selected mpaland printf call,
41 bounded IAR/runtime/fail-stop calls, and 196 first-party calls. No reusable
third-party body or new version discriminator is embedded. The frontier is now
151 closed / 83 open, with 873 closed anchors, 513,042 complete-object body
bytes, and 557,434 known physical bytes. See
`docs/research/g2-pt-protocol-procsr-dependency-boundary.md`.

`app\gui\quicklist\ui_quicklist_page.c` is now closed as 80 functions /
21,886 body bytes / 23,594 physical bytes. Seventeen functions were restored
beyond the 63-function Ghidra inventory, and fifteen aligned stored callbacks
plus 164 direct entry sites close whole-image ingress. Its 990 external calls
are 415 selected LVGL, 465 admitted EasyLogger, five exact CMSIS-FreeRTOS
`osKernelGetTickCount`, 24 bounded IAR runtime, and 81 first-party calls. It
embeds no reusable dependency body and adds no commit discriminator. The
frontier is now 152 closed / 82 open, with 916 closed anchors, 534,928
complete-object body bytes, and 581,028 known physical bytes. See
`docs/research/g2-ui-quicklist-page-dependency-boundary.md`.

`app\gui\dashboard\screens\ui_widget_news_page.c` is now closed as 45
functions / 19,058 body bytes / 20,668 physical bytes. Fourteen helpers were
restored beyond Ghidra, and 70 direct entry sites plus twelve stored callbacks
close ingress. Its 1,196 external calls are 508 selected LVGL, 565 admitted
EasyLogger, eight exact CMSIS-FreeRTOS mutex, 36 bounded IAR/EABI runtime, and
79 first-party calls. It embeds no reusable dependency body and adds no commit
discriminator. The frontier is now 153 closed / 81 open, with 938 closed
anchors, 553,986 complete-object body bytes, and 601,696 known physical bytes.
See `docs/research/g2-ui-widget-news-page-dependency-boundary.md`.

`app\gui\dashboard\screens\ui_stock_page.c` is now closed as 34 functions /
13,892 body bytes / 14,852 physical bytes. Two functions were restored beyond
Ghidra; 116 direct entry sites and two stored callbacks close ingress. Its 852
external calls are 454 selected LVGL, 355 admitted EasyLogger, ten bounded IAR
runtime, and 33 first-party calls. It has zero CMSIS-FreeRTOS/FreeRTOS calls,
embeds no reusable body, and adds no commit discriminator. The frontier is now
154 closed / 80 open, with 957 closed anchors, 567,878 complete-object body
bytes, and 616,548 known physical bytes. See
`docs/research/g2-ui-stock-page-dependency-boundary.md`.

`app\gui\navigation\navigation_ui.c` is now closed as 61 functions / 36,612
body bytes / 39,056 physical bytes. Twenty-nine entries were restored beyond
Ghidra; 152 direct entries, fourteen stored function starts, and five stored
shared-tail callback entries close ingress. Its 2,237 external calls are 702
selected LVGL, 1,245 admitted EasyLogger, twenty exact CMSIS-FreeRTOS mutex,
67 bounded IAR runtime, 22 admitted nanopb, two selected mpaland printf, and
179 first-party calls. It embeds no reusable dependency body and adds no
commit discriminator. The frontier is now 155 closed / 79 open, with 973
closed anchors, 604,490 complete-object body bytes, and 655,604 known physical
bytes. See `docs/research/g2-navigation-ui-dependency-boundary.md`.

`app\gui\menu\menu_page.c` is now closed as 34 functions / 13,906 body bytes /
15,066 physical bytes. Nine entries were restored beyond Ghidra; 98 direct
entries, eight stored function starts, and one stored shared interior entry
close ingress. Its 746 external calls are 124 selected LVGL, 445 admitted
EasyLogger, three exact CMSIS-FreeRTOS event/mutex, 24 bounded IAR runtime,
fifteen admitted nanopb, and 135 first-party calls. It embeds no reusable body
and adds no commit discriminator. The frontier is now 156 closed / 78 open,
with 987 closed anchors, 618,396 complete-object body bytes, and 670,670 known
physical bytes. See `docs/research/g2-menu-page-dependency-boundary.md`.

`app\gui\health\ui_health_page.c` is now closed as twelve functions / 9,414
body bytes / 10,054 physical bytes. One callback was restored beyond Ghidra;
nineteen direct entries and two stored pointers close ingress. Its 666 external
calls are 437 selected LVGL, 55 admitted EasyLogger, four bounded IAR, 36
selected mpaland printf, and 134 first-party calls; there are zero direct
CMSIS-FreeRTOS calls. The frontier is now 157 closed / 77 open, with 994 closed
anchors, 627,810 complete-object body bytes, and 680,724 known physical bytes.
See `docs/research/g2-ui-health-page-dependency-boundary.md`.

`platform\protocols\ring_service\ring_service.c` is now closed as eighteen
functions / 2,412 body bytes / 2,616 physical bytes. Its 121 external calls
terminate at admitted EasyLogger, CMSIS-FreeRTOS, nanopb, bounded IAR, or
first-party providers; there are zero direct Cordio calls. The frontier is now
158 closed / 76 open, with 1,003
closed anchors, 630,222 complete-object body bytes, and 683,340 known physical
bytes. See `docs/research/g2-ring-service-dependency-boundary.md`.

`platform\input\service_input_manager.c` is now closed as ten functions /
2,242 body bytes / 2,490 physical bytes. Five path anchors expand through five
adjacent helpers; 103 external calls terminate at admitted EasyLogger,
CMSIS-FreeRTOS, nanopb, bounded memory/runtime leaves, or first-party
input/event/timer/transport providers. It directly calls neither LVGL nor
Cordio. The frontier is now 159 closed / 75 open, with 1,008 closed anchors,
632,464 complete-object body bytes, and 685,830 known physical bytes. See
`docs/research/g2-service-input-manager-dependency-boundary.md`.

`app\gui\dashboard\screens\ui_calendar_page.c` is now closed as fifteen
functions / 9,690 body bytes / 10,172 physical bytes. Five path anchors expand
through seven additional Ghidra bodies and three restored functions. Its 722
external calls are 533 admitted LVGL, 85 admitted EasyLogger, 34 exact
CMSIS-FreeRTOS mutex, twelve bounded IAR/runtime, and 58 first-party calls.
The frontier is now 160 closed / 74 open, with 1,013 closed anchors, 642,154
complete-object body bytes, and 696,002 known physical bytes. See
`docs/research/g2-ui-calendar-page-dependency-boundary.md`.

`platform\protocols\ota_service\ota_transport.c` is now closed as three
functions / 2,004 body bytes / 2,292 physical bytes. Its 86 direct calls close
over EasyLogger, bounded IAR memory, the source-owned CRC and synchronized TLSF
wrappers, closed OTA-service policy, and three first-party event providers.
Four indirect sites use two registered first-party callback slots. The frontier
is now 161 closed / 73 open, with 1,015 closed anchors, 644,158 complete-object
body bytes, and 698,294 known physical bytes. See
`docs/research/g2-ota-transport-dependency-boundary.md`.

`platform\protocols\efs_service\efs_transport.c` is now closed as two
functions / 1,990 body bytes / 2,152 physical bytes. Its 87 direct calls close
over EasyLogger, one exact CMSIS-FreeRTOS tick wrapper, bounded IAR memory,
source-owned CRC/TLSF wrappers, closed EFS-service policy, and first-party
event providers. Four indirect sites use two registered callback slots. The
frontier is now 162 closed / 72 open, with 1,017 closed anchors, 646,148
complete-object body bytes, and 700,446 known physical bytes. See
`docs/research/g2-efs-transport-dependency-boundary.md`.

`app\gui\EvenHub\evenhub_loading_Page.c` is now closed as four functions /
2,042 body bytes / 2,328 physical bytes. Two path anchors expand through two
adjacent helpers, and the object boundary stops at the hidden first helper of
`evenhub_ui.c`. Its 137 external calls are 36 admitted LVGL, 85 admitted
EasyLogger, two bounded runtime, and fourteen first-party calls; two stored
function pointers close ingress. The frontier is now 163 closed / 71 open,
with 1,019 closed anchors, 648,190 complete-object body bytes, and 702,774
known physical bytes. See
`docs/research/g2-evenhub-loading-page-dependency-boundary.md`.

`app\gui\dashboard\dashboard_watchface_layout1.c` is now closed as nineteen
functions / 3,500 body bytes / 3,592 physical bytes. Ten callbacks and helpers
were restored beyond Ghidra; both indirect calls bind to two recovered local
callbacks. Its 215 external direct calls are 154 admitted LVGL, twenty
EasyLogger, thirteen bounded IAR, ten selected mpaland printf, and eighteen
first-party calls. The frontier is now 164 closed / 70 open, with 1,021 closed
anchors, 651,690 complete-object body bytes, and 706,366 known physical bytes.
See `docs/research/g2-dashboard-watchface-layout1-recovery.md`.

`app\gui\teleprompt\teleprompt_fsm.c` is now closed as fifteen functions /
2,994 body bytes / 3,302 physical bytes. Eight source-order handlers were
restored beyond Ghidra; one indirect dispatch is bounded to a nine-entry local
handler table. Its 172 external direct calls are 140 admitted EasyLogger,
three bounded IAR/runtime, one LVGL, two nanopb, and 26 first-party calls. The
frontier is now 165 closed / 69 open, with 1,024 closed anchors, 654,684
complete-object body bytes, and 709,668 known physical bytes. See
`docs/research/g2-teleprompt-fsm-dependency-boundary.md`.

`app\gui\health\health_data_manager.c` is now closed as ten functions / 2,644
body bytes / 2,912 physical bytes. One source-order parser was restored beyond
Ghidra. Its 136 external calls are 120 admitted EasyLogger, six bounded
IAR/runtime, and ten already closed health-lock calls; it has no direct RTOS
edge or hidden health/DSP library. The frontier is now 166 closed / 68 open,
with 1,029 closed anchors, 657,328 complete-object body bytes, and 712,580
known physical bytes. See
`docs/research/g2-health-data-manager-dependency-boundary.md`.

`app\gui\EvenHub\evenhub_main.c` is now closed as five functions / 3,130 body
bytes / 3,450 physical bytes. One source-order event routine was restored
beyond Ghidra. Its 180 external direct calls are 120 admitted EasyLogger, six
bounded IAR/EABI runtime, two LVGL, two exact CMSIS-FreeRTOS tick, three
nanopb, two production TLSF-wrapper, and 45 first-party calls. It embeds no
third-party implementation and adds no version discriminator. The frontier is
now 167 closed / 67 open, with 1,032 closed anchors, 660,458 complete-object
body bytes, and 716,030 known physical bytes. See
`docs/research/g2-evenhub-main-dependency-boundary.md`.

`app\gui\translate\translate.c` is now closed as eleven functions / 2,504
body bytes / 2,862 physical bytes. Two source-order handlers were restored
beyond Ghidra. Its 156 external calls terminate at admitted EasyLogger, LVGL,
CMSIS-FreeRTOS, and nanopb, bounded runtime, or first-party translate services.
The frontier is now 168 closed / 66 open, with 1,039 closed anchors, 662,962
complete-object body bytes, and 718,892 known physical bytes. See
`docs/research/g2-translate-dependency-boundary.md`.

`app\gui\teleprompt\teleprompt.c` is now closed as ten functions / 2,408 body
bytes / 3,900 physical bytes. Two event handlers were restored beyond Ghidra.
Its 149 external calls terminate at admitted EasyLogger, LVGL,
CMSIS-FreeRTOS, and nanopb, bounded runtime, or first-party teleprompt
providers. The frontier is now 169 closed / 65 open, with 1,046 closed
anchors, 665,370 complete-object body bytes, and 722,792 known physical bytes.
See `docs/research/g2-teleprompt-controller-dependency-boundary.md`.

`app\gui\conversate\conversate_comm_data.c` is now closed as twelve functions
/ 2,208 body bytes / 2,560 physical bytes. Its 72 external calls are sixty
EasyLogger, eleven bounded IAR memory, and one admitted LVGL text-measurement
call. The frontier is now 170 closed / 64 open, with 1,052 closed anchors,
667,578 complete-object body bytes, and 725,352 known physical bytes. See
`docs/research/g2-conversate-comm-data-dependency-boundary.md`.

`app\gui\dashboard\dashboard_watchface_layout3.c` is now closed as nineteen
functions / 3,254 body bytes / 3,648 physical bytes. Seven source-order
callbacks and helpers were restored beyond Ghidra. Its 173 external calls are
125 admitted LVGL, twenty EasyLogger, ten bounded IAR, two selected mpaland
printf, and sixteen first-party calls. Five raw apparent Thumb calls are the
second halfwords of pinned four-byte `sdiv` instructions. The frontier is now
171 closed / 63 open, with 1,053 closed anchors, 670,832 complete-object body
bytes, and 729,000 known physical bytes. See
`docs/research/g2-dashboard-watchface-layout3-recovery.md`.

`platform\threads\thread_ring.c` is now closed as seventeen functions / 2,374
body bytes / 2,632 physical bytes. Twelve source-order functions were restored,
including the CMSIS thread entry at `0x004C4CEC`; this corrects the preceding
BLE Ring-profile boundary by removing 120 bytes formerly classified as
noncode. Its 162 external calls are 110 EasyLogger, ten exact CMSIS-FreeRTOS,
two bounded FreeRTOS assert, two IAR, three production TLSF-wrapper, thirteen
closed Ring-service, sixteen event-loop, and six other first-party calls. The
frontier is now 172 closed / 62 open, with 1,058 closed anchors, 673,206
complete-object body bytes, and 731,512 known physical bytes. See
`docs/research/g2-thread-ring-dependency-boundary.md`.

`framework\fw_event_loop\fw_event_loop.c` is now closed as six functions /
1,806 body bytes / 2,012 physical bytes. The 108-byte worker missed by Ghidra
completes the object. Its 104 external direct calls are eighty admitted
EasyLogger, twenty exact CMSIS-FreeRTOS, and four exact FreeRTOS critical-port
calls; one indirect call invokes a callback dequeued in a bounded event record.
All six functions were already production-routed to the clean-room event-loop
source. The frontier is now 173 closed / 61 open, with 1,063 closed anchors,
675,012 complete-object body bytes, and 733,524 known physical bytes. See
`docs/research/g2-fw-event-loop-dependency-boundary.md`.

`platform\protocols\ring_service\ring_connect_policy.c` is now closed as
fifteen functions / 1,828 body bytes / 2,056 physical bytes. The true object
starts 60 bytes before its first retained-path anchor with three pathless
tick/timeout helpers; the stored `_ringReconnectTimeoutFire` callback supplies
the fourth restoration. Its 108 external calls are 95 admitted EasyLogger,
one exact CMSIS-FreeRTOS tick wrapper, ten closed event-loop, one closed
nanopb-facade, and one closed BLE-central call, with no direct Cordio or nanopb
edge. The frontier is now 174 closed / 60 open, with 1,074 closed anchors,
676,840 complete-object body bytes, and 735,580 known physical bytes. See
`docs/research/g2-ring-connect-policy-dependency-boundary.md`.

`app\gui\SystemClose\systemClose.c` is now closed as twenty functions / 4,960
body bytes / 5,368 physical bytes. Fifteen functions missed by Ghidra restore
the event FIFO, common-data/page handlers, selection animation, option builder,
reflash dispatch, and display lifecycle. The final 282-byte UI handler corrects
the old service-settings neighbor pin that had classified it as literal pool.
Its 271 external calls are 130 EasyLogger, 99 admitted LVGL, five bounded IAR,
and 37 first-party display/sync calls, with no CMSIS-FreeRTOS or new utility.
The frontier is now 175 closed / 59 open, with 1,079 closed anchors, 681,800
complete-object body bytes, and 740,948 known physical bytes. See
`docs/research/g2-system-close-dependency-boundary.md`.

The Translate-UI predecessor gap is now identified and functionally closed as
IAR DLIB `frexpf`, its binary32 decomposition helper, and `ldexpf`: three exact
bodies / 268 bytes at `[0x0059D244,0x0059D350)`. Selector-isolated clean-room
assembly reproduces the authenticated stock bytes after the two relocations,
and 12,000 differential executions pass. All three entries are guarded and
canonical-Apple production-routed; Linux remains excluded until its reviewed
Clang 22.1.8 environment records independent pins. The historical IAR release
and archive variant remain externally gated. See
`docs/research/iar-dlib-frexpf-ldexpf-recovery.md`.

`app\gui\translate\translate_ui.c` is now closed as 29 functions / 5,288
body bytes / 5,730 physical bytes. Twenty-two source-order or stored callbacks
were restored beyond its seven Ghidra anchors. Its 346 external direct calls
are 175 EasyLogger, 125 LVGL, ten bounded IAR DLIB, two exact
CMSIS-FreeRTOS, and 34 first-party edges; the single indirect callback is
record-bounded. It embeds no reusable implementation and adds no provenance
discriminator. See
`docs/research/g2-translate-ui-dependency-boundary.md`.

`app\gui\conversate\conversate.c` is now closed as twelve functions / 2,250
body bytes / 2,628 physical bytes. Three bodies were restored beyond its nine
Ghidra anchors. All 139 external calls terminate at selected EasyLogger,
CMSIS-FreeRTOS, LVGL, nanopb, bounded IAR/EABI, CmBacktrace, or first-party
providers. The vector-referenced CmBacktrace edge corroborates the existing
`4abadfa0…73714489` compatibility interval and OpenCFW's selected `73714489`
snapshot, but does not prove Even's historical commit. The frontier is now 177
closed / 57 open, with 1,095 closed anchors, 689,338 complete-object body bytes,
and 749,306 known physical bytes. See
`docs/research/g2-conversate-controller-dependency-boundary.md`.

`app\gui\EvenHub\common_image_container.c` is now closed as three functions /
1,554 body bytes / 1,834 physical bytes. Its 80 external calls terminate at
selected EasyLogger/LVGL, production TLSF-backed free and Apollo510 cache-clean
providers, one bounded absolute-value helper, or two first-party seams. It adds
no dependency or commit discriminator. The frontier advances again to 178
closed / 56 open and 450,446 closed anchored bytes. See
`docs/research/g2-common-image-container-dependency-boundary.md`.

`dashboard_watchface_layout2.c` is now closed as nineteen functions / 2,844
body bytes / 3,076 physical bytes, including thirteen source-order bodies
restored beyond its single anchor. Its 181 external calls terminate at selected
EasyLogger, LVGL, mpaland printf, bounded IAR, or first-party dashboard
providers. The frontier is now 179 closed / 55 open and 93.13% of anchored
bytes are closed. See
`docs/research/g2-dashboard-watchface-layout2-recovery.md`.

`app\gui\conversate\conversate_ui_main_page.c` is now closed as fifteen
functions / 4,132 body bytes / 4,492 physical bytes. Eleven source-order
routines were restored beyond Ghidra's four entries. One stored callback enters
the authenticated `0x005B305C` continuation of the large UI-construction
routine; it is pinned as an alternate interior entry, not double-counted as an
overlapping function. All 283 external calls terminate at selected EasyLogger
and LVGL, bounded/source-recreated IAR `snprintf`, or first-party conversate
providers. The frontier is now 180 closed / 54 open and 93.43% of anchored
bytes are closed. See
`docs/research/g2-conversate-ui-main-page-recovery.md`.

`platform\service\service_universal_setting\service_universal_setting.c`
is now closed as fifteen functions / 2,010 body bytes / 2,156 physical bytes.
Ten bodies missed by Ghidra restore the live-record helpers and six field
getters. Its 103 external calls terminate at selected EasyLogger, bounded IAR
memory primitives, the production source-owned CCITT-FALSE leaf, already
closed KV record writers, or first-party role/sync/scheduling providers. It
adds no dependency or commit discriminator. The frontier is now 181 closed /
53 open and 93.73% of anchored bytes are closed. See
`docs/research/g2-service-universal-setting-recovery.md`.

## G2 retained-path frontier closes completely

`app\gui\conversate\conversate_pb_msg_handler.c` is now closed as 15
functions / 3,440 body bytes / 3,764 physical bytes. All 214 external direct
calls terminate at admitted EasyLogger, bounded IAR, LVGL, and nanopb edges,
and its single indirect call is bounded. It embeds no reusable implementation.
The frontier is now 182 closed / 52 open. See
`docs/research/g2-conversate-pb-msg-handler-dependency-boundary.md`.

`app\gui\quicklist\quicklist_data_manager.c` is now closed as three functions
/ 1,350 body bytes / 1,480 physical bytes. Its 67 external calls terminate at
admitted EasyLogger, bounded IAR, and first-party leaf edges only, with no
embedded reusable implementation. The frontier is now 183 closed / 51 open.
See `docs/research/g2-quicklist-data-manager-dependency-boundary.md`.

`app\gui\EvenAI\even_ai_animation.c` is now closed as five functions / 2,036
body bytes / 2,228 physical bytes. Its 79 external calls terminate at admitted
EasyLogger, bounded IAR, and LVGL edges plus one exact CMSIS-FreeRTOS seam,
with no embedded reusable implementation. The frontier is now 184 closed /
50 open. See `docs/research/g2-even-ai-animation-dependency-boundary.md`.

`app\gui\onboarding\onboarding_animation.c` is now closed as eleven functions
/ 1,598 body bytes / 2,004 physical bytes. Its 80 external calls terminate at
admitted EasyLogger, bounded IAR, LVGL, and nanopb edges plus production
source-owned TLSF heap wrappers. The frontier is now 185 closed / 49 open.
See `docs/research/g2-onboarding-animation-dependency-boundary.md`.

`platform\threads\thread_manager.c` is now closed as 17 functions / 1,934
body bytes / 2,172 physical bytes. Its 30 exact CMSIS-FreeRTOS v10.5.1 calls
span twelve distinct osXxx APIs (osKernelInitialize/Start/GetTickCount,
osThreadNew/GetId/SetPriority/Terminate, osThreadFlagsSet/Wait, and
osEventFlagsNew/Set/Wait); remaining edges are admitted EasyLogger, the
FreeRTOS assert port, the littlefs port, and closed or bounded first-party
providers, with no IAR DLIB edge. The frontier is now 186 closed / 48 open.
See `docs/research/g2-thread-manager-dependency-boundary.md`.

`driver\touch\drv_cy8c4046fni.c` is now closed as 23 functions / 1,754 body
bytes / 1,924 physical bytes. Its edges are admitted EasyLogger, exact
CMSIS-FreeRTOS osDelay, the closed HAL I2C provider, and bounded IAR DLIB.
No public Cypress or Infineon host-side I2C driver source candidate exists,
so the object is documented as Even private first-party with negative
provenance. The frontier is now 187 closed / 47 open. See
`docs/research/g2-drv-cy8c4046fni-dependency-boundary.md`.

`framework\sync\thread_pool.c` is now closed as three functions / 1,290 body
bytes / 1,452 physical bytes. Its 78 external calls terminate at admitted
EasyLogger, exact CMSIS-FreeRTOS, the FreeRTOS assert port, and bounded IAR
DLIB, with zero first-party call edges. The frontier is now 188 closed /
46 open. See `docs/research/g2-thread-pool-dependency-boundary.md`.

`framework\page_manager\page_manager.c` is now closed as 45 functions /
4,510 body bytes / 4,656 physical bytes. Its 139 external calls terminate at
admitted EasyLogger and LVGL, TLSF-backed heap wrappers, closed first-party
providers, and bounded IAR DLIB. The frontier is now 189 closed / 45 open.
See `docs/research/g2-page-manager-dependency-boundary.md`.

`app\ux\ux_wear_detect\ux_wear_detect.c` is now closed as seven functions /
1,236 body bytes / 1,352 physical bytes. Its 71 external calls terminate at
admitted EasyLogger, bounded IAR, and nanopb edges; CMSIS-FreeRTOS
osKernelGetTickCount is the sole RTOS seam. The frontier is now 190 closed /
44 open. See `docs/research/g2-ux-wear-detect-dependency-boundary.md`.

`app\gui\anim\fade_anim.c` is now closed as eleven functions / 1,678 body
bytes / 1,802 physical bytes. Its 89 external calls terminate at admitted
EasyLogger and LVGL 9.3-compatible edges only, with no RTOS seam. The
frontier is now 191 closed / 43 open. See
`docs/research/g2-fade-anim-dependency-boundary.md`.

`app\gui\anim\list_anim.c` is now closed as eleven functions / 1,348 body
bytes / 1,460 physical bytes. Its 73 external calls terminate at admitted
EasyLogger, bounded IAR, and LVGL edges; CMSIS-FreeRTOS osKernelGetTickCount
is the sole RTOS seam. The frontier is now 192 closed / 42 open. See
`docs/research/g2-list-anim-dependency-boundary.md`.

`app\gui\common\generic_animation.c` is now closed as 17 functions / 1,622
body bytes / 1,736 physical bytes. Its 80 external calls terminate at admitted
EasyLogger, bounded IAR, and LVGL edges plus production source-owned TLSF
heap wrappers; CMSIS-FreeRTOS osKernelGetTickCount is the sole RTOS seam.
The frontier is now 193 closed / 41 open. See
`docs/research/g2-generic-animation-dependency-boundary.md`.

`app\gui\conversate\conversate_timer_mgr.c` is now closed as 24 functions /
2,204 body bytes / 2,440 physical bytes. Its 102 external calls terminate at
admitted EasyLogger, the exact CMSIS-FreeRTOS tick wrapper, and closed
first-party providers. The frontier is now 194 closed / 40 open. See
`docs/research/g2-conversate-timer-mgr-dependency-boundary.md`.

`app\gui\conversate\conversate_ui_prep_note_page.c` is now closed as 16
functions / 3,114 body bytes / 3,248 physical bytes. Its 188 external calls
terminate at admitted EasyLogger, bounded IAR, LVGL, and closed first-party
conversate providers. The frontier is now 195 closed / 39 open. See
`docs/research/g2-conversate-ui-prep-note-page-dependency-boundary.md`.

`app\gui\teleprompt\teleprompt_timer_mgr.c` is now closed as 13 functions /
1,498 body bytes / 1,660 physical bytes. Its 65 external calls terminate at
admitted EasyLogger, the exact CMSIS-FreeRTOS tick wrapper, and closed
first-party providers. The frontier is now 196 closed / 38 open. See
`docs/research/g2-teleprompt-timer-mgr-dependency-boundary.md`.

`app\gui\conversate\conversate_ui.c` is now closed as 23 functions / 3,774
body bytes / 4,084 physical bytes. Its 221 external calls terminate at
admitted EasyLogger, bounded IAR, LVGL, and closed first-party conversate
providers. The frontier is now 197 closed / 37 open. See
`docs/research/g2-conversate-ui-dependency-boundary.md`.

`app\gui\dashboard\page_state_sync.c` is now closed as eight functions /
1,244 body bytes / 1,380 physical bytes. Its 57 external calls terminate at
admitted EasyLogger, IAR DLIB, and nanopb edges only. The frontier is now
198 closed / 36 open. See
`docs/research/g2-page-state-sync-dependency-boundary.md`.

`app\gui\translate\translate_fsm.c` is now closed as eight functions / 1,304
body bytes / 1,448 physical bytes. Its single indirect `blx` is bounded by
the stored six-entry state-handler table; all 86 external direct calls
terminate at admitted EasyLogger, IAR DLIB, and nanopb edges. The frontier
is now 199 closed / 35 open. See
`docs/research/g2-translate-fsm-dependency-boundary.md`.

`platform\service\box_detect\service_box_detect.c` is now closed as 32
functions / 3,564 body bytes / 3,912 physical bytes. Its thirteen exact
CMSIS-FreeRTOS timer calls span osTimerNew/Start/Stop/IsRunning/Delete;
remaining edges are admitted EasyLogger and IAR DLIB only. The frontier is
now 200 closed / 34 open. See
`docs/research/g2-service-box-detect-dependency-boundary.md`.

`app\gui\module_configure\general_configure.c` is now closed as ten
functions / 2,376 body bytes / 2,616 physical bytes. Its 141 external calls
terminate at admitted EasyLogger, IAR DLIB, CMSIS-FreeRTOS event flags, and
nanopb edges only. The frontier is now 201 closed / 33 open. See
`docs/research/g2-general-configure-dependency-boundary.md`.

`app\gui\terminal\terminal_data.c` is now closed as 44 functions / 2,902
body bytes / 3,012 physical bytes. Its 45 external calls terminate at
admitted EasyLogger and IAR DLIB edges plus the closed time-service provider.
The frontier is now 202 closed / 32 open. See
`docs/research/g2-terminal-data-dependency-boundary.md`.

`platform\sensor_hub\sensor_hub.c` is now closed as 31 functions / 4,026
body bytes / 4,408 physical bytes. Its nine distinct exact CMSIS-FreeRTOS
v10.5.1 wrappers cover osKernelGetTickCount, osThreadNew/Terminate,
osTimerNew/Start/Stop, and osMessageQueueNew/Put/Get; remaining edges are
admitted EasyLogger, LVGL, a nanopb seam, and closed or bounded first-party
providers. Explicit negative evidence records no embedded sensor-fusion
library body. The frontier is now 203 closed / 31 open. See
`docs/research/g2-sensor-hub-dependency-boundary.md`.

`platform\threads\thread_input.c` is now closed as 23 functions / 2,090
body bytes / 2,296 physical bytes. Its ten exact CMSIS-FreeRTOS v10.5.1
calls span osThreadNew/Terminate, osThreadFlagsSet/Wait, osDelay, and
osMessageQueueNew/Put/Get/Delete; remaining edges are admitted EasyLogger,
IAR DLIB, a source-owned runtime wrapper, and closed or bounded first-party
providers. The frontier is now 204 closed / 30 open. See
`docs/research/g2-thread-input-dependency-boundary.md`.

`platform\service\message_notify\service_android_notify.c` is now closed as
five functions / 972 body bytes / 1,104 physical bytes. Its 65 external calls
terminate at admitted EasyLogger and IAR DLIB edges plus the closed
ANCC/profile/whitelist/sync providers. Its flagged embedded JSON-parser
candidate, shared with service_whitelist.c, is resolved by the DaveGamble
cJSON identification below. The frontier is now 205 closed / 29 open. See
`docs/research/g2-service-android-notify-dependency-boundary.md`.

`platform\device_mgr\device_mgr.c` is now closed as 20 functions / 2,484
body bytes / 2,756 physical bytes. Its ten exact CMSIS-FreeRTOS calls span
osThreadNew/Terminate, osDelay, osTimerNew/Start, and
osMessageQueueNew/Put/Get, plus one FreeRTOS kernel xTaskGetTickCount;
remaining edges are admitted EasyLogger and bounded IAR DLIB. The frontier
is now 206 closed / 28 open. See
`docs/research/g2-device-mgr-dependency-boundary.md`.

`platform\service\evenAI\service_even_ai.c` is now closed as nine functions
/ 1,984 body bytes / 2,126 physical bytes. Its 124 external calls terminate
at admitted EasyLogger, one exact CMSIS-FreeRTOS tick wrapper, and bounded
IAR DLIB edges; explicit negative evidence records no embedded AI or NN
library body. The frontier is now 207 closed / 27 open. See
`docs/research/g2-service-even-ai-dependency-boundary.md`.

`app\gui\common\ui_common_api.c` is now closed as nine functions / 892 body
bytes / 960 physical bytes. Its 41 external calls terminate at admitted
EasyLogger and bounded IAR DLIB edges only. The frontier is now 208 closed /
26 open. See `docs/research/g2-ui-common-api-dependency-boundary.md`.

`app\gui\sync_info\sync_info.c` is now closed as three functions / 780 body
bytes / 860 physical bytes. Its 55 external calls terminate at admitted
EasyLogger, the admitted nanopb runtime, and bounded IAR DLIB edges only.
The frontier is now 209 closed / 25 open. See
`docs/research/g2-sync-info-dependency-boundary.md`.

`app\gui\dashboard\dashboard.c` is now closed as 24 functions / 10,040 body
bytes / 10,856 physical bytes. Its 598 external calls terminate at admitted
LVGL, EasyLogger, IAR DLIB, CMSIS-FreeRTOS, and nanopb sources plus
first-party dashboard providers. The frontier is now 210 closed / 24 open.
See `docs/research/g2-dashboard-dependency-boundary.md`.

`app\gui\dashboard\dashboard_layout.c` is now closed as eleven functions /
2,162 body bytes / 2,332 physical bytes. Its 87 external calls terminate at
admitted EasyLogger and IAR DLIB edges plus first-party file-runtime
providers. The frontier is now 211 closed / 23 open. See
`docs/research/g2-dashboard-layout-dependency-boundary.md`.

`app\gui\terminal\terminal_session_list_ui.c` is now closed as ten functions
/ 1,966 body bytes / 2,168 physical bytes. Its 131 external calls terminate
at admitted LVGL and EasyLogger sources plus first-party terminal providers.
The frontier is now 212 closed / 22 open. See
`docs/research/g2-terminal-session-list-ui-dependency-boundary.md`.

`app\gui\terminal\terminal_ui.c` is now closed as 99 functions / 13,200
body bytes / 14,040 physical bytes, the largest anchored object in the
campaign. Its 645 external calls terminate at admitted LVGL, EasyLogger,
IAR DLIB, and CMSIS-FreeRTOS sources plus first-party terminal providers.
The frontier is now 213 closed / 21 open, with 786,254 complete-object body
bytes and 854,600 known physical bytes. See
`docs/research/g2-terminal-ui-dependency-boundary.md`.

The zero-anchor `app\gui\AgingTest\aging_test.c` object is now closed as
five functions / 856 body bytes / 972 physical bytes, linked-unanchored with
identity from eight path references and three `[aging_test]` log tags. Its
boundary against the closed compress_log.c object is exact. The frontier is
now 214 closed / 20 open. See `docs/research/g2-aging-test-recovery.md`.

The zero-anchor `app\gui\anim\bounce_anim.c` object is now closed as seven
functions / 1,114 body bytes / 1,252 physical bytes, identified by eleven
path references and eleven `[bounce.anim]` tags across a two-phase bounce
animation lifecycle. The frontier is now 215 closed / 19 open. See
`docs/research/g2-bounce-anim-recovery.md`.

The zero-anchor `platform\device_mgr\box_uart_mgr.c` object is now closed as
five functions / 1,298 body bytes / 1,410 physical bytes, identified by
eleven path references and ten `[box_uart_mgr]` tags covering the
charging-box UART unpack/CRC/flush error paths. The frontier is now 216
closed / 18 open. See `docs/research/g2-box-uart-mgr-recovery.md`.

The zero-anchor `app\gui\EvenAI\even_ai.c` object is now closed as seven
functions / 3,466 body bytes / 3,646 physical bytes: a detached 42-byte
lazy-singleton helper plus a six-block main cluster identified by fourteen
path references and fourteen `[even_ai.page]` tags. The frontier is now 217
closed / 17 open. See `docs/research/g2-even-ai-recovery.md`.

The zero-anchor `app\gui\anim\expand_anim.c` object is now closed as five
functions / 638 body bytes / 688 physical bytes, with four 32-byte callbacks
registered through its own trailing table cells. It shares its corpus gap
with the anchored conversate_ui_prep_note_page.c closure; the split is
exact and guard-pinned. The frontier is now 218 closed / 16 open. See
`docs/research/g2-expand-anim-recovery.md`.

The zero-anchor `kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c`
object is now closed as twelve functions / 3,200 body bytes / 3,256 physical
bytes, identified by six path references and six `[prvCommand_filesystem]`
tags across copy/move, directory-walk, and statfs-style command bodies.
Sparse static ingress is recorded as a scanned fact, with registration
presumed dynamic through a runtime-built command table. The frontier is now
219 closed / 15 open. See
`docs/research/g2-freertos-plus-cli-filesystem-recovery.md`.

The zero-anchor `app\gui\MessageNotify\message_notify.c` object is now
closed as four functions / 1,016 body bytes / 1,100 physical bytes,
identified by five path references and five `[message_notify.page]` tags
with screen-descriptor registration. The frontier is now 220 closed /
14 open. See `docs/research/g2-message-notify-recovery.md`.

The zero-anchor `app\gui\MessageNotify\msg_notif_timer.c` path is now
attested linked-unanchored with zero additional body bytes: its six
referencing blocks were previously absorbed as unanchored rows into the
sibling ui_msg_notif_list closure, which this attestation re-verifies
byte-for-byte against the official image. The frontier is now 221 closed /
13 open. See `docs/research/g2-msg-notif-timer-recovery.md`.

The zero-anchor `app\gui\navigation\navigation.c` object is now closed as
five functions / 1,744 body bytes / 1,934 physical bytes, identified by ten
path references and nine `[navigation.main]` tags with screen-descriptor
registration. The frontier is now 222 closed / 12 open. See
`docs/research/g2-navigation-recovery.md`.

The zero-anchor `platform\product_test\product_common.c` object is now
closed as four functions / 686 body bytes / 760 physical bytes, identified
by six path references and six `[product_common]` tags covering the font
CRC validation routine; its boundary against production_mic_func.c is
exact. The frontier is now 223 closed / 11 open. See
`docs/research/g2-product-common-recovery.md`.

The zero-anchor `product\s200\app\config\board_config.c` object is now
closed as one function / 118 body bytes / 700 physical bytes: a
data-dominated object whose 582-byte trailing extent carries the s200
pinmux/peripheral board configuration constants. The frontier is now 224
closed / 10 open. See `docs/research/g2-s200-board-config-recovery.md`.

The zero-anchor `product\s200\app\config\main.c` object is now closed as
six functions / 1,504 body bytes / 1,530 physical bytes, identified by
fourteen path references and ten `[mainThread]` tags. It is a product
configuration/startup grab-bag: custom LVGL widget constructors, an init
hook, and the main thread body. The frontier is now 225 closed / 9 open.
See `docs/research/g2-s200-config-main-recovery.md`.

The zero-anchor `platform\input\service_gesture_processor.c` object is now
closed as five functions / 1,236 body bytes / 1,346 physical bytes,
identified by five path references and five `[touch.ges]` tags covering
proximity/slider gesture telemetry. The frontier is now 226 closed /
8 open. See `docs/research/g2-service-gesture-processor-recovery.md`.

The zero-anchor `app\gui\setting\setting.c` object is now closed as 18
functions / 5,486 body bytes / 5,772 physical bytes, the largest
zero-anchor object in the campaign, identified by 51 path references and
51 `[setting]` tags across universal unit setting and dominant-hand
ring-mac recovery. The frontier is now 227 closed / 7 open. See
`docs/research/g2-setting-recovery.md`.

The zero-anchor `app\gui\SystemAlert\systemAlert.c` object is now closed as
seven functions / 2,176 body bytes / 2,346 physical bytes, identified by
twelve path references and twelve `[system_alert]` tags with
screen-descriptor registration. The frontier is now 228 closed / 6 open.
See `docs/research/g2-system-alert-recovery.md`.

The zero-anchor `app\gui\system\system_monitor.c` object is now closed as
one function / 510 body bytes / 592 physical bytes: a single screen block
with six path references and six `[system_monitor]` tags whose descriptor
cell is the sole entry vector. The frontier is now 229 closed / 5 open.
See `docs/research/g2-system-monitor-recovery.md`.

The zero-anchor `app\gui\terminal\terminal_query_panel_ui.c` object is now
closed as six functions / 1,186 body bytes / 1,186 physical bytes; five
helper blocks are included by contiguity and terminal-cluster caller
evidence. The frontier is now 230 closed / 4 open. See
`docs/research/g2-terminal-query-panel-ui-recovery.md`.

The zero-anchor `app\gui\terminal\terminal_timer.c` object is now closed as
six functions / 624 body bytes / 724 physical bytes, identified by six path
references and six `[terminal.timer]` tags covering ASR-result and
voice-recording timeout management; one interleaved 16-byte foreign block
is pinned and not claimed. The frontier is now 231 closed / 3 open. See
`docs/research/g2-terminal-timer-recovery.md`.

The zero-anchor `app\gui\translate\translate_data.c` path is now attested
linked-unanchored with zero additional body bytes: the sole block carrying
its five literal references was previously absorbed as an unanchored row
into the sibling translate_ui closure, re-verified byte-for-byte against
the official image. The frontier is now 232 closed / 2 open. See
`docs/research/g2-translate-data-recovery.md`.

The zero-anchor `app\ux\ux_production\ux_production.c` object is now closed
as one function / 854 body bytes / 956 physical bytes, identified by ten
path references and ten `[ux.production]` tags covering device-sync test
and production command handling; dispatch is presumed dynamic and recorded
as a scanned fact. The frontier is now 233 closed / 1 open. See
`docs/research/g2-ux-production-recovery.md`.

The zero-anchor `app\ux\ux_settings\ux_settings.c` object is now closed as
two functions / 572 body bytes / 648 physical bytes, identified by seven
path references and seven `[ux.setting]` tags across time sync,
production-mode gating, and the device settings app. The retained-path
frontier is now 234 closed / 0 open: all 1,230 anchored functions and all
485,274 anchored body bytes are closed, with 814,534 complete-object body
bytes and 885,418 known physical bytes over 232 closure manifests; the
closed manifest ledger is
`3cd89ad644ad243b7d2c94bf1a5d8beb5c6270235bbfe4ee936fb4b7711bb1d8`. No new
version or commit discriminator was found in any of the 53 closures. See
`docs/research/g2-ux-settings-recovery.md`.

### DaveGamble cJSON family identification

The cJSON-class JSON parser previously flagged as shared by
service_android_notify.c and service_whitelist.c is now identified as
DaveGamble cJSON, version interval v1.7.9--v1.7.12, from four binary
discriminators: the >=1.7.9 issue-315 get_object_item fix, the <1.7.13
buffer_skip_whitespace offset behavior, the absent <1.7.14
parse_array/parse_object head->prev tail store, and the <1.7.19 64-byte
stack parse_number buffer. The family is 21 functions / 2,572 body bytes at
`[0x004D798C,0x004D83D8)` with 34 external caller sites. This is the 26th
third-party family; it is identified but not yet source-admitted, and no
vendored snapshot exists. See
`docs/research/g2-json-parser-source-candidate-audit.md`.

### DaveGamble cJSON snapshot admission

The cJSON family is now admitted as an authenticated vendored snapshot. The
pristine MIT three-file closure (`cJSON.c`, `cJSON.h`, `LICENSE`) at
`g2/third_party/cJSON/` selects the interval-ceiling lightweight tag v1.7.12,
commit `3c8935676a97c7c97bf006db8312875b4f292f6c`, tree
`6c770a14e7d9ac1a8fd452a32c51fa4462cf2b45`, as the reproducible OpenCFW
baseline — not a claim about the vendor checkout or vendoring path, which
remain binary-unobservable. All 21 linked parse-side functions were
re-verified byte-identical C text between v1.7.9
(`f110bd2e585394bf47baca34a06df2569a9232b6`) and v1.7.12 during admission;
the whole-file tag diff is confined to the dead-stripped
print/create/edit/utils side. The fail-closed offline
`verify_snapshot.py` pins the commit/tree/interval identities, all three file
hashes and Git blob ids, and the explicit **production-excluded** decision:
the 21 functions / 2,572 body bytes at `[0x004D798C,0x004D83D8)` remain
cut-forward pending a compiler/ABI readiness matrix and a reviewed
production-overlay admission decision. `tests/test_cjson_snapshot.py` runs
the verifier, asserts the production-exclusion decision, and adds a
Cortex-M55 freestanding compile probe proving all six public entry sections.
The shared registry (`third-party/README.md`), upstream inventory, gap
priority, closure audit, and the machine-readable closure ledger
(`selected_source_commit`, residual gates, snapshot evidence) agree. No build
profile, ownership number, or package hash changed. See
`third_party/cJSON/README.openCFW.md` and
`third_party/cJSON/PROVENANCE.json`.

### Four-component controller-boundary evidence wave

A parallel four-lane evidence pass closed one bounded increment on each
non-Apollo component without touching production ownership:

- **EM9305 BLE controller** — all 175 residual segments / 33,658 bytes
  (15.96% of the application) are now classified in
  `tools/manifests/em9305-residual-provenance-map.tsv`: 130 segments /
  30,564 bytes are proprietary modern-controller or EM vendor-system source
  (retention recommended), 7 / 1,224 bytes first-party Even application,
  2 / 980 bytes toolchain/linker-generated, and 36 / 890 bytes remain
  explicitly unclassified. The MetaWare runtime cluster is structurally
  proven; the authenticated first-party hook-table entries, QF internal-hook
  stubs, and the `MyApp` ID-181 assertion site are pinned. See
  `docs/research/em9305-residual-provenance-audit.md` and
  `tests/test_analyze_em9305_residual_provenance.py`.
- **Audio codec/DSP** — both FWPK segment destinations are conclusively
  resolved: the 38,236-byte type-1 boot image is the NationalChip grus
  (GX8002) UART-boot container (stage1 to IRAM `0x10000000`, stage2 to
  `0x10002800`), and the 287,808-byte type-2 BINH main image targets codec
  SPI NOR offset 0 as a dual-firmware concatenation (image A
  `[0x0,0x2F3B0)` with 36,484 bytes XIP text and a 129,964-byte NPU/audio
  payload; image B `[0x2F3B0,0x46440)`); all CRCs, version chains, and the
  `serialdown 0 <size> 8192` flash command are verified. The image remains
  an explicit proprietary NationalChip boundary. See
  `docs/research/g2-codec-fwpk-segments-recovery.md` and
  `tests/test_analyze_g2_codec_fwpk_segments.py`.
- **Touch controller** — identity is proven: Infineon/Cypress PSoC 4000T
  OPN CY8C4046FNI (Cortex-M0+, 64 KiB flash, 8 KiB SRAM, 5th-gen CapSense
  MSCLP0), with every LDR-confirmed peripheral base an exact psoc4000t SVD
  block base and the retained host path `driver\touch\drv_cy8c4046fni.c`.
  A complete ten-region memory map, the polled single-handler vector model,
  FWPK type-3 framing, and the CRC-32C record and trailing-payload checksums
  (hardware-instruction-verified) are pinned. See
  `docs/research/g2-touch-identity-recovery.md` and
  `tests/test_analyze_g2_touch_identity.py`.
- **Charging case** — STM32G0Bx-class (leading STM32G0B1) is established
  from the 46-word vector table and bank-swap literals; FreeRTOS V10-line
  GCC ARM_CM0 port is instruction-matched against upstream V10.5.1 port.c
  with kernel statics pinned; STM32CubeG0 HAL/LL module presence is
  separated from G2 policy; the `5A A5 FF` UART framing and the 22-step
  OTA-box state machine (including Copy-SN) are mapped; four
  device-specific SN preservation windows are pinned as never-overwrite
  regions. See `docs/research/g2-box-stm32g0-platform-recovery.md` and
  `tests/test_analyze_g2_box_stm32g0_platform.py`.

All four lanes added fail-closed analyzers, machine-readable manifests, and
tests (42 focused tests, all passing). No build profile, ownership number,
or package hash changed; all four components remain retained behind their
declared boundaries.

### Second frontier wave: controller-cluster decompilation, codec stage2, touch protocol, case function map, Apollo unanchored census

- **EM9305 BLE controller** — the two largest high-confidence
  modern-controller clusters are now function-recovered via the
  lorelei GNU ARC lane (Ghidra ARC skipped per benchmark guidance):
  slave-connection `[0x00329888,0x0032A4BE)` and master periodic
  scan/PAwR `[0x00321C30,0x0032233C)`, ten functions / 4,930 bytes with
  an exact zero-remainder tiling, bracket-anchored against authenticated
  Packetcraft object boundaries. Three functions are opcode-exact, five
  modified (ratios 0.89–0.97), two divergent — sharpening the
  proprietary-retention verdict: stock is a newer/differently-configured
  Packetcraft build whose authoritative source is unavailable. The lane
  return is manifested at `research/corpus/em9305/cluster-recovery/`.
  See `docs/research/em9305-controller-cluster-recovery.md`.
- **Audio codec/DSP** — image-A stage2 is conclusively sectioned using
  the official `c-sky/binutils-gdb` fork (GNU 2.43.1 proven to mis-decode
  32-bit forms): 36,484 B XIP text, 12,516 B SRAM text at
  `0x10023400`, and 2,196 B SRAM data, with the combined copy closing
  exactly on `stage2_size − xip_len`. The entire 129,964 B payload is
  the LVP_KWS wake-word model: command stream `[0xF804,0x11BD0)` and
  weights `[0x11BD0,0x2F3B0)`, exact-fit to image B. See
  `docs/research/g2-codec-stage2-sections-recovery.md`.
- **Touch controller** — the SCB1 I2C protocol is closed: a 9-slot
  command switch (version/ID query, prox-baseline read/save, threshold
  read, gesture-config write, enter-DFU, sensor report), active-low
  attention line, 16 B report format, deferred EEPROM config with `UNVE`
  magic, and power entries. Architecturally decisive: the payload is the
  shipped prefix `[0,0x8680)` of a base-0 image whose resident remainder
  owns the DFU engine and boot — touch OTA depends on factory-matched
  resident flash. See `docs/research/g2-touch-i2c-protocol-recovery.md`.
- **Charging case** — a full lorelei Ghidra function map (428 functions
  / 40,664 bytes) attributes the image: 79 FreeRTOS-kernel functions /
  5,440 B (CMSIS-RTOS2 wrapper identified), 10 STM32 HAL functions /
  1,018 B, 71 first-party G2 functions, 261 unresolved helpers. Both
  open questions answered: frame checks are additive sums (no polynomial
  CRC), and logging uses direct ADR/LDR string pointers (no ID scheme).
  See `docs/research/g2-box-function-map-recovery.md`.
- **Apollo unanchored census** — the 5,610-function unanchored set is
  re-derived exactly (7,370 corpus − 1,760 anchored) and triaged with
  zero drift against the origin accounting: 27% was already reviewed by
  per-module manifests; the unreviewed core is 1,911 functions /
  299,736 bytes. Buckets pin first-party (1,782/216,564 B), LVGL
  (1,054/97,430 B), Cordio (383/27,356 B), and the smaller families;
  new identifications include the IAR DLIB formatted-I/O cluster
  (printf core `0x00481836`, scanf core `0x004D1638`) and byte-exact
  cross-validation of `FT_Done_Face`. See
  `docs/research/g2-apollo-unanchored-census.md`.

All five lanes added fail-closed analyzers, manifests, and tests (52
focused tests passing). The corpus index grew to 1,950 files / 44
manifests (EM9305 cluster-recovery lane). No build profile, ownership
number, or package hash changed; all controller components remain
retained behind their declared boundaries.
