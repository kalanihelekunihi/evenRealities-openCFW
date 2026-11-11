# i2c_5 delay-callback correlation

## Decision

The scatter-loaded `i2c_5` descriptor installs the exact callback
`0x00054AF1`, whose executable body is `0x00054AF0..<0x00054AFC`. The body is
R1 product configuration: five Thumb NOP instructions followed by `bx lr`. It
ignores its argument and has no side effect.

The callback is classified `r1_product_specific` /
`clean_room_behavior_only`. The local `r1_twi_i2c5_delay_noop` preserves only
that no-effect contract. The consolidated provider subsequently lost the
distinction from the immediate-return callback; the
[delay review](../reference/twi-delay-review.md) restores five CMSIS NOPs and
the separate `i2c_5` record binding, with a 12-byte compiled-body match.
It is not authorization to enable software-I2C timing,
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

The historical static summarizer and host tests are absent from the
consolidated tree; their descriptions are not current runnable checks.
The current [delay review](../reference/twi-delay-review.md) pins the
application hash, uses REA to inspect the complete callback body, compares
the compiled 12-byte instruction sequence, executes both callback providers
for 93 inputs each, and checks the compiled descriptor relocations. Its
execution evidence does not revalidate the historical scatter-loading claim
or establish physical bus timing.
