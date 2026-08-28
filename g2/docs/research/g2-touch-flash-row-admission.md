# G2 touch flash-row adapters (batch 19)

Batch 19 admits three isolated MIT clean-room adapters totaling 172 shipped
instruction bytes. `0x14B0` writes aligned 128-byte rows from an authenticated
zero-filled scratch buffer, `0x1510` writes aligned rows from a caller buffer,
and `0x1560` is the exact bounded memcpy callback that returns zero.

The two row adapters preserve the authenticated `0x06160002` alignment error,
row size, address/source advancement, and ignored provider return values. Their
write operation remains a typed boundary to the already admitted Apache-2.0
`Cy_Flash_WriteRow` provider. Division and copying use ordinary clean-room C
behavior; no stock bytes are copied.

Every canonical target body and direct call is pinned. Host tests cover ordered
multi-row writes, zero contents, source advancement, alignment/missing-provider
failure, bounded callback copying, and Cortex-M0+ symbol closure. No EULA body,
resident table, direct MMIO, product policy, hardware action, or production
route is admitted.

The concrete gap falls from 50 functions / 4,722 bytes to 47 / 4,550 bytes;
application contracts fall from 38 to 35 and all twelve external/unavailable
functions remain unchanged. Hardware validation remains deferred by project
direction, and the current Touch readiness summary is regenerated at Batch 19.
