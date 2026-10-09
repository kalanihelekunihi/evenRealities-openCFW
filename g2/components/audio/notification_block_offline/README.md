# Offline notification block insertion

Reconstructed current-task insertion body for stock `0x455FA8`. It removes a
valid current task from its ready list and inserts its state item into the
current delayed list, overflow delayed list, or suspended list. It does not
perform a context switch or model a resumed wait.

See the [704-case evidence](../../../analysis/audio-notification-block-insertion-2026-10-09/REPORT.md).
This is bounded reconstructed C, not production firmware.
