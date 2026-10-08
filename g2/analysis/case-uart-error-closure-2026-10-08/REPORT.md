# Case UART RX/error decisions and transfer termination

**6,768 fresh original/independent/public cases PASS**:6,480 selected IRQ RX/error-prefix cases and288 full EndRxTransfer cases. Independent [uart.c](../../components/case/uart_error_offline/uart.c) reconstructs target08005f50 prefix and080086f4 helper. Official STM32 HAL UART source at pinned a0cf8a8(v1.4.7) was downloaded directly and preserved with BSD license/hash. Full helper and verbatim IRQ prefix compile in an explicit target ARM32 environment. This is a comparator revision, not producer identification or exact-byte reproduction.

## Received-error semantics

IRQ reads ISR(+1c), CR1(+0), CR3(+8). Error mask80f includes parity1/frame2/noise4/overrun8/receiver-timeout800. No-error RXNE20 with CR1.RXNEIE20 or CR3.RXFTIE10000000 invokes RxISR if installed and returns. Errors need at least one corresponding interrupt gate to enter error handling; disabled error flags alone do not imply software error reporting.

ICR writes clear hardware flags individually, in parity/frame/noise/overrun/timeout order. Software ErrorCode+90 bits are parity1/frame4/noise2/overrun8/timeout20: **hardware frame/noise bits differ from software error flags**. Prior ErrorCode is ORed, not cleared on entry. Parity requires PEIE100, frame/noise EIE1, overrun RXNEIE or RXFTIE/EIE, timeout RTOIE4000000. If resulting error is nonzero, enabled RXNE invokes RxISR before deciding whether to terminate. Compiled synthetic callbacks observe or clear/set software errors; comparisons prove the decision rereads post-callback error state. These supplied callbacks do not prove real application callback behavior.

With DMAR disabled, overrun/timeout bits28 make the error blocking: EndRxTransfer runs, then weak ErrorCallback08005f42 executes and error is retained. Parity/frame/noise alone are nonblocking: ErrorCallback executes, then ErrorCode becomes0 and receive state/pointer remain. Actual stock ErrorCallback is BX LR (no-op), and that original function executes on all sides; hooks only observe error values at entry. This does not establish application retry/rearm behavior or physical loss of data.

EndRxTransfer atomically clears CR1 mask120 (PEIE/RXNEIE), then CR3 mask10000001(EIE/RXFTIE). If ReceptionType+6c==1, it also clears IDLEIE10. Each update saves/restores PRIMASK. It writes RxState+8c=20(READY), ReceptionType=0 and RxISR+74=NULL. **It does not reset/free/copy pRxBuffPtr, count or caller buffer.** Software buffer lifetime remains the caller's responsibility; DMA exclusion and actual pending IRQs still matter for safe reuse.

## Scoped boundaries and next source lead

Original IRQ stops before08006086 when IDLE/TX/wakeup/other handling is reached. Independent/public prefix marks the same boundary. DMAR is clear throughout IRQ comparisons; linked DMA helper aliases are never exercised. Full helper tests allow arbitrary CR3 bits but do not start DMA. Tests compare handle/register/probe state, ordered MMIO writes, actual error-callback observations and PRIMASK; they do not assert instruction/read-count equality.

Actual UART IRQ wrapper08008f98 passes fixed handle20000e24. The actual receive callback family is next: UART_RxISR_8BIT08008998 and16BIT08008758, with completion reaching product parser08006544 or RxEvent callback08005e6a. The latest public1.4.7 receive-completion body includes RTOEN/RTOIE handling absent in stock. Official1.4.0/3/4/6 sources have now been obtained to evaluate that concrete revision difference; no whole-SDK re-pin is justified from this prefix match.

Reproduce: build_offline.py --gcc <ArmGNU13.3> --output <scratch>, then venv Python verify.py <scratch/uart.elf>. Source URL/pin/hash, explicit macro/layout environment, compiler/ELF hash and selected-prefix transformation are in reproduction-receipt.json. Locked wrapped firmware SHA36ca0c... and raw773b6d... are authenticated in results/provenance. No production/index/commit/device changes. No physical UART timing, hardware safety, full handler or whole-source-completeness claim.
