# Offline case UART RX/error prefix

Independent selected IRQ and full EndRxTransfer reconstruction. [6,768-case report](../../../analysis/case-uart-error-closure-2026-10-08/REPORT.md). Fixed ARM32 handle ABI; prefix requires DMAR disabled and stops before other IRQ handling. Synthetic RX callbacks and actual weak error callback, no physical FIFO/scheduling model. Not a production replacement.
