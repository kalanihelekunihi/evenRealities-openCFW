# Nordic nRF52 SystemInit correlation

## Result

Two exact functions / 544 executable bytes in the recovered application are
Nordic nRF5 SDK startup provider code:

| Entry / half-open extent | Bytes | SHA-256 | Nordic symbol |
|---|---:|---|---|
| `0x00033364..<0x00033576` | 530 | `a09c9eaeba82d61e0cc0d0d26778aaf27f13aa0b9aad13e66a5b71a86b7becca` | `SystemInit` |
| `0x0007CA7C..<0x0007CA8A` | 14 | `f22f49539484bb5d46cfd079ac9a0b82d693b64b552315b8ab771d57144b3fa1` | `nvmc_config` |

`Reset_Handler` at `0x00027488` loads the Thumb target `0x00033365` and calls
`SystemInit` at `0x0002748A`. `SystemInit` is the only caller of `nvmc_config`,
at seven verifier-pinned callsites. The helper writes `NRF_NVMC->CONFIG` and
waits on `NRF_NVMC->READY`; Nordic's separate `nvmc_wait` source operation was
inlined into this recovered 14-byte body.

The static census is reproducible with:

```sh
python3 tools/summarize_r1_nordic_system_init.py
```

## Source route

Both functions route to the pinned Nordic SDK 17.1.0 source
`modules/nrfx/mdk/system_nrf52.c`, included by
`modules/nrfx/mdk/system_nrf52840.c`. The pinned generic source has SHA-256
`e8ac695000222af65e2e43dd9740e78715c1e7f70645b78aa14b5e9155be8717`;
the nRF52840 wrapper has SHA-256
`2fcb22d591bdba0e5b736c747a2d991019e814a1ea7c0f55cf816825ed032800`.

The recovered function's complete semantic fingerprint includes:

- nRF52840 FICR variant/revision-gated errata handling;
- CLOCK reset, TEMP calibration transfer, CCM `MAXPACKETSIZE = 0xFB`, RAM,
  QSPI, and `RESETREAS` workarounds;
- FPU CPACR enable followed by DSB/ISB;
- APPROTECT compatibility handling;
- NFCT UICR conversion and GPIO pin-reset UICR programming through NVMC;
- CMSIS system reset and `SystemCoreClockUpdate` to 64 MHz.

These are provider-specific source and hardware operations, not locally
authored R1 behavior. No Nordic startup body is recreated locally.

## Recovered build configuration

The NFCT and pin-reset branches prove the stock application was built with:

- `NRF52840_XXAA` and hard-float Cortex-M4 settings;
- `CONFIG_NFCT_PINS_AS_GPIOS`;
- `CONFIG_GPIO_AS_PINRESET`, selecting nRF52840 reset pin 18.

openR1 compiles Nordic's own `system_nrf52840.c` and now supplies both recovered
configuration switches in its SDK Makefile. This is configuration-only local
work: Nordic remains the exclusive implementation source. With the pinned GCC
settings, the linked equivalent inlines Nordic's `nvmc_config` stores into
`SystemInit` and retains Nordic's `nvmc_wait` as a separate symbol; that
compiler layout difference does not create a local implementation.

## Admission decision

- provider family: `nordic_nrf5_sdk_17_1_0`;
- disposition: `use_nordic_sdk`;
- local startup implementation: prohibited;
- local scope: compile flags, link integration, and verification only.
