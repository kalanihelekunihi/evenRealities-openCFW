# CMSIS-FreeRTOS message-queue put source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

`osMessageQueuePut` is production source-owned from CMSIS-FreeRTOS v10.5.1
commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` under Apache-2.0. Its complete
stock entry `[0x00449ABE,0x00449B3C)` is 126 bytes with SHA-256
`aba43426edc09754ce5ae6c619ba1bfe1f5ad0f0f36687b4315db9dc32a48998`.

The adapter preserves ignored message priority, IRQ/task dispatch, ISR
zero-timeout validation, resource-versus-timeout status mapping, and the
conditional PendSV request. The task call binds to source-owned
`xQueueGenericSend`; the ISR call binds to the newly closed generic ISR-send
chain. The Apple and exact-root Linux leaves are both 144 bytes, at offsets
`134284` and `136160` in their respective overlays.

Hosted tests pin parameter ordering, provider arguments, result mapping, and
PendSV behavior. Target tests pin stock bytes, compiler bytes, relocations,
dual-profile placement, and manifest admission. No image was signed or flashed.
