# CMSIS-FreeRTOS semaphore-acquire source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

`osSemaphoreAcquire` is production source-owned from CMSIS-FreeRTOS v10.5.1
commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` under Apache-2.0. Its exact
`cmsis_os2.c` blob first appeared at
`13acfbef7be85119fc6bc56832c455d4547d92c7`; this remains a source baseline,
not proof of a unique Even checkout.

The complete stock entry is `[0x0044994E,0x004499B8)` (106 bytes), SHA-256
`c433dde9706e80eb67706ed801cbf64b544c39c88bab6a946d0fdcd02c23c700`,
with five external callers. Its three executable dependencies are now all
source-owned: private `IRQ_Context`, the V10.5.1 task-side semaphore-take
provider, and `xQueueReceiveFromISR` for the `xSemaphoreTakeFromISR` macro
path. PendSV is an architectural register write, not an opaque callee.

The 108-byte unrelocated target has SHA-256
`fc7ce83a71cb739e35ce79c2fbf5ca918b4d93b8b66bc4444ad28b0dd5ce2c91`.
Apple links it at overlay offset `133292` with SHA-256
`b2507700dbaf383fe30cf380b81e6c0bf37ccd49af692aed38c77299eaa2e8cc`;
Linux links it at `135164` with SHA-256
`97a333e6e5d71ea8ca1ab54bc909d12a338f7230a669420770ed6a4ebd5709b7`.

Six focused tests cover null handles, ISR timeout rejection, ISR
success/resource/PendSV behavior, task success/timeout/resource mapping,
source and stock hashes, target relocations, and production placement. No
hardware was operated.
