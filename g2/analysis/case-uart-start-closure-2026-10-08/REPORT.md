# Case receive-start API: validation, caller buffer and interrupt selection

**2,312 fresh original/independent/public cases PASS**:2304 full HAL_UART_Receive_IT API cases and8 direct internal UART_Start_Receive_IT cases. Independent [start.c](../../components/case/uart_start_offline/start.c) reconstructs080064ec/08008d98. Official v1.4.5 bodies and authentic UART_MASK_COMPUTATION macro execute as third comparator with explicit ARM32 context/macros. No function-entry stubs. Original ISR pointers are stored/compared as ABI metadata; these setup functions never invoke them.

## Caller-facing contract

API first requires RxState+8c==20(READY), else returns2(BUSY), before buffer validation. Null pData, count0, and odd-aligned pData when WordLength1000(9-bit)/Parity0 return1(ERROR) without setup. Handle itself must be coherent/non-null; no handle-null guard is claimed. Success sets ReceptionType+6c=0, enables CR1.RTOIE4000000 if USART1 CR2.RTOEN800000 is set, then invokes full internal helper and returns0. Tests cover valid7/8/9-bit settings, parity0/400, FIFO modes, thresholds/counts, null/even/odd pointers, state, timeout and PRIMASK. USART1 address40013800 only; no cross-device/LPUART behavior inferred.

The internal helper directly stores **the caller's pData pointer** at+58, Sizeu16+5c and remainingCountu16+5e, clears RxISR, computes mask, clears ErrorCode and sets busy22. It allocates/copies no buffer and does not reset RxEventType+70. It assumes validation was already performed: direct constructed null/count0/busy-state calls still return0 and program state. Those8 tests establish the lack of guards, not application reachability or safety.

Mask table:9-bit/no parity1ff;9-bit/parityff;8-bit/no parityff;8-bit/parity7f;7-bit/no parity7f;7-bit/parity3f. Public header macro is preserved verbatim. Size counts data elements;9-bit/no-parity elements use16-bit storage. Buffer capacity cannot be inferred from Size alone.

## Selected handlers and partial hardware state

Helper always enables CR3.EIE1. If FifoMode+64==20000000 and Size>=NbRxDataToProcessu16+68, it selects FIFO16BIT08008809 for9-bit/no-parity, otherwise FIFO8BIT08008a49; parity enables CR1.PEIE100, and CR3.RXFTIE10000000 is enabled. Otherwise it selects plain16BIT08008759 or8BIT08008999, enabling CR1.RXNEIE20 plus PEIE100 if parity. Register operations OR bits rather than clearing old enables. Tests start with unrelated flags to check retention. PRIMASK is1 at every atomic register write and restored afterward.

The selected pointer is metadata, not retained executable content in a production image; these offline functions intentionally reproduce the stock ABI for tests. No source-only firmware build or byte equality follows. Physical UART delivery, FIFO consumers, cancellation, DMA and allocation are not exercised.

## Application relevance and revision controls

Actual product parser08006544 rearms through64ec with fixed handle20000e24, scratch byte20000108 and count1 (static evidence from authenticated literals). This means parser rearm can receiveBUSY/ERROR instead of installing a new receive. Parser posts event40 when rearm returns nonzero, and event8 for completed frames; those downstream event/scheduler semantics still require their own original-instruction tests. The parser is not part of2312 cases.

24 held-out revision controls in valid-event-revision-results.json set RxEventType2(IDLE), rather than the arbitrary55 sentinel in the prior broad receive fixture. Eight candidate observations agree,16 disagree: v1.4.5 agrees for both widths/timeout states;1.4.0/3/4 disagree;1.4.6/7 agrees when RTOEN is clear and differs when set. This strengthens the selected-body behavior discrimination without a unique-producer claim or global re-pin. Prior5120 receive tests and corrected6768 IRQ/helper tests are separate suites; inherited or superseded counts are not added as new coverage here.

Reproduce build_offline.py --gcc <ArmGNU13.3> --output <scratch>, then venv Python verify.py <scratch/start.elf>. Run verify_revision_valid_state.py <sealed receive ELF> for held-out controls. Official source/header/macro/compiler/ELF hashes are in reproduction-receipt.json. Header Apache license is authenticated and retained in CMSIS-G0-LICENSE.md for the earlier preserved CMSIS file; official HAL BSD license matches existing retained ST-LICENSE.md exactly. No commit/index/production/device writes.
