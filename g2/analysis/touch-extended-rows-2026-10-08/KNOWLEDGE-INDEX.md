# Current bounded storage and power knowledge

| Directory | Recovered behavior | Explicit boundary |
| --- | --- | --- |
| ../touch-callback-ownership-2026-10-08 | Static16-byte buffers; callbacks/publish slice; ownership | Synthetic descriptor interruption, no hardware-fault claim |
| ../touch-commands-2026-10-08 | All command branches; deferred restart/configuration write | Sensor counts bounded; reset/EEPROM entry cuts |
| ../case-stop-mode-2026-10-08 | STOP0/STOP1 sequencing | WFI/WFE controlled wake |
| ../case-clock-poll-2026-10-08 | Voltage scaling/VOSF retry budget | State injected by read count, no physical microseconds |
| ../touch-eeprom-dispatch-2026-10-08 | Corrected write dispatch; stock simple write direction | Earlier row-provider cuts |
| ../touch-flash-provider-2026-10-08 | Actual provider callbacks, discarded errors, flash/clock/status flow | SROM only synthetic for normal provider chain; generic gate tests cut callbacks |
| . | Extended orchestration, checksum+1 span, command7→deferred outcomes | Three history cuts; SROM synthetic; scheduling constructed |

Only new standalone modules are linked. Accepted integrated firmware checkpoints and sealed prior evidence are preserved. Per-suite case counts are not additive whole-image coverage. Remaining integrity/history/merge algorithm recovery is actionable; physical ROM/storage/scheduling remains a separate missing-input boundary.
