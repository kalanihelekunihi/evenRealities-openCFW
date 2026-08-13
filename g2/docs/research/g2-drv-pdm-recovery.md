# G2 generic PDM driver recovery

Status: complete bounded object/provider closure over authenticated G2 2.2.6.10.
This is analysis only; the object remains excluded from production routing.

## Result

`driver\pdm\drv_pdm.c` occupies `[0x0057B704,0x0057BA88)`: seven functions,
794 reachable body bytes, 900 physical bytes, and 288 instructions. The source
path has no baseline Ghidra function anchors, but four raw literal references
recover it. The exact end is fixed by the following `service_codec_host.c`
function at `0x0057BA88`.

The first three functions are CMSIS-Core `__NVIC_EnableIRQ`,
`__NVIC_DisableIRQ`, and `__NVIC_SetPriority` definitions. The remaining four
implement idempotent PDM0 initialization/deinitialization, the PDM0 IRQ handler,
and inactive-DMA-buffer extraction. The extractor converts 160 packed 32-bit
PDM words into 160 signed 16-bit samples (320 bytes); this smaller frame is
passed into the already closed audio algorithm path.

## Upstream shortcut

Nineteen direct calls cover 14 public APIs in Apollo510 `am_hal_pdm.c`. Twelve
are the same APIs independently recovered from `drv_pdm_production.c`; this
object adds `am_hal_pdm_interrupt_service` and
`am_hal_pdm_interrupt_status_get`. Every API exists in official public replay
commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`, whose PDM source is Git blob
`23a440bfd6121509b0586f0afe1990fcf59dd8fb` (SHA-256
`a4d6a2acdcb8414afcfb940d1c97e5aff6530aa972d72640be48ac216c7e2d8c`).
Together, the two PDM wrappers exercise 14 distinct APIs and reinforce the
same AmbiqSuite 5.1.0 lineage already selected by the RTOS and I2S seams.

The stock build predates Ambiq's public import. Consequently this identifies
the proper public replay and exact source blob, but cannot claim the unavailable
private pre-release producing commit.

## Ingress and residual boundary

The startup vector cell at `0x00438100` stores Thumb entry `0x0057B941`, proving
`0x0057B940` is the PDM0 IRQ handler. Three external calls and four internal
calls target object entries. One raw `BL`-shaped word at `0x0067B116` targets
interior address `0x0057B70E`; it lies in non-code data and is pinned as a
pseudo-instruction, not executable ingress. There are no indirect calls or
real strict-interior entries.

All remaining external calls terminate at admitted EasyLogger, bounded IAR
fill, or already closed first-party board/cache/audio providers. No additional
third-party implementation or version discriminator remains in this object.

## Reproduction

```sh
python3 tools/analyze_g2_drv_pdm.py
python3 -m unittest -v tests.test_analyze_g2_drv_pdm
make drv-pdm-closure
```
