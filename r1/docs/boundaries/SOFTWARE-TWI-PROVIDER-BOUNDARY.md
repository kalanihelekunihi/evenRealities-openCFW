# Software-TWI provider boundary

## Result

Forty recovered functions occupy 3,524 executable bytes in the rebuilt application image. They
form four compiler-instantiated GPIO-driven two-wire engines, one each for `i2c_2` through
`i2c_5`. Every extent and SHA-256 digest is checked by
`tools/evidence/summarize_r1_software_twi_engines.py` and the complete OpenR1 verifier.

The behavior is high-confidence evidence, but source ownership is unresolved. The ownership
ledger therefore assigns every body to `unknown_software_twi_provider_candidate` with
`investigate_before_implementing`. This boundary is implementation-blocked: OpenR1 does not
translate or recreate the recovered engine bodies until an exact attributable source, version,
and usable license are established.

The analyzer is a static parser only. It exposes no live GPIO or I2C sender, performs no device
access, and contains no signing or deployment path.

## Exact function families

Each bus has the same ten semantic roles. End addresses are exclusive.

| Role | `i2c_2` | `i2c_3` | `i2c_4` | `i2c_5` |
|---|---:|---:|---:|---:|
| open | `0x00055330..<0x0005535C` | `0x00055360..<0x0005538C` | `0x00055390..<0x000553DE` | `0x000553E4..<0x00055410` |
| read adapter | `0x0005547C..<0x000554AA` | `0x000554B0..<0x000554DE` | `0x000554E4..<0x00055512` | `0x00055518..<0x00055542` |
| read byte | `0x00055548..<0x000555F4` | `0x000555F4..<0x000556A0` | `0x000556A0..<0x0005574C` | `0x0005574C..<0x000557F8` |
| read transaction | `0x000557F8..<0x00055878` | `0x00055878..<0x000558F8` | `0x000558F8..<0x00055988` | `0x00055988..<0x00055A18` |
| start | `0x00055A18..<0x00055A56` | `0x00055A56..<0x00055A94` | `0x00055A94..<0x00055AD2` | `0x00055AD2..<0x00055B10` |
| stop | `0x00055B10..<0x00055B3C` | `0x00055B3C..<0x00055B68` | `0x00055B68..<0x00055B94` | `0x00055B94..<0x00055BC0` |
| ACK | `0x00055BC0..<0x00055C08` | `0x00055C08..<0x00055C50` | `0x00055C50..<0x00055C98` | `0x00055C98..<0x00055CE0` |
| write adapter | `0x00055DBC..<0x00055E3C` | `0x00055E40..<0x00055EC0` | `0x00055EC4..<0x00055F58` | `0x00055F5C..<0x00055F9E` |
| write byte | `0x00055FA4..<0x00055FF2` | `0x00055FF2..<0x00056040` | `0x00056040..<0x0005608E` | `0x0005608E..<0x000560DC` |
| write transaction | `0x000560DC..<0x0005613E` | `0x0005613E..<0x000561A0` | `0x000561A0..<0x00056202` | `0x00056202..<0x00056274` |

The `open` family spans `0x00055330..<0x00055410`; all remaining recovered operation families
span `0x0005547C..<0x00056274`, with non-function gaps preserved. The four `read byte`, `start`,
`stop`, `ACK`, and `write byte` bodies are byte-identical within their respective role. This is
strong evidence of compiler-instantiated generic code, but byte identity does not establish who
authored the source.

## Recovered instances and board bindings

| Bus | State | SDA / SCL | Delay argument | Recovered use |
|---|---:|---|---:|---|
| `i2c_2` | `0x20007400` | P0.28 / P1.13 | 1 | GXT310 optical channels |
| `i2c_3` | `0x20007470` | P0.12 / P0.11 | 5 | present but dormant in the recovered product path |
| `i2c_4` | `0x200074E0` | P0.31 / P1.09 | 1 | Goodix optical provider boundary |
| `i2c_5` | `0x20007550` | P1.11 / P1.14 | 1 | ST25DVxxKC/YHM2710 shared resource |

The recovered `i2c_5` delay callback accepts the delay argument but has no observable delay
effect. That is evidence about the stock image, not behavior OpenR1 should blindly preserve: an
attributable provider and owned-hardware timing validation must determine the safe implementation.

The four close/shutdown wrappers at `0x000551E8`, `0x0005520C`, `0x00055230`, and
`0x00055254` are outside this boundary. They are separately admitted R1 adapters that release the
two pins through Nordic `nrf_gpio_cfg_default`. Similarly, the four fixed bus-binding wrappers at
`0x00056508...0x00056550` retain R1 board configuration without admitting either this engine or
the unidentified global device registry.

## Sharpened fingerprint evidence

The provenance investigation added the following structural detail. None of it changes the
admission state; the family remains `investigate_before_implementing`.

- Callback-vtable engine: each bus owns a per-bus state struct (delay context, SCL/SDA handles,
  and six GPIO/delay operations — drive-low, release-high, set-output, set-input(pin, pull),
  udelay(ctx), read-pin). The operation bodies are byte-identical across the four
  compiler-instantiated buses `i2c_2`..`i2c_5`, with per-bus state structs at
  `0x20007400 + n*0x70`.
- Registry-adapter error enums interlock with the generic device registry: the read adapter at
  `0x0005547C` returns `4/10/12` and the write adapter at `0x00055DBC` returns `4/8/11`, gap-free
  alongside the registry's missing-operation codes `{1,2,3,5,6,7,9}`. Together they form one
  coherent positive-integer status enum `0..12` spanning both families — strong evidence that the
  software-TWI engine and the generic device registry are one framework by one author.
- Transaction semantics: the read transaction at `0x000557F8` performs
  start / address / register / repeated-start / address|1 / N bytes / stop; the write transaction
  at `0x000560DC` sends address + 16-bit register MSB-first + one data byte.
- The divergent `i2c_4` open at `0x00055390` calls a Nordic-attributed six-argument
  `nrf_gpio_cfg` wrapper — vendor-HAL special-casing inside one bus open, not evidence of Nordic
  authorship of the engine.
- No pointers to any family entry exist in flash; the operations tables are installed at runtime
  into the `0x200074xx` records.

## Candidates rejected

- Nordic `twi_sw_master`: single compile-time bus, direct `nrf_gpio` calls, boolean returns.
- RT-Thread `i2c-bit-ops`: different operations decomposition and negative `rt_err_t` returns.
- Linux/Zephyr GPIO-I2C bit-bang: wrong ecosystem.
- Sensor-vendor SDKs: the same engine also drives the ST25DV NFC tag and the YHM2710 PMIC on
  `i2c_5`, outside any single sensor vendor's scope.

## Next evidence step

Trace the runtime vtable installer that writes `0x2000740C..0x20007424`. If the callbacks resolve
to already admitted R1 Nordic-GPIO adapters, that further confirms vendor-framework authorship;
otherwise search code hosts for the exact six-operation set signature.

## Cross-family interlock

The software-TWI, generic device-registry, RTC-device, time/calendar, and sensor-stream families
interlock: they share the positive status enum `0..12`, runtime registration into the
`0x200074xx`/registry records, and the `sys rtc` / `i2c_n` device naming. They most likely form
one proprietary platform layer inside Even Realities' B210 product tree and therefore share one
provenance fate — evidence resolving any one of them bears directly on the others.

## Clean-room routing decision

- Prefer Nordic SDK TWIM/TWI providers where peripheral availability, electrical routing, power
  ownership, and coexistence can be validated on owned hardware.
- If a software bus remains necessary, select a separately attributable and license-compatible
  provider, then implement only the R1 pin/configuration adapter and product lifecycle policy.
- Keep Goodix, GXT310 acquisition/register/calibration, and YHM2710 register/wire behavior behind
  their existing licensed-provider or evidence gates.
- Do not infer source ownership from generic I2C semantics or repeated compiler output.
- Do not expose a raw wire sender merely to exercise recovered transactions.

This decision uses all recoverable behavior while respecting the rule that identifiable or
potentially third-party implementation code is supplied by its vendor or another attributable
provider, not reconstructed locally.

## Attribution re-examination 2026-08

A full re-examination (instruction-level disassembly of all forty bodies from the rebuilt
image, exhaustive flash-pointer scans, upstream source comparisons) found no attributable
upstream: RT-Thread `i2c-bit-ops` was re-tested against fetched v4.1.0 source and rejected on
four concrete structural grounds (ops model, clock-stretching, ACK polarity, error signing);
Nordic, Linux/Zephyr, and sensor-vendor SDKs remain rejected. Build-path strings
(`product/B210/app/_build/B210_Application`, `..\..\..\platform\...`) place the engine in the
B210 platform middleware tree, identified as Wuxi Bravechip "ChipletRing" / BCL603M (see the
quantized-runtime sibling report). Verdict: NO ATTRIBUTION — family remains
`investigate_before_implementing`. Full evidence:
[`unknown_software_twi_provider_candidate-ATTRIBUTION-2026-08.md`](unknown_software_twi_provider_candidate-ATTRIBUTION-2026-08.md).

## Reduction 2026-08

Under the owner-authorized full reduction (2026-08-14, see
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md)), the forty ledger entries of
`unknown_software_twi_provider_candidate` (all four compiler-instantiated GPIO bit-bang buses and their shared helpers) are reconstructed
from the recovered decompilation evidence as independently compiled C in
[`../../reconstructed/software_twi/`](../../reconstructed/software_twi/).  The
reconstruction is not vendor source; it carries per-function provenance
banners, and its contract, reconstruction decisions, divergences, and
host-test mapping are documented in
[`../correlation/SOFTWARE-TWI-REDUCTION-CORRELATION.md`](../correlation/SOFTWARE-TWI-REDUCTION-CORRELATION.md).
The ledger disposition for the forty entries is now
`clean_room_reimplementation_owner_authorized`.  This document remains the
provenance record of why no upstream source was admitted.
