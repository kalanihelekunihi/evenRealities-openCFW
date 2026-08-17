# i2c_5 delay-callback correlation

## Decision

The scatter-loaded `i2c_5` descriptor installs the exact callback
`0x00054AF1`, whose executable body is `0x00054AF0..<0x00054AFC`. The body is
R1 product configuration: five Thumb NOP instructions followed by `bx lr`. It
ignores its argument and has no side effect.

The callback is classified `r1_product_specific` /
`clean_room_behavior_only`. The local `r1_twi_i2c5_delay_noop` preserves only
that no-effect contract. It is not authorization to enable software-I2C timing,
GPIO drive, NFC, PMIC, or YHM2710 traffic.

## Exact identity and descriptor binding

| Range | Bytes | SHA-256 |
| --- | ---: | --- |
| `0x00054AF0..<0x00054AFC` | 12 | `33ff9323be43957254a5dbd6680b5e2103e8484374493bdfcf56d6e35c48256a` |

The complete body has no direct branch callers. Decompressing the pinned
startup scatter image places the `i2c_5` descriptor at `0x20007550`; its delay
callback word at offset `0x28` is exactly the Thumb pointer `0x00054AF1`.

This matches the existing six-bus registry evidence. `i2c_5` remains a shared
software-driven descriptor associated with the ST25DVxxKC NFC tag and adjacent
YHM2710 state-command wrapper. Those transports keep their independent source
and safety gates.

## Verification

```sh
python3 tools/evidence/summarize_r1_i2c5_delay_callback.py
```

The static check pins the application hash, complete callback body, lack of
direct callers, decompressed descriptor address, field offset, and Thumb
pointer. Host tests call the transparent no-op with zero and `UINT32_MAX` and
observe no state or provider effect.
