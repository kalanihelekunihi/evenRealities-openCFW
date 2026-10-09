# Offline UART RX and stream-buffer source

Eight selected bodies preserve public source text: FreeRTOS10.5.1 stream create/spaces/ISR-send/write-message/write-bytes/bytes-in-buffer/initialize, and pinned Apollo510 UART FIFO read. MIT/BSD3 notices retained. compat.h binds stock36byte control layout and config choices; support.c provides bounded reconstructed non-overlap byte-copy/fill and previously explained BASEPRI operations.

[Report, exact build, source provenance and original-instruction comparisons](../../../analysis/audio-uart-rx-stream-ownership-2026-10-09/REPORT.md). Heap and task notification remain explicit external aliases; tests cut or mock their return behavior. No source-complete driver, scheduling or physical UART claim.

RX copy contract: staged UART bytes are copied into the stream ring before ISR-send returns. Stream send may accept a prefix; caller must inspect its return to know what was copied. Stock logger callback ignores this return and the outer flush resets staging count. Copied bytes no longer borrow staging storage; unaccepted suffix is not retained by the tested path.
