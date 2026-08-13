# YHM2710 and shared i2c_5 resource boundary

## Decision

The YHM2710 chip driver and its software-driven state-command transport remain a
vendor-owned provider boundary. No authoritative, redistributable YHM2710 source
or register specification has been admitted. openR1 therefore implements no
YHM register read, write, initialization sequence, thermal action, readiness
repair, system-track operation, or ship-mode operation.

Five adjacent functions are independently attributable to R1 product ownership
rather than the chip driver: three manage the NFC board-enable and exclusive
`i2c_5` lifecycle, and two maintain a battery/optical/touch client mask around a
provider-owned electrical transition. These are implemented as clean-room
resource adapters.

## Exact recovered split

| R1 entry | Size | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x00050464` | 66 | `15fcba3427ed758f3e6040449531392b360c046d2b8f27f23f7c7ebc6dd06509` | register NFC GPO/`i2c_5`, configure P1.10, drive it low |
| `0x000504C0` | 20 | `2a985eaced1ffba181347e060a1aa38cd3167807051d6ca7082ee42a28bfe318` | release `i2c_5`, drive P1.10 low |
| `0x000504D8` | 52 | `672d16c18e2add902d1916583a3b6e4cc974ef445782a7046fa0bd10e4605a27` | low, delay 10, high, delay 10, acquire `i2c_5` |
| `0x00050758` | 48 | `4b22fb4a06a2d023856499add6354c49714db435df0e5244ad0d097d5ceb8582` | release one of three product clients; act only at the one-to-zero boundary |
| `0x00050778` | 32 | `dc1383f7285121c71e7525dcd20e3e4f272bc069eef3aeedabbe47a82cb03dc6` | acquire one of three product clients; act only at the zero-to-one boundary |

The P1.10 configuration word is `0x0000030F`: output, input disconnected,
pull-up, H0H1 high-drive mode, sense disabled. P1.10 is deliberately named only
as the recovered NFC board-enable seam; its downstream schematic net and
electrical load have not been proven.

The client indices are product-level roles recovered from their callers:

| Client | Role |
| ---: | --- |
| 0 | transient battery sampling |
| 1 | optical/PPG |
| 2 | touch |

The stock zero-boundary actions eventually produce YHM register-2 writes
`0xA8` and `0x28`. Those bytes are evidence, not locally implemented constants.
Their electrical meaning is unknown and they remain entirely inside the future
licensed provider.

## Vendor-owned transport

The scatter descriptor audit separates two different provider transports that had previously
been conflated in the diagnostic parser. `0x200075A4` is the `i2c_5` operation table and points to
the software-TWI functions `0x000553E5`, `0x00055255`, `0x00055519`, and `0x00055F5D`.
The actual `device_stacmd` operation table is at `0x20007614` and points to `0x0005657D`,
`0x00056569`, `0x00056591`, and `0x0005660D`.

Fifteen exact state-command functions total 1,018 executable bytes. Fourteen functions / 1,000
bytes implement P1.01 framing, edge waits, parity, retries, read/write, and lifecycle and are now
explicitly `yhmicros_yhm2710_candidate`. The remaining 18-byte initcall at
`0x000565F4..<0x00056606` is configuration-only: OpenR1 may preserve a direct typed provider
binding, but may not recreate the transport or the stock registry. Exact segments, including the
three-block `0x0005CBE4` function, and every digest are emitted by
`../../scripts/firmware/summarize_r1_pmic_transport.py`.

The exact production descriptor is software-driven I2C-style state-command
framing, not ordinary addressed I2C:

- clock P1.11 and data P1.14, with status/IRQ P1.01;
- START/STOP and MSB-first bytes with an ACK after each transmitted byte;
- read command phases `[r, 00, 00]`, repeated START, `[r | 01]`;
- write phase `[r, 00, 00, payload...]`;
- no recovered clock-stretch wait; and
- no fixed slave-address phase (odd command values remain odd).

The `i2c_5` facts are preserved by the immutable parser
`../../scripts/firmware/summarize_r1_pmic_transport.py`.
The separately recovered P1.01 state-command evidence is likewise static and is not used to create
a replacement live sender.

The marker-bearing YHM2710 initialization and system-track bodies remain
`yhmicros_yhm2710_candidate` in the ownership ledger. A source-admission review
on 2026-08-12 found no authoritative public provider source or usable license;
similarly named HM2710 material is a different part and is not admissible.

## Implemented clean-room resource layer

[`../../src/r1_power_lease.c`](../../src/r1_power_lease.c)
implements only the three-bit product ownership policy. Its provider has one
semantic operation, `set_shared_power_enabled(context, enabled)`. Duplicate
acquires, absent releases, and non-boundary transitions do not call the
provider. A failed first enable leaves the mask empty; a failed final disable
retains the last client, avoiding a software state that falsely reports the
rail as released.

No YHM identity, register, command, wire, timing, readiness, thermal, charging,
or shutdown data appears in that module. Until a lawfully obtained provider is
admitted and hardware-tested, touch cannot bind this power service and remains
fail closed.

[`../../platform/nrf52840/sdk/openr1_i2c5_resources.c`](../../platform/nrf52840/sdk/openr1_i2c5_resources.c)
uses the pinned Nordic SDK/CMSIS-FreeRTOS primitives to reproduce the R1-owned
NFC board lifecycle and serialize the shared conductors:

- Nordic GPIO configures P1.10 exactly and holds it low at startup;
- activation performs low / 10 ticks / high / 10 ticks;
- a static CMSIS mutex grants exclusive `i2c_5` ownership;
- deactivation first releases the ST provider/bus, then the mutex, then drives
  P1.10 low; and
- the interface exposes ownership only, never a generic transfer primitive.

The resource layer is bound to the ST25DVxxKC adapter during Nordic startup.
NFC still starts disabled and has no BLE/raw-register/mailbox-write control
surface. Any future YHM provider must use the same mutex before reconfiguring or
driving P1.11/P1.14.

## Verification

Strict host tests cover all client permutations, duplicate calls, absent
releases, invalid clients, unbound providers, and provider failures. Sanitizer
tests and freestanding Cortex-M4 compilation pass. The Nordic SDK image compiles
the resource objects and retains the static CMSIS mutex, exact GPIO setup, NFC
binding, and ownership functions.

This is static and host verification. P1.10 electrical behavior, physical
`i2c_5` coexistence, YHM state transitions, touch power, dock behavior, and
recovery after interrupted transitions still require owned-hardware validation.

The verified unsigned SDK application is 90,956 bytes text, 236 bytes data,
and 132,456 bytes BSS. Its standalone HEX and BIN SHA-256 values are
`0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81`
and `31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.
