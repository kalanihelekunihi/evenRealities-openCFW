# YHM2710 and shared i2c_5 resource boundary

## Decision

The unavailable YHM2710 vendor package remains unlicensed, but the repository owner authorized
full independent reduction on 2026-08-14. All 44 provider-classified functions are now
reconstructed as transparent C in `reconstructed/yhm2710/`; exact mapping, recovered behavior,
and hardening differences are documented in
[`../correlation/YHM2710-REDUCTION-CORRELATION.md`](../correlation/YHM2710-REDUCTION-CORRELATION.md).
No vendor source, binary library, firmware blob, or opaque object is a build input.

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
`0xA8` and `0x28`. Both bytes are implemented in the owner-authorized transparent
YHM reconstruction and selected only through the typed three-client lease. Their
electrical meaning remains unknown and is not surfaced as a raw register API.

## Reconstructed transport

The scatter descriptor audit separates two different provider transports that had previously
been conflated in the diagnostic parser. `0x200075A4` is the `i2c_5` operation table and points to
the software-TWI functions `0x000553E5`, `0x00055255`, `0x00055519`, and `0x00055F5D`.
The actual `device_stacmd` operation table is at `0x20007614` and points to `0x0005657D`,
`0x00056569`, `0x00056591`, and `0x0005660D`.

Fifteen exact state-command functions total 1,018 executable bytes. Fourteen functions / 1,000
bytes implement P1.01 framing, edge waits, parity, retries, read/write, and lifecycle and are now
owner-authorized clean-room reconstructions. The remaining 18-byte initcall at
`0x000565F4..<0x00056606` is configuration-only: OpenR1 may preserve a direct typed provider
binding without recreating the stock registry. Exact segments, including the
three-block `0x0005CBE4` function, and every digest are emitted by
`../../tools/evidence/summarize_r1_pmic_transport.py`.

The exact production descriptor is software-driven I2C-style state-command
framing, not ordinary addressed I2C:

- clock P1.11 and data P1.14, with status/IRQ P1.01;
- START/STOP and MSB-first bytes with an ACK after each transmitted byte;
- read command phases `[r, 00, 00]`, repeated START, `[r | 01]`;
- write phase `[r, 00, 00, payload...]`;
- no recovered clock-stretch wait; and
- no fixed slave-address phase (odd command values remain odd).

The `i2c_5` facts are preserved by the immutable parser
`../../tools/evidence/summarize_r1_pmic_transport.py`.
The P1.01 evidence now drives the independently compiled sender; it is never copied in as an
opaque artifact.

The marker-bearing initialization, status, ladder, and system-track bodies are included in the
44-entry reduction. A source-admission review found no authoritative public provider source or
usable license; similarly named HM2710 material is a different part and is not used.

## Implemented clean-room resource layer

`../src/r1_power_lease.c`
implements only the three-bit product ownership policy. Its provider has one
semantic operation, `set_shared_power_enabled(context, enabled)`. Duplicate
acquires, absent releases, and non-boundary transitions do not call the
provider. A failed first enable leaves the mask empty; a failed final disable
retains the last client, avoiding a software state that falsely reports the
rail as released.

The resource module still contains no YHM wire logic. The Zephyr adapter now binds it to the
reconstructed typed YHM device service: P1.01 uses the exact pull-up GPIO callbacks, 13/52/209 us
wire delays, separate 64-MHz post-configuration cycle delay, chip-ID probe, and five-register
initialization. Battery client 0 and touch client 2 are bound. The Zephyr optical board lifecycle
now acquires client 1 before asserting the emitter and releases it after disabling the interrupt,
reset, emitter, and software bus. Sampling is not started at boot and has no wire-facing command
route. Touch remains identity/wear gated, and all electrical behavior remains hardware-validation
work.

`../platform/nrf52840/sdk/openr1_i2c5_resources.c`
uses the pinned Nordic SDK/CMSIS-FreeRTOS primitives to reproduce the R1-owned
NFC board lifecycle and serialize the shared conductors:

- Nordic GPIO configures P1.10 exactly and holds it low at startup;
- activation performs low / 10 ticks / high / 10 ticks;
- a static CMSIS mutex grants exclusive `i2c_5` ownership;
- deactivation first releases the ST provider/bus, then the mutex, then drives
  P1.10 low; and
- the interface exposes ownership only, never a generic transfer primitive.

The resource layer is bound to the ST25DVxxKC adapter during Nordic startup. The Zephyr adapter
provides the same exact P1.10 sequence and a typed dock-session mutex in addition to its TWIM1
motion/NFC arbiter.
NFC still starts disabled and has no BLE/raw-register/mailbox-write control
surface. Any future YHM provider must use the same mutex before reconfiguring or
driving P1.11/P1.14.

## Verification

Strict host tests cover all client permutations, duplicate calls, absent
releases, invalid clients, unbound providers, and provider failures. Sanitizer
tests and freestanding Cortex-M4 compilation pass. The Nordic SDK image compiles
the resource objects and retains the static CMSIS mutex, exact GPIO setup, NFC
binding, and ownership functions.

This is static, host, and clean Zephyr build verification. P1.10 electrical behavior, physical
`i2c_5` coexistence, YHM state transitions, touch power, dock behavior, and
recovery after interrupted transitions still require owned-hardware validation.

The verified unsigned SDK application is 94,804 bytes text, 236 bytes data,
and 132,544 bytes BSS. Its standalone HEX and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`
and `421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

## Attribution re-examination 2026-08

Exhaustive GitHub/Gitee/web searches found zero public YHM2710 driver code and no downloadable
datasheet; the single-wire stacmd protocol and chip-ID `0xA0` appear in no public document.
All 44 entries retain the attribution label and have no provider pointer, but are source-admitted
as owner-authorized transparent reconstructions. Full attribution evidence:
[`withheld-providers-ATTRIBUTION-2026-08.md`](withheld-providers-ATTRIBUTION-2026-08.md).
