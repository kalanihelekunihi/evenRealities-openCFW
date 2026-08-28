# G2 bootloader event-flags service source closure

The complete event-flags service cluster `[0x0041FE62,0x0041FF08)` now routes
to three production C functions in
`runtime_event_flags_service_41fe62.c`. The implementation owns guarded static
creation, wait-forever acquisition, guarded release, and the three failure-only
EasyLogger records. It preserves the authenticated handle word at
`0x200270E0`, configuration at `0x00433CF8`, source-routed create/acquire/
release entries, and source-routed EasyLogger output seam.

The authenticated stock spans are:

| Entry | Stock bytes | SHA-256 | Direct caller |
| --- | ---: | --- | --- |
| init `[0x41FE62,0x41FE9C)` | 58 | `b5dbeb76a423f8cea25297e99a8287c96fd07ff2734beaa0551aefb3d4842c8c` | `0x0042051C` |
| acquire `[0x41FE9C,0x41FED4)` | 56 | `29b06ffce120996862a184169a3fb2f17e46787672085d79977eaa979500244c` | `0x0041FF0A` |
| release `[0x41FED4,0x41FF08)` | 52 | `9a3c0274be0fd350c7090add8b8adcccec4dea0fdb2a9c93a7733c1fd965e681` | `0x0041FF2E` |

Host tests pin idempotent initialization, handle publication, null-handle
guards, the `0xFFFFFFFF` acquire timeout, return-status handling, and exact
logger arguments. The logger records use level one, tag `0x00433CD8`, file
`0x00431540`, functions `0x0043376C`/`0x00433784`/`0x0043379C`, lines
`0xBA`/`0xC3`/`0xCC`, and formats
`0x004329FC`/`0x00432CA0`/`0x00432A24`.

Apple Clang emits relocation-free leaves of 76, 68, and 64 bytes with
SHA-256 `845174df…`, `214d0a00…`, and `8afbc2c1…`. Linux Clang emits the
same sizes with SHA-256 `ee08db7d…`, `316e136c…`, and `7e1820b3…`.
The 166 authenticated executable bytes are replaced by 208 source-owned
Thumb bytes.

The later guard and XIP-config entries are now source-owned too. The current
cumulative Apple overlay/provider are 10,500 / 159,100 bytes with SHA-256
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
Their flash plans contain 6,490 / 3,446 placed regions, two unresolved
address regions, five container-only regions, and six protected regions.

No signing, flashing, installation, reset, boot, event-flags mutation, or
other hardware operation was performed. Live RTOS scheduling, contention,
logger, and cold-boot behavior is blocked by unavailable physical evidence:
there is no authorized responsive right G2 temple, and the left temple must
remain stock. Executable bodies after `0x0041FF60` remain software gaps, so
firmware-wide functional completeness is not claimed.
