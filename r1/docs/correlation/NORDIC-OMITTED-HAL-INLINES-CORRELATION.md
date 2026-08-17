# Nordic omitted HAL inline correlation

Three explicit `R1PowerEvidence.java` entries that Ghidra placed only inside
noncontiguous bounding ranges are independent compiler-emitted Nordic nRF5 SDK
17.1.0 HAL inlines. They are source-routed rather than reimplemented locally.

| Executable extent | Bytes | SDK symbol and source | SHA-256 |
| --- | ---: | --- | --- |
| `0x0007902C..<0x0007903E` | 18 | `modules/nrfx/hal/nrf_gpio.h::nrf_gpio_cfg_default` | `0225ea03c5a9447c82d7a50a869c409e1415b8b56d6aca2da81ec9037d99e1a4` |
| `0x000791E4..<0x000791F8` | 20 | `modules/nrfx/hal/nrf_gpio.h::nrf_gpio_pin_clear` | `5d9088f1d1399da831f929bd6c63b824486fbbefaca6605772b6bb1f9d428b3e` |
| `0x00079E10..<0x00079E20` | 16 | `modules/nrfx/hal/nrf_saadc.h::nrf_saadc_channel_input_set` | `89cc89d1dc3ea948787e9ab258dded01450b8bdf17c6408f6983c0ba4493015a` |

The first GPIO body passes input, disconnected, no-pull, S0S1, and no-sense
constants to the already source-routed `nrf_gpio_cfg` instance at `0x00078F4A`.
Its Thumb pointer occurs once in the decompressed startup image at
`0x200075F0`. The second calls the already source-routed pin/port decoder at
`0x00079314`, writes `1 << pin` to `OUTCLR` offset `0x50C`, and has one startup
Thumb pointer at `0x200075D4`.

The SAADC body uses channel stride 16 and stores the negative and positive
selectors at offsets `0x514` and `0x510`. Its five direct callers are
`0x0007AF28`, `0x0007AF62`, `0x0007B0C8`, `0x0007B0DC`, and `0x0007B126`.
The nRF52840 SAADC base literal `0x40007000` is stored at `0x00079E20`; that
literal is data immediately after the return and is deliberately excluded from
the 16-byte executable extent.

All three entries are exact manual provenance supplements because the exported
Ghidra function CSV omitted their independent bodies. Production firmware
compiles the pinned Nordic headers. No GPIO or SAADC implementation is copied
into the clean-room product layer.

Reproduce the byte, callsite, literal, and decompressed-pointer checks with:

```sh
python3 tools/evidence/summarize_r1_nordic_omitted_hal_inlines.py
```
