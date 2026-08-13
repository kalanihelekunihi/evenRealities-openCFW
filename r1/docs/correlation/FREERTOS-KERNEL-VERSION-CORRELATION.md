# FreeRTOS kernel version and Nordic port correlation

The R1 application uses the authenticated FreeRTOS-Kernel 10.5.1 core with Nordic's nRF52
Cortex-M port. It does not use Nordic SDK 17.1.0's bundled 10.0.0 kernel core.

The decisive function is `0x00085440..<0x00085468`, the 40-byte `prvReloadTimer` from FreeRTOS
10.5.1 `timers.c` (SHA-256
`d03d69b29abd0f1d1fd5c818b9cda349717d56534de9709497af868b7cb4b635`). Its loop advances an
already-expired auto-reload timer by its period and invokes its callback until
`prvInsertTimerInActiveList` accepts the next expiry. Its only callers are `0x000852C2` and
`0x00085354` in the recovered 10.5.1 timer paths. Nordic's bundled 10.0.0 `timers.c` has neither
this helper nor the recovered status-byte timer layout. The independently recovered CMSIS wrapper's
10.5.1-specific ISR event-flag behavior corroborates the version.

The exact body and caller set are checked by:

```sh
python3 scripts/firmware/summarize_r1_freertos_kernel_version.py
```

openR1 compiles the authenticated `g2/third_party/freertos-kernel` 10.5.1 core and allocator,
while retaining Nordic SDK 17.1.0's `portable/GCC/nrf52` and `portable/CMSIS/nrf52` sources. The
R1-owned boundary remains configuration and application hooks only; no kernel or port body is
reimplemented locally.
