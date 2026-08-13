# CMSIS-FreeRTOS message-queue get source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

`osMessageQueueGet` is production source-owned from CMSIS-FreeRTOS v10.5.1
commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` under Apache-2.0. Its complete
128-byte stock entry `[0x00449B3C,0x00449BBC)` has SHA-256
`ba577117e8cc2833921c4d0ab5f8dcf8122fab6090ccb32571ff62231dfd52ba`.

The adapter preserves ignored message priority, IRQ/task dispatch, ISR
zero-timeout validation, resource-versus-timeout status mapping, and
conditional PendSV. Its ISR dependency is the prior source-owned
`xQueueReceiveFromISR`; its task dependency is the newly closed
`xQueueReceive` chain. There is no remaining opaque dependency in either
branch.

Apple and exact-root Linux emit identical 132-byte unrelocated bodies at
overlay offsets `135160` and `137036`, with independently pinned linked
hashes. The resulting packages are `4437182` bytes / SHA-256
`945adee4721dda4dcee484baee56e96a3a8373e3bb6b08a0ec50ae1f65572308`
and `4439058` bytes / SHA-256
`ad8cbdfdf14abbd80ae1b0ae4aed3e6c979f9985d0c34b332b63d1ad3c8f245a`.
This is the 30th of 38 linked public CMSIS APIs; all five linked private
helpers are also source-owned. No image was signed or flashed.
