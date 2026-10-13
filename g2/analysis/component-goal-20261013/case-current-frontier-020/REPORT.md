# CASE current frontier after waves014–019

CASE software work is not globally exhausted. Missing the original compiler constrains exact matching; it did not prevent the concrete improvements completed here. Stay on CASE; no next-component ownership handoff or scheduler is requested.

- Exact matching: original Arm Compiler6/armlink release and authenticated project/per-file/scatter recipe remain absent. The current image is not byte-identical to stock;0/6 replacement images are accepted.
- Custom-image fit: current401-unit source code/data span is63,122bytes. The constrained raw image is63,128bytes including6 erased-flash alignment bytes. It fits before the documented0x0803F000 reserved factory pages with194,920bytes headroom. The7,370-byte stock-length difference is not a physical-capacity failure. Link assertions reject protected-page overlap, insufficient flash space, and unqualified allocated mutable sections. This establishes emitted-layout/capacity contracts, not every absoluteRAM reference, computed root, ambient stack, package or runtime-update contract.
- Hardware acceptance: physical clocks, IRQ/FIFO latency, sensorbus data/guard races, scheduler arbitration and flash persistence are still unvalidated. Static register fixtures are not hardware acceptance.

## Completed substantive findings

Wave014 found and corrected a real recovery bug: command0x13 returned0x13 for unsupported subtypes; stock returns0xFF. Only subtype6 or subtype1 plus confirmation1 succeeds. The new source passes4,750 full linked native/C router cases, including ten RAM command families and every opcode's bad-CRC branch. Earlierb3c5 ELF remains historical; corrected current source supersedes it.

Wave016 unifies the signed battery measurement ABI across two providers/three callers, fixing the void/int32 declaration mismatch.538 controlled-query success cases execute actual native/source divide;6 explicit counterfactual client fault cases qualify error guards without claiming native hardware can return those errors. Native guarded wrapperA130 actually returns0. Eight busy-guard cases execute real query/status/delay/divide/conversion without child interception.

Wave017 executes9,840 complete native/source forwarding cases through actual UART BUSY providers. It compares every attempted header/payload/checksum byte and RAM/return/SP. BUSY rejects transmission; these are attempts, not wire bytes. Wave019 executes738 cases through actual UART/wait/tick providers with a clearly synthetic always-ready register fixture and compares actual TDR writes. No firmware stubs, child-return injections or physical FIFO claims are made.

Wave018 refreshes the reproducible constrained artifact against current source. The current semantic ELF is SHA256a23c019ada7fe636347dbd22806879bdcabb689e6e524ed09b711a9c0946f27a; artifact hashes are in the sealed wave018 receipt. Established6,509 graph cases,765 memory cases andthree full reset fills still pass. Counts are bounded test domains, not interval/byte-coverage promotion.

## Investigated remaining candidates

| Candidate | Current disposition |
|---|---|
| RAM/error/quiet forwarding router and battery client ABI | Implemented and qualified in the stated regimes. Hardware-dependent regimes are not silently covered. |
| Source custom image bounds/alignment | Implemented. Raw artifact is reviewable; it is not an approved flash/package. |
| Log-enabled router/sink composition | Remains a supported software candidate. Needs a coherent console/formatter sink fixture and full native/provider identities before tests can substantiate it; not blocked by missing original compiler. |
| UART transient-ready/FIFO/timeout/error paths | Remains a supported software/model candidate. Staticready andBUSY fixtures do not provide independent timing/status-transition evidence. Build a source/datasheet-grounded model or obtain traces before claiming those regimes; physical acceptance still requires hardware. |
| All absoluteRAM/computed callback roots/ambient stack | Additional evidence/qualification needed.39 known roots and the reset boundary are not a complete inventory. Original scatter absence blocks claiming stock placement but does not prohibit a source-derived custom contract. |
| Exact official package/producer matching | Cannot currently close without producing-tool/project evidence and complete source/data/placement/accounting gates. |
| Touch remaining widget/history generators | Still blocked on authenticated meaning of nonzero offset142 halfwords and history capacity/alignment. A426-byte gap is not a generator count. |

Because supported CASE candidates remain, do not declare CASE/Touch globally exhausted or switch to boot/EM/codecs solely on compiler availability. Keep the original frontier012 and correctedfrontier013 historical; this is a separate current-frontier checkpoint. No Goal control is a substantive stopcondition; no scheduler substitute will be created. MAIN/FreeType remains its owner's scope. No commits, pushes, worktrees, branches, flashing or git-index mutations were performed. Concurrent staged work is preserved.
