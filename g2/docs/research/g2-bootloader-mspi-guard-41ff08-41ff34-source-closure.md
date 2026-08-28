# G2 bootloader MSPI guard source closure

The paired critical-section wrappers `[0x0041FF08,0x0041FF34)` now route to
two production C functions in `runtime_mspi_guard_41ff08.c`. The enter wrapper
always acquires the event-flags service and then disables MSPI when the bypass
byte at `0x200271C5` is not one. The exit wrapper conditionally enables MSPI
before always releasing the event-flags service. The asymmetry and call order
are intentional and match the authenticated stock control flow.

| Entry | Stock bytes | SHA-256 | Direct callers |
| --- | ---: | --- | --- |
| enter `[0x41FF08,0x41FF1E)` | 22 | `02963ef679faf897f9108a5e1526bd79eccabb28b11192d6325dfb4165ca0dc5` | `0x00420A48`, `0x00420B54`, `0x00420F98` |
| exit `[0x41FF1E,0x41FF34)` | 22 | `ecb3a585f0f910e6428aa9a722ff0f2a621ca1d195b8fd8b4a9d4f2820f0dddd` | `0x00420AD2`, `0x00420C0C`, `0x00420FE8` |

The shared literal at `0x00420AE0` is exactly `0x200271C5`. Host tests pin
both bypass branches and the precise acquire/disable and enable/release
ordering. Apple Clang and Linux Clang both emit relocation-free 36- and
32-byte leaves with SHA-256
`e900042722fccbebf61515c642ef2f75157022328550eaed47ecafa2465307eb`
and `dfb2fdd918afb3a3133234aa452430ab22ce73839c07e81914fa798ec49b4e40`.

The later XIP-config entry is now source-owned as well. The cumulative Apple
overlay/provider are 10,500 / 159,100 bytes with SHA-256
`28c298a0ab3273a8f5ade3e900268b80b879076a33dc12e504c73e42f623ba2c`
and `d1c9554cea1418c933767ca98b93a928a978cd66ed4c7d562b918acd6e351407`.
Linux identities are 10,484 / 159,084 bytes with SHA-256
`65ecb970600c878cc4ed7916cff4c57057d7baf83ef4923630340f2e5492b3c1`
and `21636af65f7eaa7b4e20c9e5d61902dfcaf20cd9ba13a6f6edf244bfa4d19fcd`.
Accounting is 10,487 source-owned, 11,782 generated patch, 14 alignment, and
136,817 retained official bytes across 170 functions, 151 relocated leaves,
and 168 patch sites. Apple headroom is 4,740 bytes.

Unsigned Apple/Linux packages are 4,740,678 / 4,516,672 bytes with SHA-256
`81ae4b1c4f87e3d6348aa55426f6c7f3cc766aa079d94a96ec82f3ffddc76b2d`
and `bb52277456ff2d69aaa34f4639734ab5d23bcea984f153ac19795b372955de71`.
Their flash plans are 4,514,624 / 2,405,251 bytes with SHA-256
`c2881ce57b2ece6918b7f8e8d2245a3efb61c36ca82bf150f8210ca4e8914a96`
and `24f543df6f2cdc6b78a43c93adf918eacbb79c3f4f0d675855e504c7cd065209`.
They contain 6,490 / 3,446 placed regions, two unresolved address regions,
five container-only regions, and six protected regions.

No signing, flashing, installation, reset, boot, MSPI or RTOS mutation, or
other hardware operation was performed. Live lock contention, MSPI timing,
and cold-boot behavior are explicitly blocked by unavailable physical
evidence: there is no authorized responsive right G2 temple and the left
temple must remain stock. Executable bodies after `0x0041FF60` remain software
gaps, so firmware-wide functional completeness is not claimed.
