# G2 bootloader address-index helper source closure

The two authenticated helpers at `[0x004213D8,0x004213E6)` are compiled from
maintained C and installed at their exact stock addresses. Their compiled bytes
are byte-identical to stock, so this ownership transition changes manifest
classification without changing the firmware provider or package payload.

## Recovered contracts

- `[0x004213D8,0x004213DA)` is the 32-bit identity mapping used by the caller at
  `0x004214BE`; bytes `70 47`, SHA-256
  `c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8`.
- `[0x004213DA,0x004213E6)` returns its input below `0x200`, otherwise adds
  `0x280` with 32-bit wrap. Calls at `0x004214E8`; SHA-256
  `742c0902623d3c2df2a28eaa1cde52792f9cf28dccd447d513720eb408f5392a`.

`runtime_address_map_4213d8.c` is 774 bytes with SHA-256
`db7dfe2cf26594cc89f30921196792e1f8dfc2a1fe67926bef421e776b906b41`.
Apple clang 21 and Homebrew clang 22.1.8 reproduce both exact bodies with no
relocations. The target-only inline assembly constrains the recovered
flag-setting instruction form; the host branch is behaviorally equivalent and
is tested at the threshold and wrap boundaries.

Canonical accounting is 15,351 source-owned, 16,386 generated patch, 16
alignment, and 132,087 retained official bytes, including 112 cave bytes and
14 exact in-place bytes. Apple/Linux providers remain 163,840 /
`a3b12625d63e769ab89d2bd9ea729e9b280ffa553f7c48a2e4b96974b60919e3`
and 163,824 /
`9e4494d967a6402ba329b05e664842404289ad9688ffa00aca7c0e5bf7908f9d`.
Apple/Linux packages remain
`1ad64997630cb2ebd2df43ae244bda8fda3008473f254adbebde8aa9d2045f5b`
and `3aba526397878e500d0b3ccfdc38b2dd171573b6099fbdb97369fde0ee2c7f01`.
The 4,569,828-byte canonical flash plan has SHA-256
`6570fe6cf7b172f99da733a26fe9964ea8c9f6985bfba2430359bd5fad874a4f`
with 6,567 placed regions.

No hardware operation occurred. The next retained executable body begins at
`0x004213E6`; firmware-wide functional completeness is not claimed.
