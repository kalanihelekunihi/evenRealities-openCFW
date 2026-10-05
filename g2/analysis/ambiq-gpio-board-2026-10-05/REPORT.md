# GPIO state-write and radio consumer: completed source comparison

The existing GPIO configuration module now includes the unchanged pinned SDK state-write body at stock 0x480fd6 and a reconstructed consumer at 0x52dd7c. The consumer clears pin 93, then configures pin 138 with raw 3; both statuses are ignored and its return is void. This is a bounded synchronous register chain, not a complete radio shutdown implementation.

Source lives in g2/components/foundation/ambiq_gpio_config/gpio_state.c and radio_board.c with reusable declarations in gpio_config.h. The same ambiq-gpio-config-simulator target builds configuration/state/consumer/actual PRIMASK together; its default output is now build/foundation/ambiq-gpio-board-simulator. Prior config-only evidence and ELF are preserved, as are exact old source snapshots under prior-gpio-config-source. No shared campaign gates or protected firmware source were changed.

## Verified contract

State-write truncates the operation to eight bits. Operations 0–5 are output clear, output set, output toggle, output disable, output enable and enable toggle. Unknown operation bytes return 0 without MMIO. There is no pin-range check: bank=(pin>>5)&7 and bit=pin&31. Direct set/clear commands preserve incoming PRIMASK; the two read/XOR/write toggles save/mask/restore it. All cases return 0.

The physical register families contain seven words, ordered RD 0x404, WT 0x420, WTS 0x43c, WTC 0x458, EN 0x474, ENS 0x490, ENC 0x4ac relative to GPIO base 0x40010000. Bank 7 reaches the next register family, while pin 256 wraps to bank0/bit0. These invalid-input address aliases are explicitly diagnostic; they are not validated physical pins. Readable reconstruction, layout and ABI details are in pseudocode.md.

The radio consumer's first write is WTC2 at 0x40010460 with mask 0x20000000 and incoming PRIMASK. It then validates pin 138/raw 3 and performs PADKEY0x73→PINCFG138=3→PADKEY0 under PRIMASK 1, restoring the previous mask. The two calls are not one atomic section. Injected rejected raw 0x800/0xffffffff still leave the earlier clear command observable, with no key/configuration writes and no rollback. Those injected values are synthetic perturbations; stock contains3, so this is not evidence of an actual hardware failure.

The public state operation type is a byte. The raw-u32 adapter performs explicit conversion before calling the unchanged SDK body, matching stock UXTB without violating C's byte-argument ABI. Configuration remains four bytes passed by value; the radio source explicitly loads its volatile raw word before synchronous use. No asynchronous buffer ownership exists within this chain.

## Concrete failure resolved

The first complete comparison failed on state operation0. The newly added compatibility struct and model had incorrectly ordered EN/WTS/WTC after WT. Stock disassembly, its literal pointers and the pinned primary apollo510.h register type agreed on WTS/WTC/EN. Correcting those offsets fixed actual source MMIO behavior. The original SDK body, enum meanings, stock instructions and validation assertions were retained. The failed log, original wrong source/verifier and wrong ELF are preserved in failed-first-comparison.log and failed-first-source. No failure was silently dropped.

## Fresh validation

The corrected O2 source ELF passes 16,108 fresh stock/source/independent-model cases: 912 getter, 8,392 setter, 6,708 state-write and 96 consumer cases. Cases include every logical pin0–223 and all six state operations under both prior masks, direct commands/toggles, preserved register bits, raw operation truncation/no-op values, boundary/alias addresses, external output-active masks and synthetic rejected board configurations.

The comparator preserves ordered MMIO reads/writes and mask-at-access, nested call arguments/order, complete modeled register state, output guards, SP and R4–R11. Board R0 is intentionally unspecified by its void ABI rather than treated as a status. Original/source instructions execute with no executable call stubs; actual PRIMASK code is linked. The code hook binds every executed instruction to unchanged original/source segment bytes.

Every declared new body byte executes:218 state-write and 24 radio bytes. With prior getter/setter 156 and shared critical 8, this profile observes 406 unique original bytes. Deduplication against all earlier passing foundation evidence adds 242 bytes, raising 4,322→4,564 (touch 234, Apollo 4,330). Data, statically inspected callers, failed executions and duplicate shared helper bytes add no credit. No new compiled body byte-equality claim is made.

The fresh 42-module aggregate passes 215 methods, with 6 method skips and 1 separate setup skip (221 executed method tests,7 skip records); failures/errors are zero. Six component methods pass, including unchanged SDK state/macro provenance, real provider linkage and byte-operation ABI conversion. The initial system-Python aggregate lacked Capstone; its failed log/result are preserved as aggregate-system-python-failed.*. Repeating in the installed project environment resolved that prerequisite rather than skipping the module.

Exact compiler/source/ELF/result hashes are in build-provenance.json; counts are in validation-summary.json, original identity/disassembly in original/, and deduplicated evidence in cumulative-inventory.json and new-code-evidence.jsonl. Independent review passed with no remaining implementation blocker, including a fresh 208-case stock/source/model rerun. Its sample observes 344 original bytes; complete declared-body coverage is established by the full comparison above. Review report and results are under review/.

## Practical limits and next work

This provides reusable GPIO state/configuration interfaces and the actual radio board consumer needed for further reconstructed radio startup/shutdown code. It establishes software ordering, masks and synchronous ownership. Register set/clear effects are synthetic device fixtures based on primary register documentation; physical output-enable derivation is supplied as an external mask, not inferred from EN alone. Command-register readback latches are synthetic. Electrical state, settling, pinmux/mux-enable interaction, clocks, NVIC, complete radio lifecycle and asynchronous hardware behavior remain unproven.

Foundation source/header count is 64; all prior59 files remain unchanged. Source count is not firmware completeness. Zero of six payloads is established source-complete, and no source-built byte-identical bundle is proven. The independent optimized tick memory-hook execution blocker remains explicitly retained, with its original failed artifacts unchanged.

A useful next bounded consumer is the radio startup reset/SPI GPIO sequence, or pin 103 configuration save/restore around flash setup. Complete shutdown safety still requires lifecycle and hardware evidence; this batch does not clear that boundary. No commits, staging, flashing, deployment, device access or security changes occurred.
