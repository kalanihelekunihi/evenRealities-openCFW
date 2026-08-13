# Internal flash, FDS, and FAL correlation

## Decision

The firmware name `device_flash` refers to **nRF52840 internal flash**, not an external NOR part.
The production adapter reads `FICR.CODEPAGESIZE`, `FICR.CODESIZE`, and the bootloader boundary in
`UICR.NRFFW[0]`; it assigns the 36 pages immediately below that boundary to the seven-entry FAL
partition table. Nordic `nrf_fstorage` owns erase/write operations and the nRF52 memory map supplies
reads. openR1 therefore links Nordic SDK 17.1.0 and upstream FAL 0.5.99, while local code contains
only recovered geometry, bounds, synchronization, and provider-binding glue.

The generic stock device registry around `0x00085CE0...0x00085DA8` is not reproduced. It is not
needed in the clean implementation because the single recovered flash provider is bound directly
to FAL. This avoids inventing or copying an unresolved framework implementation.

## Exact installed layout

The captured UICR image has SHA-256
`1a6dc7725aa1903ed240dd245ecd036a6c72b244e8b26179affdd0fdde74b150`, with
`NRFFW[0] = 0x000F8000` and `NRFFW[1] = 0x000FE000`. The application and initialized-RAM evidence
therefore establish:

| Range | Pages | Owner |
| --- | ---: | --- |
| `0x00027000..<0x000D1000` | 170 | maximum openR1 application link region |
| `0x000D1000..<0x000D4000` | 3 | Nordic FDS / Peer Manager |
| `0x000D4000..<0x000F8000` | 36 | R1 `device_flash` / FAL partitions |
| `0x000F8000..<0x000FE000` | 6 | bootloader |
| `0x000FE000..<0x000FF000` | 1 | MBR parameter page |

The stock FDS initializer at `0x00063EB8` first subtracts `0x24000` from the bootloader boundary,
then subtracts `0x3000` for its own three pages. Its complete 204-byte body is pinned by SHA-256
`9fa3e325b3955765dcda42a277d30292ba377611d54ef89d2a5032b71695abd7`. Accordingly,
`FDS_VIRTUAL_PAGES_RESERVED` is 36 and the linker ends before `0x000D1000`; neither provider can
silently overlap application code, each other, or the bootloader.

If `NRFFW[0]` is erased, both the stock adapter and openR1 fall back to
`FICR.CODEPAGESIZE * FICR.CODESIZE`. The relative arrangement remains the same. The SDK port also
checks the runtime page size, physical capacity, boundary alignment, and range before enabling
storage.

## Recovered adapter map

These ten complete functions define the product/provider seam. The ownership ledger pins each
extent and digest; the decompilation is used only for R1 behavior and configuration.

| Entry | Bytes | Compatibility role |
| --- | ---: | --- |
| `0x00054970` | 24 | optional pre/post-operation callback configuration |
| `0x0005498C` | 90 | erase request and 36-page geometry query |
| `0x000549F0` | 78 | dynamic boundary calculation and Nordic fstorage configuration |
| `0x00054A4C` | 58 | bounded memory-mapped read wrapper |
| `0x00054A8C` | 20 | `device_flash` registration and operation-table binding |
| `0x00054AA4` | 72 | serialized Nordic write wrapper |
| `0x0005C40C` | 80 | page-rounded Nordic `nrf_fstorage_erase` adapter |
| `0x0005C464` | 24 | memory-mapped byte read adapter |
| `0x0005C480` | 62 | word-rounded Nordic `nrf_fstorage_write` adapter |
| `0x00071054` | 50 | device lookup, geometry query, and FAL binding |

The scatter-initialized descriptor is at `0x20006F98`; its operation table is at `0x20006FC4`.
The operation pointers are `0x000549F1`, `0x00054A4D`, `0x00054AA5`, `0x0005498D`, and
`0x00054971`. The static parser
`summarize_r1_flash_layout.py` verifies the
descriptor, table, functions, FDS separation, UICR layout, and every partition record without
accessing physical hardware.

## Clean implementation

`openr1_storage.c` defines a separate Nordic
`nrf_fstorage_sd` instance over the recovered 36-page region. Reads, writes, and erases remain
bounded to that instance. Mutations are word/page aligned and serialized through CMSIS-RTOS2;
accepted asynchronous operations complete through Nordic's event callback before the synchronous
`r1_flash` seam returns. Because that callback is dispatched by `nrf_sdh_evts_poll`, mutations from
the SoftDevice event thread are rejected instead of deadlocking it; a production persistence
consumer must call the synchronous seam from a separate worker. The port binds the already tested generic `r1_flash` interface to
unmodified upstream FAL and requires all seven recovered partitions to initialize.

The linked image retains the storage API, Nordic fstorage calls, FAL initializer/device lookup, and
the local binding. FlashDB 2.0.0 remains the provider for `health.db`; `kv.bin` and `sleep.db` use
their separately documented R1 formats.

## Safety and remaining validation

There is no BLE or host raw-flash command. The port cannot address application, FDS, bootloader,
MBR-parameter, UICR, or signing regions. `pKey.bin`, `ep.bin`, destructive format, and raw export
remain policy-gated. Host NOR, FlashDB/FAL integration, source-admission, linked-image, sanitizer,
and freestanding builds pass. The production runtime does not yet instantiate the KV, sleep, or
health database consumers over this provider. Their non-SoftDevice worker integration, on-device
power-loss behavior, SoftDevice queue saturation, FDS coexistence, and migration against an
owner-authorized ring image still require physical validation.
