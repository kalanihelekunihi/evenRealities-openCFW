# Offline codec UART lifecycle reconstruction

Reconstructed ring initialization, callback registration, channel enable/disable/baud, codec initialize/close/baud, host initialization and thin RX callback. Fixed ARM addresses and log-disabled behavior are explicit. Power, GPIO and configure remain external providers; this is not production firmware or hardware quiescence proof.

[213 original/source comparisons and retained-ring/error behavior](../../../analysis/audio-codec-uart-lifecycle-2026-10-09/REPORT.md). Ring write/drain bodies are reused unchanged. `lifecycle.h` is the recovered helper interface. Non-power-of-two ring assertion paths remain outside this source contract; size0 state initialization is tested as a degenerate software edge, not a usable queue.
