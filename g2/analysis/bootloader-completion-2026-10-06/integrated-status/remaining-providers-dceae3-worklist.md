# Recoverable provider work following the aligned integration

## Current component checklistca59e9

ISR put/get/notify/deferred flags and callable reset now native:1480+62+1 direct cases and7 integrated cases PASS;624 inputs/157 objects unchanged. [ISR evidence](isr-delivery/REPORT.md), [current31-alias ledger](remaining-providers-current.md). Earlier tables below remain historical.

Native mutex wrappers/kernel/priority helpers now integrated;7 exact-image cases,516 focused,2 persistent sequences,4 actual block-setup cases PASS;619 inputs/156 objects unchanged. See [mutex evidence and limits](mutex-kernel/REPORT.md) and [current35-alias ledger](remaining-providers-current.md). Previous tables below are historical.

The current exhaustive selected-linker boundary ledger is [remaining-providers-current.md](remaining-providers-current.md). Seven exact-image3fcec2 cases PASS;614 inputs/154 objects unchanged. EasyLogger records/guard/wrappers and native constructor integrated; lower mutex acquire/release, kernel ownership and scheduler remain open. Older checkpoint table below is preserved as history.

Current verified image 67f3f209bc1867dbb2a995e7805dd756105f05bae31831d86e61bda7df689796;7 exact-image cases PASS, 608 input hashes / 153 objects match. Supersedes historical open rows below. Coverage is bounded original/source comparison, not full source/byte equality.

| Component/provider | Current status | Evidence/next edge |
| --- | --- | --- |
| IOM context/config/CQ/async/IRQ | Native selected bodies, regression PASS | Hardware delivery/task ownership and dynamic/global reachability remain open |
| GPIO/NVIC/semaphore | Native selected bodies, regression PASS | Higher-bank IRQ/zero-fill/physical scheduling limits retained |
| ADC init/reset + INFO chain | Native135 tests | External ROM48/factory values modeled |
| ADC control/getters | Native279 tests | API0≠valid calibration; stale pair/cache behavior preserved |
| ADC context/channel config | Native93 tests | Register encoding/counter, not physical sampling rate |
| ADC correction/enumeration/lifecycle | Native988 tests/776 original bytes +7 shared cases | [Behavior/limits](adc-samples/REPORT.md); no ISR/task drain proof |
| ADC profile42f020/apply42ea68 + user15 power children | Native 650 tests/all444 new bytes | [Native reused power/clock/poll/critical chain](adc-profile/REPORT.md); external ROM/callback/ack/lifetime limits |
| Contiguous ADC region42e8d0..42f14e |14 mapped bodies/2148 instruction bytes+24 literals+2 alignment | [Component map](adc-region-map-ff5313.json), not whole firmware/physical proof |
| UART constructor 422ad4 and actual config/save-restore/activate/baud/status/NVIC | Native 1040 direct/all 1,652 bytes + focused shared state and 7 exact-image cases PASS | [Source, borrowed buffers, row initialized0 and ignored-status/partial-write limits](uart-context/REPORT.md); TX/RX/DMA/IRQ drain remains open |
| Service + lower RTOS/kernel/startup alternatives | Open | Recover actual reachable providers; do not infer completion from wrappers |
| Full vectors/assets/data/layout/compiler/byte equality | Open | Whole payload source reconstruction and exact rebuild remain unproved |

## Historical checkpoints

The aligned, corrected initializer/NOR source image is pinned as `dceae3b56c3ef4b0572f4cd499230ca8f5eb20419cf1c4a0910d05d607389bee`. All seven DCE cases passed. Subsequent immutable459804 also passed its own seven cases, with matching before/after interruption and reboot results;563 input files and134 objects were unchanged at receipt creation.

Concrete work performed beyond the alignment repair:

- Context interrupt API `0x42c63a`: new readable `initializer_callbacks/context_interrupt.c` and original/source comparison, 52 PASS cases /56 original instruction bytes. Null/malformed handles return2; mask bit1 returns6; accepted calls OR the enable register. Synthetic MMIO; now selected in subsequent bcc057 shared candidate;52 direct cases PASS on that exact ELF, all seven fresh integration cases PASS, both stop/reboot phases matched.
- Kernel-state wrapper `0x416088`: existing native source replayed directly from the DCE shared ELF; lifecycle suite216 PASS cases /224 original bytes. No-argument uint32 ABI verified. 459804 now binds callers natively through `opencfw_bl_kernel_state = opencfw_boot_kernel_state`;73 direct NOR wait cases validate the delayed branch. Lower scheduler startup is modeled and actual IRQ delivery remains unproved.
- Filesystem mutex acquire/release `0x4166aa/0x416710`: existing reconstructed wrappers replayed in their isolated ELF,288 PASS /258 original bytes; minimal selected object/dependency analysis completed. Only `queue/mutex.c` should be added, avoiding duplicate queue/runtime objects. Tagged/plain kernel take and tagged give remain lower boundaries; plain release can use the already native queue-put. No priority inheritance, blocking latency or complete kernel ownership claim.

These are implementation/validation prerequisites, not completion by file count. Current bcc057 integration has its own seven-case PASS; source completeness remains open. Next highest-value initializer edge is context claim/configuration that populates real transfer handles; native interrupt tests currently receive null at the shared caller. Filesystem mutex/kernel and startup orchestration remain separate concrete options. Future integration must pin a new ELF and run fresh comparisons; previous results cannot be relabeled. No commits, index changes or hardware operations were performed.

## Subsequent IOM context closure85d6eb

Claim42c4c6 and transaction42c988 now have reconstructed C, source-owned static pool and native shared linkage.496 direct cases plus52 interrupt cases and all seven exact-image integration cases PASS;567 inputs/137 objects remain unchanged. Valid module4 handle reaches IRQ caller, whose mask255 returns6. Instance configuration42cc34, enable42c538, retry43048e and CQ42c420/42c44e remain next specific edges. Powerdown retains claim; no unrecovered SDK release path is fabricated. Partial ownership maps854 original bytes for these three functions; full implementation percentage remains unaudited.

## d98328 closure and next boundary

Instance configuration42cc34, enable42c538, retry43048e, interface/clock helpers and CQ42c3e2/42c420/42c44e are native and validated (seven integration cases;740 child cases). They are no longer open provider cuts. Remaining initializer boundaries: NVIC430470, semaphore416762, descriptor430280, ADC/service children. Asynchronous IOM service42c6f8/publication42c45a and release/uninitialize remain unclosed; synthetic retry tests do not prove hardware cleanup safety. Next bounded provider: NVIC430470. See same-image-validation-d98328.json for immutable identity/provenance.

## Native NVIC19ff0c

NVIC430470 is now native, with196608 original/source comparisons and all seven fresh image cases PASS;573 frozen files/142 objects unchanged. Its30-byte mapping is separately recorded. Next specific initializer provider: semaphore creation416762, including its lower kernel/object allocation dependencies. Descriptor registration430280, ADC/service children, asynchronous IOM publication42c45a/service42c6f8 and release remain open. The wrapper proves issued writes only, not physical IRQ delivery.

## Semaphore52ca30

416762 is native with wrapper-reachable counting419e62/419e94 and destroy41a470 behavior. All seven fresh image cases,1344 direct cases,12 native heap cleanup cases,740 IOM cases and2 conditional CQ cases PASS;574 inputs/143 objects unchanged. Independently invalid constructor/null-destroy fatal entries remain untested; child C bodies inline and separate sections are GC discarded. Descriptor registrar430280/ADC/service and lower lifecycle/scheduling remain initializer boundaries. Next asynchronous target is publisher42c45a, followed by reachable service42c6f8/callback/head movement; new pseudocode is in iom-publisher-next.md. No release beyond stock semantics is inferred.

## Asynchronous IOM92619e

Publisher42c45a/service42c6f8 plus classifier42c076, recovery42c0b2 and CQ status427a56/resume427b38/index427754 reconstructed and retained.515 direct comparisons observe1490 mapped original body bytes; all seven fresh integration cases and740/12/2 regressions PASS.581 files/144 objects unchanged. Asynchronous delivery is not exercised by seven-case startup. Actual next reachable routing chain: IRQ430610 -> status42c672 -> clear42c6b6 -> service42c6f8 with transfer handle0x200003b8. Those three routing bodies, submission/full/allocation paths and true release/uninitialize remain open. Callback clear/retain is not buffer free; no speculative release is added.

## Current checkpoint4f111c (supersedes earlier open IRQ rows)

IRQ status42c672/clear42c6b6/wrapper430610 are native;292 direct plus7 integration and515/740/12/2 affected cases PASS,584 files/145 objects unchanged. All18 IOM-island bodies are accounted,3424 instruction bytes/28 literals. Submission/full/uninitialize APIs are not standalone retained functions in that island; do not invent vendor SDK replacements. Global inline/dynamic reachability is not certified. Next actual initializer cut430280 registers pin/GPIO descriptors, not queue messages. Physical IRQ/callback scheduling, whole payload, kernel/lifecycle and compiler/byte equality remain open.

## CMDQ ownership follow-up

Actual reserve/post/cancel direct edges traced in MSPI control requests,40 shared-image stock/source cases PASS. Generic term427ad6:13 comparisons PASS with separate retained frozen-object module (not linked into4f111c). No heap allocation/free in these bodies. MSPI423f64 ignores forced-term status and clears slot; actual DMA/IRQ quiescence unproved. IOM submission/uninit remains not retained in its island; global dynamic/inline users remain outside this bounded proof. See cmdq-ownership/REPORT.md and supplemental provenance.

## Current GPIO initializer checkpoint6bef4e

Supersedes earlier open descriptor430280 rows. Registrar430280/status41dcca/clear41de3c/register41e000/control41da84/priority43025c are source-owned and integrated; existing pin-config/state/NVIC sources reused.434 direct and7 fresh shared-image cases PASS,589 files/147 objects unchanged; all affected292/515/740/12/2 regressions PASS. Original zero-fill is explicitly modeled only in direct IRQ-descriptor fixtures; local IRQ data supports four banks and higher-bank callback descriptors remain outside the partial-image validation domain. CMDQ term13 comparisons still use a separate module, not shared-image linkage. Next actual retained initializer gap: ADC42e8d0 static-context/calibration initialization and its421548 lower provider, then its remaining HAL children. See adc-next.md; no ADC source integration claimed yet. Whole bootloader/source/byte equality remains open.

## Current ADC context checkpoint8ec1fa

Supersedes ADC context-initialize42e8d0/reset42ea32 cuts: native C/static72-byte pool plus native reused421548/4213e6/41d28a chain integrated.135 direct cases cover408 original new body bytes; all7 exact-image and434/292/515/740/12/2 regressions PASS.592 files/148 objects unchanged. Only absent ROM48 gets explicit zero-word/status fixture in seven cases; no actual OTP/calibration proof. Init success may select defaults/invalid correction markers, claim published before reads; reset is metadata, not stop/free/quiescence. Next retained ADC cut42ec0c control/getters340 bytes: correction getter does not read validity marker; temperature getter returns rawword0/1. Remaining ADC configure/profile/channel/activate/enumerate and service/post-bringup/runtime/kernel completion stays open. CMDQ term remains separately tested, GPIO higher-bank/zero-fill limits remain.

## Current ADC control checkpoint4cb522

Supersedes42ec0c control/getter cut: native FP32 implementation integrated,279 direct tests/all340 original bytes visited and7 fresh exact-image cases PASS;595 files/149 objects unchanged, all affected135/434/292/515/740/12/2 regressions PASS. API0 does not prove calibration validity; request3 ignores correction marker; request2 raw0/1 marker;20027028 temperature cache survives init/reset. Next42eb74 context54B and42eaf6 channel126B already have93 separate-leaf comparisons PASS, **shared integration outstanding**; no increase of seven-case source coverage from that leaf. Profile/activation/sample normalization/service/RTOS and whole-source/byte equality remain open. Existing ROM/IRQ/termination limits preserved.

## Current ADC configuration checkpoint44d67f

42eb74 context54B and42eaf6 channel126B now native and shared-integrated.93 direct comparisons/all180 bytes,279 control/135 init and all affected regressions plus7 fresh exact-image cases PASS;598 final input hashes/150 objects match (direct runner scope wording correction preserved in prior manifest; logic/image unchanged). Repeated configuration increments2002702c without uniqueness/locking/saturation proof. Next actual retained sample/lifecycle region: numerical correction42ee00 checks20027199;42eda0 is deactivation/clock release, not numerical normalization. Profile/apply/activation/enumeration/service/RTOS/source completeness/byte equality remain open. Seeadc-sample-next.md. No hardware/ROM/calibration/quiescence claims changed.

## Current ADC sample/lifecycle checkpoint8287c7

Supersedes cuts42ed60 activation,42ebaa/42ebe2 timer enable/disable,42eff4 command,42eda0 deactivation and42ee70 enumeration;42ee00 correction native too.7 bodies776B/all visited,988 direct/all affected regressions/7 fresh exact-image cases PASS;601 files/151 objects unchanged. Native reused clock_release422364/provider4 children tested with absent/sole/remaining user15; explicit ROM/ready/FIFO/user-map inputs, no actual physical sampling or IRQ/task drain proof. Count0 still processes1; correction ignores pair when marker0, temperatureCHSEL8 bypasses; corrected result12-bit mask. Next retainedADC42f020 profile transfer302B and42ea68 apply142B plus required41bf84/41c17a power-mode children. Static dependencies documented inadc-profile-next.md; no closure credited for them. Remaining service/RTOS/kernel/source/layout/byte equality stays open.

## Current ADC profile checkpointff5313

42f020 profile302B/apply42ea68142B native,650 direct/all444 bytes plus required reused native user15 power/clock/query/poll/critical children.988 zero-count/temperature/calibration sample tests and all affected regressions/7 fresh exact-image cases PASS;604 inputs/152 objects unchanged. ADC region14 mapped functions2148 instruction bytes+24 literals+2 alignment; component mapping not whole bootloader completeness. Power failures may be ignored/clock restore errors no rollback; ROM40/48/FIFO/acknowledgement/physical/async/lifetime limits explicit. Next post-context422ad4(212B) and real-handle downstream children, then service/RTOS/kernel/startup/source/layout/byte equality. Seepost-context-next.md.
