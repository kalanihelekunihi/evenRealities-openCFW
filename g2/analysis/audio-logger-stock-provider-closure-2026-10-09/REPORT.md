# Stock logger providers and actual UART sink registration

**A raw call scan found the actual nonzero sink installer that the failed decompiler output omitted.** At0x541726, function0x54171C installs callback0x5415C3; the literal is0x54177C. Callback0x5415C2 computes string length at0x44A43C and calls channel-write0x55E7FA with channel1, the original buffer pointer and length. The wrapper's transfer call0x58E3F8 matches the pinned Apollo510 UART handle/type routing. This is a concrete UART sink binding path, not an assumed ITM sink or proof that the path ran on a particular live boot.

Current function-census entry0x54171C records decompiled=false with a low-level range-construction error; its callee list already includes setter0x472C7C. Raw BL scanning below0x600FAA independently finds both setter calls:0x4C2B52(zero) and0x541726(nonzero). The current decomp-file-only search was incomplete. Preserve this distinction when using census/inventory labels as source evidence.

## Source closure and validation

Ten selected bodies from pinned local Apollo510 SDK source are copied with unchanged function text and BSD3 notices: poll, debug disable/power/trace disable, ITM disable/flush/notbusy/stimulus-ready/print-ready and TPIU disable. Version text is release_sdk5p1p0-366b80e084. Compatibility definitions bind stock globals/registers/status values; these are meaningful adaptations, not an assertion of whole-file/compiler/SDK producing identity. [Source hashes and unchanged body hashes](source-reference.json) supersede the Apollo3-family-only analogue for these selected bodies.

**681 comparisons PASS** against the final receipt-bound source ELF:573 direct selected-provider cases and108 outer-disable compositions. Existing GPIO setter/getter and PRIMASK source are reused unchanged; no new GPIO closure counted. Top compositions execute the stock enclosing routine/setter plus native ITM/TPIU/debug/poll/GPIO source. Native reached instruction addresses are guarded; all selected internal providers execute source, with four explicit external aliases for delay and peripheral power operations. Those external calls use synthetic return/query stubs. No real power/clock, elapsed-time, scheduling or FIFO-drain inference.

**Nine additional original-instruction checks PASS**: registration prefix through setter/channel callback installation, plus empty/3byte/newline/205byte strings on inactive/active channel1. Registration stops before allocator0x57DEEA. Active sink tests execute actual strlen and56byte transfer zero/init instructions, then stop before HAL0x58E3F8; no HAL-return or physical UART completion fabricated. Inactive channel returns without HAL.

[Exact final ELF and source receipt](reproduction-receipt.json), [provider comparisons](results.json), [sink tests](sink-results.json), [readable data/control flow](pseudocode.md), [reusable native sources](../../components/audio/logger_stock_provider_offline/README.md). This is bounded author validation, not independent review or firmware completeness/byte equality.

## Practical findings

- The stock ITM disable status poll passes mask0, matching SDK's ITMENA & BUSY expression. The recovered poll therefore succeeds on the first read independent of that register's contents; do not call this proof of a drained trace pipeline.
- General debug disable returns its final power-release status, overwriting the earlier retained-debug-reference status; trace-reference release status is ignored by that wrapper.
- ITM/TPIU shutdown's final pin configuration is logical28/raw3, confirmed from literal0x78EE3C and through reused stock-matching GPIO source. Physical pad state is unproven.
- Actual UART channel records have stride28 at0x20000D2C: handle+4, callback+20, active+24, completion+25. The sink constructs56byte transfer with buffer+0,length+4,timeout+12=0,type+52=0(blocking write). It passes the shared formatter buffer directly; copy/consumption ownership requires the UART child, not an inferred asynchronous-buffer fix.
- Channel wrapper waits up to1000 delay calls after HAL, but its return uses HAL status, not independent completion-loop exhaustion. This is static post-boundary evidence only.

## Remaining bounded source leads

Sink installation is now mapped statically through0x54171C; caller0x4C953E performs it before uart_instance_init0x541A2E. No runtime execution is inferred. Startup first zero-fill clears the logger globals, as already proven; it does not install the sink. The separate flag0x20074F4E still has no established later writer: exact-address and ±32byte literal searches do not prove absence of computed writes. Adjacent200742EC at0x5A4FA0 belongs to0x5A4EF4 accessing offset0, not a discovered callback writer. Search evidence is recorded, not closed-world completeness.

Next useful source dependency is UART blocking_write0x58E454 and nonblocking_write0x58E4E8, their queue/interrupt completion path, plus uart_instance_init0x541A2E. Pinned SDK am_hal_uart.c has these source bodies and the transfer ABI. This is actionable work, not an external-input blocker or a claim that broader source search is exhausted. Actual TX completion/copy lifetime remains unresolved until those providers are composed. Existing delay source/evidence should be reused.

All prior seals,110 audit inputs,four checkpoints and staging are checked unchanged in preservation.json. No commits, firmware source edits, flashing or device writes.
