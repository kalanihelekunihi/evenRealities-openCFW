# G2 production PDM driver recovery

Status date: 2026-08-12  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Result: complete linked object and AmbiqSuite PDM source seam closed;
production source not routed

## Result

The zero-baseline-anchor retained path
`driver\pdm\drv_pdm_production.c` owns six functions in
`[0x0057B444,0x0057B704)`: 610 executable bytes plus 94 bytes of literal data,
704 physical bytes total. Four raw references to the path cell recover the
otherwise absent path ownership. Whole-image ingress contains six direct entry
sites, no stored entry pointer, no strict interior ingress, and no indirect
call.

The first three definitions are the exact CMSIS-Core `__NVIC_EnableIRQ`,
`__NVIC_DisableIRQ`, and `__NVIC_SetPriority` inline helpers. The next two are
the retained exact symbols `DRV_PdmProductionInit` and
`DRV_PdmProductionDeinit`. The final pathless helper obtains the inactive PDM
DMA buffer, performs the first-party cache operation, and extracts bytes 1 and
2 from each 32-bit PDM word into 1,600 signed 16-bit samples / 3,200 bytes.

## AmbiqSuite source shortcut

Thirteen calls terminate at twelve public APIs in
`mcu/apollo510/hal/am_hal_pdm.c`:

- initialize, deinitialize, and power control;
- configure, enable, and disable;
- DMA start and inactive-buffer selection;
- FIFO threshold setup; and
- interrupt enable, disable, and clear.

All signatures are already present in the authenticated Apollo510 header
snapshot. The public C source at selected AmbiqSuite 5.1.0 replay commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b` has Git blob
`23a440bfd6121509b0586f0afe1990fcf59dd8fb` and SHA-256
`a4d6a2acdcb8414afcfb940d1c97e5aff6530aa972d72640be48ac216c7e2d8c`.
The stock register graphs and signatures map every call to that source. As with
the existing Apollo510 sleep and I2S results, the firmware predates the public
import: this proves the SDK 5.1.0 source lineage and reusable public baseline,
not the unavailable private pre-release generating commit.

The remaining 25 calls are 20 EasyLogger diagnostics, one bounded IAR fill,
and four first-party pin/IRQ/cache seams. No additional vendor library or
opaque utility function appears.

## Reproduction and gate

The function, provider, exact upstream-API, and closure maps are the four
`tools/manifests/g2-drv-pdm-production-*.tsv` records.
`tools/analyze_g2_drv_pdm_production.py` authenticates the object, raw path
references, ingress, providers, selected commit, official source identity, and
vendored PDM header API set. Run `make drv-pdm-production-closure` for its
focused regression contract.

Production routing remains gated on the complete Apollo510 PDM translation-unit
dependency admission, G2 pin/IRQ/cache adapter implementation, DMA buffer
placement/coherency, microphone clocking, and device capture tests. The linked
third-party HAL behavior and public source identity are no longer opaque.
