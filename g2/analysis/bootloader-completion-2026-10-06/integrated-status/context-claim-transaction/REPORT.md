# Static IOM context claim and transaction recovery

Image: `85d6eb5362976d4d4a296ae08b92161bb979342d21002dfa2257c0f75f5e975f`. Locked bootloader:148599 bytes at0x410000, SHA256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. The actual instruction stream, rather than SDK equivalence or historical “source_owned” labels, is the implementation oracle.

## Source and ABI

Readable reconstructed source is in `g2/components/bootloader/initializer_callbacks/context_claim.c`, `context_transaction.c` and `context_claim.h`. Claim: original42c4c6..42c538 (114 bytes). Transaction:42c988..42cc34 (684 bytes). These are complete bounded function bodies; their lower dependency bodies are separate. `original-disassembly.txt` / `instructions.json` contain273 decoded stock instructions with exact bytes. `../iom-source-ownership-85d6eb.json` hashes these extents and the prior56-byte interrupt helper:854 deduplicated original body bytes across this three-function audited subset. This is not whole-bootloader source completeness.

Claim's register ABI is `(uint32 module, uint32 *output_handle) -> uint32 status`. It reserves a static slot, not heap memory. Eight source-owned NOLOAD slots live at0x2001455c, each0x8a8 bytes, total17728 bytes, end0x20018a9c. Slot prefix+0 is flags/magic; +4 is module. The rest is explicitly opaque except recovered transaction offsets. Success performs three prefix writes: set claimed bit24, clear enabled bit25, then preserve high8 flag bits while setting low24 magic0x123456; write module and output pointer. It does not clear the opaque tail.

| Path | Result | State/ownership |
| --- | --- | --- |
| module>=8 |5|Pool/output unchanged; module check precedes null-output check.|
| null output |6|Pool/output unchanged.|
| claimed bit24 already set |7|Pool/output unchanged; does not allocate another slot.|
| available slot |0|Caller receives address of static slot; no malloc/free or per-call capacity allocation.|
| transaction command1/2 |clock release result|Powerdown/config snapshot may change, but claim/magic remain. A later claim still returns7.|

Transaction register ABI is `(handle, command, retain) -> uint32 status`. Handle must satisfy `(flags & 0x01ffffff)==0x01123456`, otherwise2. Command and retain truncate to uint8. Command0 enters the module power domain and requests clock class4. Restore requested without snapshot byte+0x868 returns7. Restore copies13 saved registers, clears CQ-enable bit while restoring+0x228, optionally calls CQ-enable, optionally waits for enabled hardware status, and clears the snapshot byte. Commands1 and2 share the powerdown path; other commands return6. If already enabled, busy status `(reg+0x248 &6)!=4` or pending context+0x24 returns3 before changes. Optional retention copies13 registers, optionally disables CQ and marks+0x868=1. It then clears bits0 and4 of register+0x11c in two distinct writes, calls mode-leave and releases class4 clock.

Save order/context offsets: register104→86c,118→874,11c→878,228→87c,22c→880,234→884,23c→888,240→88c,244→890,280→894,2c0→898,200→89c,210→870. Restore order differs and is preserved in source. Mode-enter/leave statuses are ignored; clock request/release results propagate. Restore's lower CQ/wait return values are ignored too, as in stock.

## Actual shared caller path

`platform_finish.c` calls claim with the address of each row's transfer field. Both normal runs now create real handles for modules2,4,5,7, then execute four native transactions. Row4 receives0x200167fc; the subsequent interrupt call sees that valid handle and mask255. Original/source now execute the valid-magic, forbidden-mask branch, returning6; the caller ignores it. This does not claim successful physical IRQ activation. The same-image52-case direct interrupt suite includes successful mask4 register writes using simulated MMIO; the composed496-case suite also covers claim→configuration→interrupt→powerdown→duplicate-claim.

Instance configuration42cc34, context enable42c538 and retry43048e remain explicit child boundaries. Thus the newly owned handle can be traced through the caller, but its detailed peripheral instance setup/enable fields are not yet proven. The shared image reuses native power-domain and clock implementations. CQ adapters42c420/42c44e remain explicit numerical dependencies; replacing whole transaction cuts with these narrower edges leaves numeric binding count73, which must not be interpreted as no implementation progress.

## Validation and cleanup limit

`../context-claim-transaction-85d6eb.json`:496 PASS comparisons /850 observed stock bytes. It compares ordered pool/output/MMIO writes, full pool/MMIO hashes, return values and exact lower-call arguments. Cases exercise modules0..10, invalid/null outputs, initialized/high-bit prefixes, all command classes and uint8 truncation, missing snapshots, enabled/busy states, snapshot/restore, CQ branches, and injected lower/clock failures. Lower APIs are deterministic cuts in this direct suite; shared native execution is separate. `../context-interrupt-85d6eb.json`:52 PASS cases on the same immutable ELF.

Alignment334 mappings PASS and known bad ac4b is rejected. All seven exact-image cases PASS: normal2, malformed3, interruption/reboot2. Both interruption phases and reboot outcomes match.567 frozen inputs and137 objects are unchanged; `../same-image-validation-85d6eb.json` records profile hashes and endpoints.

Failure “cleanup” for claim is no-change failure behavior, not a free operation. The recovered platform-finish caller does not check claim's status or release it on later errors; the transaction powerdown preserves the static claim. The SDK documents an uninitialize API and its older available implementation clears a claimed bit after disable, but no corresponding target release body has been independently recovered or made reachable here. No speculative release/reset was added. Real scheduling, MMIO timing, cancellation, silicon cleanup and IRQ delivery remain unverified.

## Provenance and loader correction

The local Apollo510 HAL header supplies the initialize/configure/enable/uninitialize API shape. The documented locally installed R3.2.0 Apollo3p `am_hal_iom.c` supplies a comparison for static allocation and prefix fields; it is not treated as the target source revision. Header/source identity and body hashes are distinct. Initial shared runs stopped before source execution because the common ELF loader tried to map the new SRAM NOLOAD pool over an existing mapping. The loader now reuses covered memory and initializes PT_LOAD zero-fill. `initial-loader-failure.json` and the initial input freeze are preserved in the snapshot; firmware ELF identity did not change.
