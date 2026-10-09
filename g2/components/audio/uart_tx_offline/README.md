# Offline UART TX source and ownership interfaces

Eleven selected pinned Apollo510 SDK functions retain unchanged text and BSD3 notices: HAL initialize/bufferconfigure, transaction save, blocking/nonblocking write and TX state machine, FIFO write, queue drain, queue initialize/add/get. compat.h is the explicitly adapted stock-layout ABI: one-byte transaction enums,284byte handle stride,56byte transaction and24byte queue.

[Report, provenance, exact build and instruction tests](../../../analysis/audio-uart-tx-ownership-2026-10-09/REPORT.md). These are offline source/knowledge helpers; no production firmware module or complete UART/hardware reconstruction is claimed. The only executable original-address alias is delay0x4807A0, replaced by documented synthetic returns/timing in tests. Physical FIFO readiness and interrupt delivery remain unverified.

Buffer contract: nonblocking entry retains the source pointer until requested bytes have been consumed into queue/FIFO. Transaction completion marks that consumption; software or hardware queued bytes may remain. Stock logger channel1 is configured without a software TX queue and uses blocking write. FIFO acceptance and an observed TX-complete interrupt are different boundaries.
