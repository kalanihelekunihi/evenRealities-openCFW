# UART grouped-power offline providers

Reconstructed UART-specific subset and repeated callback/poll behavior; no original executable blob. Reuses prior descriptor data/source unchanged. [Report, correction and limits](../../../analysis/audio-uart-group-power-2026-10-09/REPORT.md). Callback bodies are cut; delay status transitions are synthetic. uart_group_can_poll only claims UART domains11..14 and byte-wrapped equivalents, not other power groups. This is not a production HAL or full shutdown implementation.
