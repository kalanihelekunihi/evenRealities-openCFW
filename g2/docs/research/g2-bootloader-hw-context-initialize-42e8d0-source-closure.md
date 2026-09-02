# G2 bootloader hardware-context initializer source closure

The authenticated interval `[0x0042E8D0,0x0042EA32)` is production-routed from
`runtime_hw_context_initialize_42e8d0.c`. Apple clang 21 and Homebrew clang 22
reproduce all 354 stock bytes after five strict configuration-read relocations.
The sole caller is `0x00430016`; there is no interior or stored-pointer ingress.
The Apollo-main analogue at `0x0055D94C` matches 339 of 354 bytes. Eleven
literal cells pin the slot table, retained state, profile buffers, defaults,
control register, and validity outputs.

The portable model covers index/output/occupied-slot rejection, 72-byte slot
claim and magic publication, retained and configuration-backed three-word
primary profiles, deterministic defaults on zero/error, retained and
configuration-backed two-word secondary profiles, control-bit clearing, and
both validity flags. The primary defaults are pinned as `0x4395C000`,
`0x3F839874`, and `0xBB8C47A1`.

Offline compilation, portable behavior, provider identity, manifest ownership,
and unsigned firmware assembly are verified. Live retained SRAM, configuration
storage, calibration meaning, MMIO control, peripheral response, concurrency,
reset, and cold boot are blocked by unavailable physical evidence. No signing,
flashing, reset, or hardware access occurred; functional completeness is not
claimed.
