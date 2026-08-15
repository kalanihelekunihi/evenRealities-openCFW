# QST QMA6100 complete source reduction

Snapshot: 2026-08-14. The three QST-lineage provider interiors and all fourteen
coupled R1 adapter functions are now reconstructed as independently compiled C
under `reconstructed/qma6100/`. This is decompilation-derived behavior, not QST
or Even Realities source. The unlicensed public QST V1.0 snapshot remains
correlation evidence only and is not a build input.

## Exact function closure

All hashes below are over the stock application image at load base
`0x00027000`, image SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

| Entry | Bytes | SHA-256 | Reduced role |
| --- | ---: | --- | --- |
| `0x0006F404` | 20 | `a569ba70d7ed024938ee16539bf0a7182af65ee069a91bf455a3a2e443b0a1ff` | locked chip-ID wrapper |
| `0x0006F418` | 30 | `bf5cdade8e56223363c4429f1dce08d62170ad08a89094c3f9805a10a6ddc7b5` | locked fixed-25-Hz configuration wrapper |
| `0x0006F436` | 18 | `443a2fac2784fd3089a8fbbc773d19872dce3ffb6e584a1ae30ef17a0b0f4ed0` | locked IRQ wrapper |
| `0x0006F448` | 84 | `a1188526e84dbec45782d4201f866cc3d17d746db9e187633f71bffcc5f8c3dc` | locked FIFO wrapper and signed axis `/4` normalization |
| `0x00086D40` | 238 | `936861ba9a194a2a34bc8d2dfcbf810771e279edabca38842b74914256b41562` | any-motion configuration |
| `0x00086E34` | 18 | `9150e53e6c6413f7361a9e9ceeca3c25168a088f1afeb0554bb9a3a8bc87d013` | chip ID read |
| `0x00086E48` | 28 | `df77f9d30ead57426f5663a1fd4683a40d72dd98537f950d553de8d4eec00b33` | 64,000-cycle delay port |
| `0x00086E68` | 110 | `c5d03aad9ed018efc702937ee49b081151389bd58baaca0d589ae89309dfd855` | `0x12`/`0x13` identity and axis layout |
| `0x00086EE4` | 194 | `3094056552e7a4390cd5efd5ccf2ff66ee4e87b924fa6fd71e09cec353c82327` | complete rate/range/FIFO/step/motion/tap init |
| `0x00086FA8` | 72 | `05cdb478b4f6fd9eaadd02811cdb387e54ee3e14c6cb978a7777586c9d4ac84c` | IRQ status and two callback slots |
| `0x00086FF4` | 190 | `d8c52ede55f6ae0e52d977d9ed8f4ca95b27b130e9c80e7d3df85dd637ae7468` | bounded 64-sample FIFO read |
| `0x0008714C` | 56 | `70bb77aa7bae95986e45eba2299c6176125dcdaef31b31f8490c2c8a9d90cf56` | five-attempt read transport |
| `0x00087188` | 56 | `ed4e473b41a6125acb9c1260643621d0741429f05585785b5e293b0dee9de81b` | range and LSB/g mapping |
| `0x000871C4` | 138 | `7f40093f45ba9195467bf2832cbbb0a2199dbd0d2425ddb453a6b231534ca22d` | reset and bounded readiness polls |
| `0x00087250` | 144 | `8394647f708e2560968e4fd1396ca08fa57411632c16a15d79dc0c38f363b39d` | step configuration |
| `0x000872E4` | 268 | `617fe1f9d6ef12a232744a1ca8f4941b031c4246af62a6664349aa9fae49dc1b` | tap mask and route configuration |
| `0x000873F4` | 46 | `581ff53e52acf319d5f51d4c011e5f2fdb57fd6b68322f66ca6bb055855003a9` | five-attempt write transport |

## Preserved behavior

The implementation preserves the `0x12` then `0x13` address search; acceptance
of ID `0xFA` or any `0x9x` QMA6100P ID; the exact 2/4/8/15-g sensitivity map;
reset sequence and 102-attempt bounds; 25/50/100/150/200-Hz register mapping;
step, all-axis any-motion, and `0x31` tap mask; IRQ bits for any-motion and
double-tap; five-attempt transport loops; 64-record FIFO bound; six-byte XYZ
records; and arithmetic right shift by two.

Every hardware dependency is a typed callback: address-aware register read,
register write, 64,000-cycle delay, lock, unlock, and event delivery. No binary
provider remains. The generic motion selector now accepts QMA6100/QMA6100P as
the third stock-order provider and supports an explicit forced-QMA policy.

## Intentional hardening

Unlike the stock initializer, transport or readiness failure propagates as an
explicit failure instead of returning success unconditionally. FIFO payload
read and FIFO-reset failures propagate as `QMA6100_FIFO_ERROR`; null pointers,
invalid event routes, and absent callbacks fail without dereferencing. These
changes preserve successful-path register behavior while enforcing the
project's fail-closed source-reduction policy.

`tests/test_reconstructed_qma6100.c` covers the identity rules, retry counts,
range table, reset, step/tap/any-motion registers, complete configuration,
event bits, FIFO limit, lock bracketing, and negative-axis normalization.
