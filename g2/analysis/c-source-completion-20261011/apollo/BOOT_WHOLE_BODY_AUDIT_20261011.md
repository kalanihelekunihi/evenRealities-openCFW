# Apollo Boot whole-body audit checkpoint

The combined experimental relocatable Boot graph in
`g2/build/c-firmware/20261011/channel-indirect-font-round/receipt.json`
defines 908 symbols and leaves three unresolved resident ROM APIs:
`opencfw_boot_rom48`, `opencfw_boot_rom_delay_cycles`, and
`opencfw_boot_rom_mram_program`. Those are hardware ROM contracts, not evidence
of missing firmware-owned implementations. This is a source compile/link result,
not a complete loadable boot image or device result.

The locked catalogue has 903 recognized function entries (849 with retained
raw pseudocode and 54 without). A fresh 337-unit/917-provider selected-source
archive includes the newly recovered thread-name getter and separate source
symbols for selector callbacks 24, 25, and 26. It also includes the UART IRQ
receive drain and the independently implemented Boot overlap copy. The prior
336-unit archive linked with three experimental objects at 919 defined globals
and the same three resident ROM imports. The new 337-unit archive compiles;
its combined linker result needs a fresh hash-bound coordinator receipt.
The conservative
crosswalk against that archive now has 376 entries without a machine-body
attribution lead, down from 421 before this audit. The 376 stock envelopes
sum to 20,724 bytes; this sum is a triage
measure, not a count of missing source bytes or unique uncovered image bytes.
Several of these entries have selected source already: the clock-select5 body
and inlined `ftoa`, tick-step, RTOS event/mutex/timer/queue/ISR bodies were
crosswalk omissions. The latter source bindings are attribution leads, not
whole-domain equivalence proofs. The class-5 clock entry has seven bounded
original/source cases. Earlier pinned formatter probes cover 1,778 cases,
but their source hash differs from the current selected source, so that older
receipt does not certify the current source snapshot.

The source scatter adapter reconstructs 24 ITCM bytes, 1,371 initialized SRAM
bytes, and 4,096 zero SRAM bytes. The earlier bounded oracle compared 1,235
initialized SRAM bytes exactly and normalized 136 bytes of 34 callback
relocations. `verify_scatter_callback_relocations.py` now binds all 34 selected
source symbols to their authenticated stock pointer values and compares all
1,371 initialized bytes exactly, with zero normalized bytes. This validates
source data layout under that explicit placement. Final loadable source
placement of those callbacks, source-owned tables and ITCM helpers,
and a full code/data/scatter partition remain open. The selected archive's
Cortex-M55 compilation and Cortex-M4 bounded emulator result have separate
scopes.
`audit_scatter_placement_fit.py` measures the final selected object functions
against the original callback envelopes. All 34 callbacks have compiled source
symbols; 29 have direct stock catalogue envelopes, and 10 selected source
functions are larger than their stock envelopes. The current linker places
generic `.text` at `0x10000`, while the bounded scatter oracle forces 34
stock pointer values with `--defsym`. The ten oversize functions cannot simply
be dropped into their old slots from these exact objects. A final source image
needs its own address layout and table relocations, or separately qualified
smaller implementations; this size audit does not prove placement for the
other 24 callbacks.

The stock 0x418372 thread-name getter was a genuine missing selected body.
`thread_name_getter.c` now implements its null-to-current-TCB fallback,
fatal-null path, and TCB+0x34 return; three bounded nonfatal stock/source
cases pass. The selected architectural SVC veneer already owns 0x41b374,
although real exception entry remains outside this oracle.

The stock 0x4276bc overlap-copy runtime had no selected source provider.
`runtime_memory/boot_memmove.c` now implements directional copying; 2,016
stock/source cases pass exact 96-byte memory, SP, and return-control
comparisons over overlapping/nonoverlapping source and destination offsets,
alignment and lengths. The native body is void and leaves incidental R0 values
that differ by path, so this oracle makes no R0 equivalence claim. No physical
memory or DMA behavior is inferred.

The stock 0x41f776 UART IRQ RX drain was also missing from selected source.
`uart_irq_rx.c` now composes the existing source FIFO child, row descriptor
state, optional callback and count reset. Six bounded stock/source cases pass
across empty, ready, error, zero-limit and notify paths. The caller at
0x41f558 also passes six bounded status/row-flag/call-order cases with child
calls deliberately cut. Wider UART IRQ side effects remain for review.
The stock 0x42372a UART IRQ status leaf is now selected. Six bounded native/C
cases pass, including null and invalid contexts, raw/enabled status and two
modules. Native code reads the module word before checking for null; the C
source preserves that access order. Physical MMIO effects are untested.
The selected UART IRQ chain now also includes row caller 0x41f558, dispatch
0x42377c and DMA leaves 0x422d20/4c/7a plus recovery 0x422fde. Its current
bounded native/C suite passes 16 cases, including timer-inactive and
timer-active recovery with FIFO/cancel at controlled child cuts. The two
timer-active cases compare the stock/C delay argument and resulting SRAM/MMIO
state. Callback side effects and asynchronous IRQ behavior still need full
integrated qualification.

Next body work should start by reviewing the 376 unbound catalogue entries
against current selected source and actual native instructions. Address
proximity or a catalogue lead alone cannot establish a missing body. All
376 current unbound entries have retained raw pseudocode, but no machine-body
crosswalk. This audit added reviewed candidate bindings for 0x428a94 (selected
PCM22 state-7 timer child), 0x41090c (upstream LittleFS `lfs_bd_prog`),
0x4110f8 (upstream LittleFS `lfs_dir_getread`), and 0x4232c8 (selected UART
FIFO). These are attribution leads, not whole-body
equivalence receipts. The unmatched cases need semantic review before
duplicate implementations. Whole-path branch coverage
and output hardware timing
are separate qualifications.

The callback-table audit found a real collision: stock selector 24/25/26
entries are distinct pointers `0x42a031`, `0x42a033`, and `0x42a035` into
three separate two-byte `BX LR` bodies, but the prior source table pointed all
three at selector 24. The selected C source now defines separate 25 and 26
naked callbacks, and the table relocates to those symbols. Selected compiler
output for each function is exactly the two-byte `BX LR` instruction. The
bounded linker with halfword input-section alignment places those three C
functions at `0x42a030/32/34`; its six bytes and three Thumb symbol values
match stock exactly. The remaining callback addresses are assigned explicitly
for this data oracle, so a final linker must place their bodies coherently.

## Co-placed source and current reachability (2026-10-11)

The later `boot_coplacement_experiment.ld` and `build_boot_coplacement.py`
link the selected C/assembly archive at `0x410000` with live source symbol
relocations. `boot-coplacement-locale/receipt.json` records a successful
140,288-byte source ELF from 343 selected units and 934 provider names. All
256 vector words are checked against the authenticated vector shape, including
10 distinct source IRQ handlers. The 1,371-byte initialized object has 34
function callback relocations and 10 locale-string relocations to live source
symbols. The source image does not require stock addresses for the scheduler
idle entry, manager/event thread and timer callbacks, locale strings, or six
stream mode strings. The mode-string oracle compares the pointed-to bytes in
4,099 native/source flag cases after relocation. The manager task is an
explicit linker root because scheduler execution via a control block is not
statically visible to section GC.

The actual package validator rejects Boot data ending beyond `0x438000`, the
main execution base (`g2/tools/open_cfw.py:737-749`). The conservative source
linker ends at `0x437fe0` to reserve the 32-byte main OTA preamble coordinate
identified in `g2/docs/reference/memory-map.md`. This yields 163,808 bytes
from `0x410000`; the current linked source has 23,520 bytes of headroom. The
stock file occupied only 148,599 bytes, so its length is not the partition
capacity. `boot-reachability-audit.json` records 660 of 934 selected provider
names in the GC-linked ELF and 274 removed names. An otherwise identical
no-GC link exceeds the conservative partition by 5,156 bytes. Removed names
include optional LittleFS APIs and potentially unmodeled asynchronous code;
their count does not measure functional completion. Additional live roots,
source size work, and final placement remain open.

The regenerated `boot-body-crosswalk-current.json` has 903 catalogue entries,
368 with no machine-body attribution and 535 with varied source leads. These
leads and a successful ELF link do not establish full native-body equivalence,
physical ROM/IRQ behavior, application handoff or flashable firmware. Earlier
counts in this document describe older snapshots.

### Subsequent source reachability and data relocation

The current co-placement receipt supersedes the earlier 140,288-byte and
152,524-byte checkpoints: 346 selected units expose 966 provider names, and
the linked ELF is 154,720 bytes under the conservative 163,808-byte Boot
partition bound (9,088 bytes headroom). Section GC retains 785 provider names
and omits 181; `boot-reachability-audit.json` records an all-selected no-GC
overflow of 6,200 bytes. Neither number is a count of missing bodies. Compiler
inlining, optional library APIs, and possibly lost asynchronous reachability
all contribute to the difference.

The startup scatter walker and four-record callback runner now address their
source-defined record tables through relocations. Their chosen callbacks,
manager task entry, idle/timer entries, timer callback and task-return PC are
live source symbols. Authenticated product data now includes the shared-memory
startup profile, sleep/conditional-power words, ADC descriptor/power words,
manager and DFU names and attributes, CMDQ register rows, runtime mode values,
GPIO descriptors, five NOR/LittleFS failure formats and 21 initializer/ADC/I2C
log strings. `verify_boot_coplacement.py` checks byte equality for each source
string/data extent and the named pointer relocations it can observe.

The selected-source scan now finds only two stock-flash-coordinate literals:
`0x410000` is the required VTOR vector base; `gpio_descriptors.c` still reads
its native `0x43409c` IRQ lookup in a generic descriptor path. The source
four-entry IRQ table matches the first eight stock bytes, but a caller can
provide a pin whose `pin >> 5` exceeds 3, and native code would read adjacent
non-IRQ bytes. The pinned 97-row product descriptor has no type-2 row with
both nonzero interrupt mode and callback, so that lookup is not exercised by
that table. The generic API's out-of-domain behavior is intentionally left as
an explicit qualification boundary rather than given an invented range guard.
The source scan covers selected `.c` and `.S` textual hex literals; it is not
proof that all decimal, generated, runtime or linker references are correct.
