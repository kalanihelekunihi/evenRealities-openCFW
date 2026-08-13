# Goodix GH3X2X biometric provider boundary

## Decision

The application embeds `gh3x2x-v2.23_7ecd2a`, `Gh3x2x*` names, Goodix demo initialization and
sampling diagnostics, configuration-slot management, watermarks, and the demo `MultiSensor` event
queue. Goodix's own developer community publishes matching `Gh3x2xDemoInit`, demo/driver/config/
algorithm version, slot, sampling, and interrupt diagnostics for its official GH3X2X libraries.
This establishes a Goodix SDK/demo lineage, but no lawfully redistributable SDK matching the exact
R1 version has been admitted.

The ownership ledger now separates 392 provider/demo functions across the individually reviewed
set, direct-call-graph closures, the exact branch-only thunk, GH_NADT, GH_HR, GH_HRV,
GH_SPO2/dlCom, private-context, packed-channel, quality, peak-mask, accumulation, and register-profile
closures, plus 17 distinct R1 product adapters. All provider/demo bodies remain
`goodix_gh3x2x_candidate` with disposition
`vendor_source_required_not_redistributable`. Power, transport, lifecycle, recovered profile-mask,
reference-count, and command-routing bodies are `r1_goodix_provider_adapter` and are the only part
authorized for clean-room implementation. The adapter fails closed when a licensed provider is not
bound; it does not emit synthetic biometric measurements.

Five of the individually reviewed functions close duplicate packed-word integrity helpers. Their
complete callers, exact bodies, and three identical constant-table copies are documented in
[`GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md`](GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md). That
classification uses Goodix-rooted callgraph context; byte identity is corroborating evidence only.

The 32-function / 14,064-byte GH_NADT census, including its already gated version builder and 31
newly routed processing functions, is independently segment-, hash-, and callsite-pinned in
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](GOODIX-NADT-PROVIDER-BOUNDARY.md). It is provider code, not a
clean-room implementation target.

The separate GH_HR processing closure routes 31 additional functions / 7,144 bytes, including the
2,814-byte feature/event decision core at `0x00032808`. Every direct caller is within the closed
Goodix component. See
[`GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md`](GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md).

The GH_HR private-context closure also includes the 372-byte initializer at
`0x00072C48`. Its sole caller at `0x0006D2B4` allocates the exact 0x158-byte
secondary context inside the already gated `pv_v1.1.0` initializer. It clears
that private object and constructs provider-owned buffers using adjacent Goodix
runtime helpers. The layout and defaults are evidence only and are not
implemented locally.

The GH_SPO2/dlCom closure adds 84 exact functions / 19,204 executable bytes: 81 formerly
unclassified Ghidra functions plus three valid dispatcher-table wrappers omitted by Ghidra. It
connects the already gated `0x0002C944` entry to processing root `0x0006C6A8`, then pins the
generated graph builders selected by the table at `0x000BCF58`. Shared runtime callers are
explicitly retained without asserting exclusivity. This includes the indirect 1,120-byte
quantized recurrent executor at `0x000739A8`, its constructor, and four helpers. It also gates the
dormant `0x000617F8`/`0x000876C8` generated graph pair using the shared dlCom
configuration object and provider callback edge without treating them as a production path. The
same wrapper is the sole caller of the 984-byte `0x0006CCC0` algorithm-input diagnostic formatter,
which remains provider code rather than an R1 telemetry implementation. See
[`GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md`](GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md).

## Byte-pinned functions

| Recovered entry | Size | Recovered provider/demo role |
| --- | ---: | --- |
| `0x00029D58` | 4 | exact branch-only thunk to gated provider entry `0x0002B91C` |
| `0x0002A0F4` | 110 | GH3X2X algorithm-version dispatcher |
| `0x0002A380` | 166 | GH3X2X wake-up confirmation diagnostic |
| `0x0002A55C` | 4 | exact `GH(M)3X2X_DEMO_v1.6_AC_v0.5` version getter |
| `0x0002A598` | 4 | exact driver-library `v4.3.0.0` version getter |
| `0x0002A614` | 4 | exact thunk into the GH3X2X path |
| `0x0002A754` | 152 | provider initialization core reached by `Gh3x2xDemoInit` |
| `0x0002AAD0` | 6 | provider callback setter |
| `0x0002AADC` | 24 | provider operation-callback registration |
| `0x0002AAF8` | 54 | SPI-operation registration with provider-owned state |
| `0x0002ABFC` | 14 | algorithm-enable state setter |
| `0x0002AC1C` | 16 | provider sampling-parameter setter |
| `0x0002C2EC` | 222 | config application-mode search diagnostics |
| `0x0002CD00` | 132 | configuration-index/slot diagnostics |
| `0x0002D670` | 238 | configuration switch diagnostics |
| `0x0002D824` | 78 | enabled-algorithm output dispatcher |
| `0x0002D87C` | 480 | `Gh3x2xDemoInit` demo, driver, config, and algorithm version reporting |
| `0x0002DB8C` | 958 | `Gh3x2xDemoInterruptProcess` state and warning diagnostics |
| `0x0002E0D0` | 454 | demo mode and watermark management diagnostics |
| `0x0002E358` | 144 | demo start-sampling wrapper boundary |
| `0x0002E36C` | 418 | `Gh3x2xDemoStartSampling` and configuration-error diagnostics |
| `0x0002E61C` | 76 | provider array/config diagnostic |
| `0x0002E6A8` | 42 | demo stop-sampling wrapper boundary |
| `0x0002E6BC` | 60 | `Gh3x2xDemoStopSampling` diagnostic |
| `0x0002E778` | 40 | demo algorithm-state reset |
| `0x0002E7C4` | 174 | GH3X2X configuration-version reporting |
| `0x0002E964` | 374 | current slot-enable diagnostics |
| `0x0002EB84` | 444 | Goodix demo `MultiSensor` event handling called from the interrupt path |
| `0x0002EDEC` | 10 | demo state initializer |
| `0x0002EE28` | 10 | demo event-state initializer |
| `0x0002EE50` | 36 | demo multisensor-state initializer |
| `0x0002EF6C` | 210 | Goodix demo `MultiSensor` event dump path |
| `0x0002F0F8` | 10 | demo output-state initializer |
| `0x00032788` | 88 | NADT output wrapper linked to the exact version builder |
| `0x0005A5EC` | 54 | GH_HR integrity-bit encoder called by the heart-rate core |
| `0x00066840` | 46 | exact `dsp_pv_v1.3.0_30234f22` version builder |
| `0x00066890` | 14 | shared GH3X2X version qualifier helper |
| `0x0006A020` | 8 | retained GH3X2X provider thunk |
| `0x0006A4D8` | 376 | provider algorithm-output callback dispatcher |
| `0x0006A500` | 110 | provider configuration-table loader |
| `0x0006D204` | 406 | GH_HR private-context initializer; exact `pv_v1.1.0`, sole caller in the gated output wrapper |
| `0x00072C48` | 372 | GH_HR 0x158-byte private subcontext initializer; sole caller `0x0006D2B4` in the gated primary initializer |
| `0x0006D3C0` | 96 | heart-rate output wrapper linked to the exact version builder |
| `0x0006D424` | 180 | exact `GH_HR_exc_pv_v2.0.3.0_CONF_nc_21d2063d_002271a1` version builder |
| `0x0006D51C` | 1382 | heart-rate algorithm core using the integrity-bit encoder |
| `0x0002CAC6` | 18 | GH_HRV cleanup dispatcher wrapper |
| `0x0002CC5C` | 46 | GH_HRV output dispatcher wrapper |
| `0x0006DA9C` | 4 | GH_HRV configuration getter |
| `0x0006DAA4` | 30 | GH_HRV private ABI-version copier |
| `0x0006DAD0` | 126 | GH_HRV lifecycle cleanup |
| `0x0006DB58` | 4 | GH_HRV cleanup thunk |
| `0x0006DB5C` | 926 | GH_HRV lifecycle initializer |
| `0x0006DF14` | 76 | HRV output wrapper linked to the exact version builder |
| `0x0006DF60` | 58 | exact `GH_HRV_pre_pv_v1.0.1.0_ed953ff3` version builder |
| `0x0006E788` | 126 | exact `GH_NADT_pre_pv_v1.0.2.0_nc_548d894d` version builder |
| `0x0006EC28` | 100 | SpO2 output wrapper linked to the exact version builder |
| `0x0006EC90` | 182 | exact `GH_SPO2_pre_pv_v2.1.10.0`, driver, network, DSP, and `dlCom` version builder |
| `0x000759F4` | 20 | GH_HR input integrity validator; formerly misclassified as LIS2DW12 glue |

Goodix's [GH3220 developer trace](https://developers.goodix.com/zh/bbs/detail/c7d1af01d0e8467cac183bc66c74cdb9)
prints the same algorithm names, versions, component hashes, demo messages, and driver identifier.
An additional [official-library trace](https://developers.goodix.com/en/bbs/detail/4de13ec5986d4d989deee3887d43faf2)
shows the same `Gh3x2xDemoInit` and `GH3X2X_RegisterSpiOperationFunc` topology and identifies
`gh3x2x_demo_user.c` as the configuration source. A Goodix employee's
[desktop-demo response](https://developers.goodix.com/zh/bbs/detail/875147b152034370a8d4d2037c71edbb)
describes a separately supplied C# reference/tool interface rather than publishing a portable SDK.
These primary-source matches correct an earlier classification of the HRV version builder as a
GoMore marker and support the proprietary provider gate; they do not establish redistribution
rights. The verifier pins exact size and SHA-256 for every listed body.

The complete nine-function / 1,288-byte GH_HRV lifecycle is independently pinned in
[`GOODIX-HRV-PROVIDER-BOUNDARY.md`](GOODIX-HRV-PROVIDER-BOUNDARY.md). Seven formerly unclassified
functions / 1,154 bytes are now gated with the already classified output and identity builders.
No HRV preprocessing state, allocation, or calibration implementation is admitted locally.

## Direct-call-graph closure

The frozen undirected component inside `0x00029F88..0x0002F107` contains 149 recovered entries:
32 individually reviewed Goodix seeds from the table, 116 additional provider candidates, and the
separately resolved Nordic `nrfx_gpiote_irq_handler`. Twenty-five isolated functions in that same
address interval remain unclassified instead of being swept in by proximity. The complete 116-entry
set is recorded in `FUNCTION-OWNERSHIP.csv`; its entry-set SHA-256 is
`4decf6432c5a96fd2594f87f497c087c625988aa6e093fbbefcf5b04e0367cb9`, and the aggregate of every
`entry:size:function-SHA-256` record is
`75c4f2bbe38b623a1d8c31642c450ea49e118016fadfda9bf0029f11eb596d2d`.

This remains a conservative provider gate, not a claim to private Goodix symbol names. Tiny generic
thunks that happen to BSim-match unrelated SDK thunks are kept in this candidate closure because
such non-unique matches do not prove authorship. Licensed-source comparison must resolve them more
finely before any body becomes eligible for local implementation.

## Clean-room R1 adapters

| Recovered entry | Clean-room role |
| --- | --- |
| `0x0005036C` / `0x00050372` | optical transport release/prepare |
| `0x00050870` | stop recovered stock masks `0x2000`, then `0x4000` |
| `0x00050892` / `0x000508B6` | prepare, initialize, and start recovered masks `0x4000` / `0x2000` |
| `0x000508DA` | bounded identity probe lifecycle |
| `0x00050904` | switch configuration, clear mask `0x42`, then start mask `0x02` or `0x40` |
| `0x000509A4` / `0x000509B0` | board-line release/prepare |
| `0x000509E0` | bounded initialization probe |
| `0x00050AB0` | secondary board-line release |
| `0x00050AE0` / `0x00050AF0` | optical power enable/disable |
| `0x00050BE0` | reference-counted product release policy |
| `0x0006249C` / `0x000624C8` | command routing for recovered masks `0x02` / `0x40` |

The implementation is in `r1/src/r1_goodix.c` with its public boundary in
`r1/include/openr1/r1_goodix.h`. Tests pin call order, delays, mask values, error rollback, and
provider-absent behavior. The names of the masks intentionally do not claim vendor-private
algorithm meanings that the evidence has not established.

## Admission requirements

Enabling the optical path requires a lawfully obtained matching Goodix GH3X2X SDK, recorded
version and hashes, target/ABI verification, license and redistribution review, and function-level
separation of driver/algorithm bodies from R1 SPI, reset, interrupt, allocation, logging,
configuration, and health-event adapters. Observable host-side behavior models may be retained as
compatibility tests, but they are not production substitutes for Goodix biometric algorithms.
