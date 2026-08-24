# G2 GX8002B host-driver recovery

`driver\codec\drv_gx8002b.c` is now closed as a complete 12-function,
1,028-body-byte object plus a 144-byte literal/pointer pool, for 1,172
physical bytes at `[0x0057A46C,0x0057A900)`. The authenticated image contains
three baseline path anchors / 424 bytes. Raw recursive recovery adds nine
adjacent bodies, including three CMSIS-Core NVIC helpers, the I2S ISR, the
power-state accessor, both I2S lifecycle bodies, a DMA-buffer/cache helper,
and a stored audio-thread callback.

The audit pins every function hash, all 399 decoded instructions, 79 direct
body calls, 18 direct BL ingress sites, two stored Thumb pointers, nine raw
path-pointer references, both neighboring boundaries, and the complete pool.
There are no indirect calls, strict-interior BL targets, uncovered body bytes,
or unrecovered direct object targets.

## The software provider is Ambiq I2S, not a GX8002 SDK

The driver name initially makes NationalChip's device SDK the obvious source
candidate. The binary tells a narrower story. Every external HAL call made by
`DRV_Gx8002_I2SInit`, `DRV_Gx8002_I2SDeinit`, and the stored ISR maps to the
Apollo510 I2S API:

| Stock address | Selected public function |
|---:|---|
| `0x0059005E` | `am_hal_i2s_initialize` |
| `0x005900CE` | `am_hal_i2s_deinitialize` |
| `0x00590104` | `am_hal_i2s_configure` |
| `0x005904CE` | `am_hal_i2s_dma_transfer_start` |
| `0x00590648` | `am_hal_i2s_power_control` (two calls) |
| `0x00590818` | `am_hal_i2s_interrupt_clear` |
| `0x00590848` | `am_hal_i2s_interrupt_status_get` |
| `0x005908A0` | `am_hal_i2s_interrupt_service` |
| `0x00590A24` | `am_hal_i2s_dma_configure` |
| `0x00590B6C` | `am_hal_i2s_dma_get_buffer` |
| `0x00590B92` | `am_hal_i2s_enable` |
| `0x00590C62` | `am_hal_i2s_disable` |

The selected source oracle is Ambiq's complete
[`mcu/apollo510/hal/am_hal_i2s.c`](https://github.com/AmbiqMicro/ambiqhal_ambiq/blob/5efc0228528a8adce5eae0d226fac85d2551eb3b/mcu/apollo510/hal/am_hal_i2s.c)
at public commit
[`5efc0228528a8adce5eae0d226fac85d2551eb3b`](https://github.com/AmbiqMicro/ambiqhal_ambiq/commit/5efc0228528a8adce5eae0d226fac85d2551eb3b).
The file identifies AmbiqSuite 5.1.0 revision
`release_sdk5p1p0-366b80e084`; its exact SHA-256 is
`16888e7bc9e2daf3ed936463c4e0ecfec73ea3c74c3c49b1fe60618b8aa86dc4`
and Git blob is `cc422934767912c218b619084e7fbe92ce7eaf6b`.

The stock functions preserve the public file's handle initialization and
validation, I2S register programming, retained-state power transitions,
two-stage DMA state, interrupt clear/status/service sequence, enable/disable
logic, and inactive-buffer selection. This is an authenticated
source-equivalent replay. It is not a claim that the later public import is
the historical generating commit: the G2 image predates that import, and the
exact private Ambiq checkout remains unavailable.

NationalChip's official documentation identifies GX8002B as its low-power
voice processor and calls the device software package LVP (Lower-Power Voice
Process). Public access is routed through NationalChip's registered GitLab or
sales flow; the public hardware document is
[`GX8002_datasheet_V1.15`](https://document.nationalchip.com/hardware/%E8%8A%AF%E7%89%87%E6%95%B0%E6%8D%AE%E6%89%8B%E5%86%8C/datasheet/GX8002_datasheet_V1.15.pdf).
No LVP code, command parser, firmware blob, or NationalChip software call is
linked into this object. The GX8002B is an external hardware/protocol
dependency; this object is G2 host-side power, I2S, DMA, and callback policy.

## Embedded and callable dependencies

The first three linked bodies are the exact stable semantics of
`__NVIC_EnableIRQ`, `__NVIC_DisableIRQ`, and `__NVIC_SetPriority` from
CMSIS-Core `core_cm55.h`. Their ISER, ICER, IPR, and SHPR addresses are present
in the object's pool, and the disable helper retains `DSB`/`ISB`. The local
authenticated CMSIS-Core selection is commit
`d23a6949a0331ca96853bcd98b0fdcc4db47184c`; these inline bodies do not narrow
that version.

The remaining call boundary is exhaustive:

- 13 calls reach the 12 AmbiqSuite I2S functions above;
- four calls reach exact CMSIS-FreeRTOS v10.5.1 `osDelay` at selected commit
  `d213f261b5be6bb29a7cce8b84071706b72f4d53`;
- 45 calls reach admitted EasyLogger diagnostics; and
- 12 calls reach first-party GPIO arbitration, clock/pin setup, IRQ plumbing,
  the already source-owned data-cache invalidator, and audio-thread notification.

No opaque third-party software body remains in this object.

## Production source routing

`components/apollo_main/core_overlay/drv_gx8002b.c` is the clean-room
production implementation of all twelve routines. Selector-isolated Apple
Clang builds emit 608 bytes of Thumb text plus eight alignment bytes. Thirty-
four strict relocations bind the Ambiq I2S HAL, CMSIS delay, source-owned cache
invalidation, board GPIO/pin/IRQ seams, audio callbacks, and five sibling
source calls. Twelve guarded `B.W` replacements cover every callable stock
body byte (1,028 bytes); the 144-byte unreachable diagnostic/literal pool is
retained and classified as official data.

Host tests exercise signed IRQ handling, DSB/ISB ordering, external and system
priority slots, ISR status/clear/service ordering and RX gate, exact GPIO and
5/20 ms power sequencing, idempotent I2S lifecycle order, the inactive RX
buffer plus fixed 3,200-byte cache descriptor, audio notification, and the
100/1,500 ms reboot policy. All twelve selectors also compile strictly for
Cortex-M55. The canonical overlay/component/package identities are 240,692 /
3,764,088 / 4,542,582 bytes; the 2,588,615-byte flash plan contains 3,715
placed, two unresolved, five container-only, and six protected regions.

Software production routing is complete for this object. Live GX8002B rail,
I2S, DMA, interrupt, and reboot behavior remains explicitly hardware-blocked:
there is no authorized responsive G2 pair or live codec evidence available.
This is not a wider firmware-completeness claim.

## Reproduction

```sh
python3 tools/analyze_g2_drv_gx8002b.py
python3 -m unittest -v tests.test_analyze_g2_drv_gx8002b tests.test_drv_gx8002b_candidate
make drv-gx8002b-closure
```
