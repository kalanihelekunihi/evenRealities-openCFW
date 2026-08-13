# G2 CMSIS-FreeRTOS kernel-state source candidate

Status: source-integrated in the Apollo-main production overlay

`osKernelGetState` occupies `[0x0044906C,0x00449094)`: 40 bytes, SHA-256
`279b1f9ba1e6f1a319637906efa9c1dd9ccbc54e5e343ed60f351d0add2e4dda`,
with two external callers. Stock calls the already source-owned
`xTaskGetSchedulerState` provider and, only for the not-started scheduler
state, reads the CMSIS `KernelState` word at `0x20074384`.

The 1,741-byte Apache-2.0 candidate has SHA-256
`4a8af24ddb5a0bd0449322f98a681c9903eb6406739a27153cac9b4cccf2e34f`.
Apple Clang emits 38 bytes, SHA-256
`bdb63a444adb684059befa22bd854d08db9b8dba7b122c436f2de048ae6d3ab0`,
with one Thumb call relocation. The fixed CMSIS state address is encoded
directly; no TCB field is read. Host tests cover running, suspended, ready,
inactive, and unexpected pre-start wrapper states.

The complete stock span is now redirected to the source leaf. Apple places it
at offset 131,652 (`0x007B4568`) with linked SHA-256
`7b4328e12ec4d911c8ae88820c2bf73f661ab233bd144ef57e478037809a7ff7`;
Linux places it at offset 133,520 with linked SHA-256
`b0cd0bb92000f35609928d234c561af59ddfee0d4036641e2674a35c93563b2f`.
The fixed word is now coupled to source-owned `osKernelInitialize` and
`osKernelStart`; both writers were admitted atomically in the separate
[`kernel-lifecycle audit`](cmsis-freertos-kernel-lifecycle-source-audit.md).
