# Touch SCB FIFO upstream contract check

This check follows the official Infineon `mtb-pdl-cat2` pin recorded in `third-party/README.md`: commit `35f1714623cfea682d5e285af80d50416b4c7bbc`, release label `release-v2.21.0`, Apache-2.0. The official pinned raw source/header and SVD URLs are linked below. The local submodule directory is empty, so evidence was read from the official pinned URLs; no local checkout was changed.

The source supports the prior touch symbol attribution at behavioral/source level:

- `Cy_SCB_ReadArrayNoCheck` source, `drivers/source/cy_scb_common.c:51–74`, branches on `Cy_SCB_IsRxDataWidthByte`, iterates `size` data elements, reads each through `Cy_SCB_ReadRxFifo`, and stores as `uint8_t` or `uint16_t`. Its comments state that it does not check whether the FIFO contains enough elements; its precondition is that enough elements exist.
- `Cy_SCB_ReadArray`, `cy_scb_common.c:99–113`, reads `Cy_SCB_GetNumInRxFifo`, clamps the requested element count to that snapshot, calls `Cy_SCB_ReadArrayNoCheck` once (including when the clamped count is zero), then returns the clamped element count.
- The pinned common header defines `Cy_SCB_IsRxDataWidthByte` as `_FLD2VAL(SCB_RX_CTRL_DATA_WIDTH, SCB_RX_CTRL(base)) < CY_SCB_BYTE_WIDTH` (`drivers/include/cy_scb_common.h:1831–1846`); the PDL describes byte width as 8 bits. `Cy_SCB_GetNumInRxFifo` returns `_FLD2VAL(SCB_RX_FIFO_STATUS_USED, SCB_RX_FIFO_STATUS(base))` (`:831–846`). `Cy_SCB_ReadRxFifo` returns `SCB_RX_FIFO_RD(base)` directly with no availability check (`:791–808`). `drivers/include/cy_device.h:561–565` maps those field accessors through `CySCB_Type` members.
- The pinned PSoC 4000T SVD (`devices/svd/psoc4000t.svd`) identifies `RX_CTRL` at `0x300`, `DATA_WIDTH` bits `[4:0]`; `RX_FIFO_STATUS` at `0x308`, `USED` bits `[8:0]`; and `RX_FIFO_RD` at `0x340`. The 9-bit USED field corresponds to mask `0x1ff`. SVD says an RX FIFO read pops one data frame; an empty read sets RX underflow. Device header `cy8c4046fni_t412.h` identifies the CY8C4046FNI-T412 device and SCB0/SCB1 bases `0x40240000` / `0x40250000`.

One expected detail needs precise wording: the pinned PDL does not use a literal `0x18` mask for `Cy_SCB_IsRxDataWidthByte`. It extracts the `DATA_WIDTH` field and compares it against `CY_SCB_BYTE_WIDTH` (8). The SVD field is `[4:0]`, whose full field mask is `0x1f`. If “CTRL mask 18” means hex `0x18` as a mask, these official sources do not support that claim; it may refer to a binary instruction literal or another intermediate representation.

The size/count unit is **FIFO data elements**, not bytes. `ReadArrayNoCheck` stores each element as 1 byte in byte-width mode and as 2 bytes otherwise. The code takes a single count snapshot in `ReadArray`; it does not lock the FIFO or disable interrupts around the count and transfer. A concurrent FIFO consumer can invalidate that snapshot before the reads and cause underflow; this source does not supply serialization against ISR/DMA/other consumers.

## Existing firmware evidence and limits

The work adds no firmware coverage. `g2/symbols/touch.tsv` already records:

- `Cy_SCB_ReadArrayNoCheck` at `[0x9218,0x9250)`, 56 bytes, SHA-256 `07627776d2bc275029e974a40d0944d6b87502cfea118880b8d60d6c3fa97cc7`.
- `Cy_SCB_ReadArray` at `[0x9250,0x926E)`, 30 bytes, SHA-256 `c7729e5dfb38b7391112b5eeeb9e0a8b0fc0d2ad0bc2e1e9b53b353b401e5e49`.

The saved prior oracle `g2/analysis/shortcut-batch-2026-10-05/touch-upstream/results.json` binds those bytes to firmware SHA-256 `0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`. Its execution stubs the callee at entry. This source review corroborates API behavior and register semantics; it is not a compiler-level byte match, does not execute the original 56-byte callee, and does not verify physical hardware timing or concurrent access behavior.

## Official references

- [Pinned `cy_scb_common.c`](https://raw.githubusercontent.com/Infineon/mtb-pdl-cat2/35f1714623cfea682d5e285af80d50416b4c7bbc/drivers/source/cy_scb_common.c)
- [Pinned `cy_scb_common.h`](https://raw.githubusercontent.com/Infineon/mtb-pdl-cat2/35f1714623cfea682d5e285af80d50416b4c7bbc/drivers/include/cy_scb_common.h)
- [Pinned `cy_device.h`](https://raw.githubusercontent.com/Infineon/mtb-pdl-cat2/35f1714623cfea682d5e285af80d50416b4c7bbc/drivers/include/cy_device.h)
- [Pinned PSoC 4000T SVD](https://raw.githubusercontent.com/Infineon/mtb-pdl-cat2/35f1714623cfea682d5e285af80d50416b4c7bbc/devices/svd/psoc4000t.svd)
- [Pinned CY8C4046FNI-T412 device header](https://raw.githubusercontent.com/Infineon/mtb-pdl-cat2/35f1714623cfea682d5e285af80d50416b4c7bbc/devices/include/cy8c4046fni_t412.h)
- [Infineon PDL GitHub repository](https://github.com/Infineon/mtb-pdl-cat2)
