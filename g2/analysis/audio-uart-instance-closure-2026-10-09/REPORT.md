# UART worker instance initialization

**16 original/source comparisons PASS** for first-party body
`0x541A2E..0x541A86`. [Results](results.json), [ELF and source hashes](reproduction-receipt.json),
and [readable reconstruction](../../components/audio/uart_instance_offline/instance.c)
retain the exact evidence.

The function calls CMSIS `osThreadNew` with handler `0x5417D7`, NULL argument,
and attribute record `0x75C1EC`, then stores the returned thread handle at
`0x20074B0C`. The recovered static attributes are:

| Field | Locked value |
|---|---:|
| name | `uart_sync_thread` (`0x7846A8`) |
| control block | `0x20072530`, 112 bytes |
| stack | `0x20370E40`, 4096 bytes |
| priority | 42 |
| attribute bits / TrustZone / reserved | 0 |

A non-NULL handle returns zero. NULL returns `-1` after optional diagnostics.
Log flag bit1 gates the detailed source/function/line197 error; bit0 or bit2
gates compressed message `[sync.module.uart]Failed to create uart sync thread`.
The comparison covers all eight flag combinations and NULL/non-NULL thread
returns, including exact call arguments and stored handle.

CMSIS thread creation and both logging sinks are explicit supplied boundaries.
The test does not execute the created worker, deliver an exception, start the
scheduler, or establish live task creation. It closes the wrapper and static
configuration only.

The preceding UART TX ownership batch already closed blocking/nonblocking
transfer, synchronous-copy versus retained-borrow behavior, queue/FIFO state,
completion markers, HAL initialization, and initialized SRAM in 665 cases.
This batch deliberately adds only the previously uncovered first-party wrapper.
