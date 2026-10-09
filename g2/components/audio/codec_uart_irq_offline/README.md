# Offline codec UART IRQ routing

Reconstructed channel IRQ wrapper for stock `0x55E2CE` and its RX callback
delivery subset. HAL status, clear, service, and FIFO reads remain explicit
interfaces. The per-channel RX object has accumulated count at offset `+8` and
staging-buffer pointer at `+12`. See the adjacent analysis report for tested
masks and limits.
