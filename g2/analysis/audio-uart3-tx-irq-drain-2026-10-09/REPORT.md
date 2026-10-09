# UART3 queued TX interrupt drain

**40 original/source compositions PASS** through common channel IRQ body
`0x55E2CE`, original HAL interrupt status/clear/service, and original or native
TX state machine `0x58E534`. [Results](results.json) reuse the exact sealed UART
TX ELF and source receipt from `audio-uart-tx-ownership-2026-10-09`.

The fixtures bind channel 3 to HAL state `0x2006A380`, its initialized 1,024-byte
TX queue at `0x200BA420`, and UART3 registers at `0x4003C000`. Status bit `0x20`
enters HAL TX service. With no active borrowed transaction, service still drains
the already-owned software queue into the FIFO until the queue is empty or
synthetic TXFF becomes set. Queue read index and length advance with exactly the
bytes written. Cases cover queue lengths 0/1/3/8/32, FIFO budgets 0/1/2/full,
and status `0x20`/`0x21`.

Status bit `0x01` independently sets the channel completion byte and HAL
last-TX-complete marker. It does not imply that queued bytes were physically
transmitted. The application request path's successful blocking admission is
therefore safe to reuse its source buffer because UART3 queue-add copied those
bytes, while completion remains a separate interrupt marker.

The fixture directly enters the common IRQ function with supplied status and
FIFO readiness. It does not execute a vector, NVIC exception entry/return,
peripheral clocking, electrical transmission, or real interrupt timing.
