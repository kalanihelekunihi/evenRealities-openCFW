# Case UART receive helpers: revision discrimination and caller buffers

**5,120 original/independent/public v1.4.5 comparisons PASS**, plus10 rejected revision controls (8- and16-bit bodies from1.4.0/3/4/6/7). Independent [receive.c](../../components/case/uart_receive_offline/receive.c) reconstructs8-bit08008998 and16-bit08008758. Full helper bodies execute through completion-call boundary; **the product completion bodies are excluded**, not silently considered no-ops. Original code stops before first instruction08006544(parser) or08005e6a(event callback). Compiled source/public callbacks supply explicit boundary markers. Tests compare handler/register/guard-buffer/marker state, ordered MMIO writes including PRIMASK at atomic updates and restored PRIMASK.

## Payload and lifetime

Handle ABI: pRxBuffPtr+58, RxXferSizeu16+5c,RxXferCountu16+5e,Masku16+60,ReceptionType+6c,RxEventType+70,RxISR+74,RxState+8c,ErrorCode+90. Busy RX=22; ready=20. If not busy, helper writes RQR|8(flush request) without writing caller buffer/count. If busy, it reads RDR+24, applies mask, stores one byte or little-endian halfword, advances pointer by1/2, decrements count modulo65536. **Initial count0 wraps to65535 after writing; no zero-count/buffer-capacity guard exists in this helper.** Tests supply allocated/aligned buffers and one invocation; no real overflow/reachability claim.

When decrement reaches0, it atomically disables CR1.PEIE/RXNEIE mask120 and CR3.EIE1, restores ready state, clears RxISR, sets RxEventType0(TC). Unlike EndRxTransfer, this completion does **not** clear CR3.RXFTIE. Buffer pointer remains advanced, not reset/freed. Standard mode calls the actual product frame parser at08006544. TOIDLE mode resets ReceptionType0, disables IDLEIE10, clears ICR.IDLE16 only if ISR.IDLE was set, then invokes event callback with original u16 requested size. Parser rearm and event consumers are external to these tests.

## Official source screen

Official annotated tags were resolved to immutable commits and UART source files preserved with BSD license. Initial raw requests using tag-object SHA returned404; only peeled commit files were accepted.

| Release | Commit | Proven difference/assessment |
| --- | --- | --- |
|1.4.0|e84a576c18bf5806d43bf45fe0f8d7007ff8e6c2|Control rejected: non-atomic clear and missing later IDLE/event details|
|1.4.3|38df07685b03ab758d2374ff56edbbf20ba829c8|Control rejected: leaves RxEventType sentinel unchanged|
|1.4.4|3e7e57636112b59a7c88babb18de3070262a51ae|Body hash identical to1.4.3; same rejected event-state behavior|
|1.4.5|ba4210f57d3c863d31ace271219a12f43ab59847|5120 scoped comparisons pass|
|1.4.6|e194e5abc3a125ef08434f1ee122a2bc7b3d9af4|Control rejected: when CR2.RTOEN is set, clears CR1.RTOIE on completion; stock does not|
|1.4.7|a0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9|Body hash identical to1.4.6; same rejected timeout behavior|

This discriminates selected **behavior**, not whole firmware producer version or exact opcodes. Untested patches/forks may share these bodies. Existing HAL gitlink remains1.4.7 and is not globally re-pinned: error prefix compatibility and RX-helper differences must be kept separate. The source receipt pins1.4.5 specifically for these functions. submodule-proposal.json records an isolated candidate reference; no index/gitlink changes.

CMSIS G0 header from registered pinf576c24 verifies CR2.RTOEN bit23 and CR1.RTOIE bit26, source hash retained. It does not prove exact G0B1 hardware identity. Tests use USART1 address40013800 and synthetic RDR/ISR/SFLASH-free memory, not physical FIFO or interrupts. Both requested CR2 states are covered, with CR1.RTOIE set initially, so the later-release mismatch is exercised rather than masked.

## Next actionable interface

Actual IRQ wrapper08008f98 uses handle20000e24. Product parser08006544 assembles5A/A5 framing plus7F(one-byte length) orCF(two-byte little-endian length), performs some blocking bulk reads, posts event8 and rearms one-byte receive via080064ec. This paragraph is static corpus/disassembly interpretation pending its own instruction validation; it is not part of5120 cases. HAL start/rearm and product frame/event handling remain actionable source leads, as do the separate project-wide Cordio/LVGL/storage/codec ledgers. No project-wide source exhaustion is claimed.

Reproduce build_offline.py --gcc <ArmGNU13.3> --output <scratch>, then venv Python verify.py <scratch/receive.elf>. Receipts bind all official commits/source/body/environment/compiler/ELF hashes. No production/index/commit/device writes; no hardware buffer-safety, whole-handler or source-completeness claim.
