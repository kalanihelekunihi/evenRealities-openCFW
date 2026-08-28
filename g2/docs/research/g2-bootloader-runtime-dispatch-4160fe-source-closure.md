# G2 bootloader address-identified runtime dispatcher source closure

Status: software implemented and production-routed; physical validation blocked.

The complete 200-byte entry `[0x004160FE,0x004161C6)` has SHA-256
`ee5d5e11a21632f16c94cfe5ae2ae6251386e1387ae3e4c090031b7695ed944f`
and authenticated direct callers at `0x0042DDBE`, `0x0042E3AA`, and
`0x0042E616`. The address-derived name deliberately avoids assigning an
unsupported subsystem label.

The recovered three-argument ABI returns zero in critical context or when its
first scalar argument is zero. Its optional 28-byte record supplies scalar
arguments at offsets `0x00`, `0x08`, `0x10`, `0x14`, and `0x18`, a minimum at
`0x0C`, and a bit-zero enable flag at `0x04`. Defaults are zero, `0x100`, and
`0x18`; a supplied final scalar must be in `[1,56]`. A fully populated record
selects retained path A at `0x00417C7C`. An empty path-selection triplet uses
retained path B at `0x00417D16`, accepting its output word only when the path
returns exactly one. Mixed or invalid records return zero. Host tests pin all
short circuits, defaults, bounds, selection cases, six-/seven-argument AAPCS
ordering, output-pointer behavior, and return propagation.

`runtime_dispatch_4160fe.c` is a 3,805-byte MIT clean-room
implementation with SHA-256
`bab9266e01939a709741121492a9e3e8f3efd9439d5f4bfb43dd733862762fe5`.
Apple clang emits a 166-byte leaf at overlay offset 3,140/runtime
`0x004350BC`. Its unrelocated SHA-256 is
`196359baa9923c4e2a2cdc7c5626a53f14f19d901eaaff72b38ce169bad980b0`
and its relocated SHA-256 is
`d07956e54f4b3402066b46be77056fc7e5e6b393dbe048a194648f3d4085f4f9`.
Three strict `R_ARM_THM_CALL` relocations at offsets 14, 108, and 134 bind the
source-owned critical-context predicate and the two retained dispatch paths.
The stock entry is replaced exactly by `1ef0ddbf` and 98 Thumb NOPs.

Homebrew clang 22.1.8 emits a 164-byte leaf at profile offset 3,132/runtime
`0x004350B4`. Its unrelocated SHA-256 is
`95900ed30b19d426fc0f622d2f05b4c97f084867d27a95cea325e4ab8c10bbb7`
and relocated SHA-256 is
`eb93b1564f6365eaa0423c506b3184e4fbd5a2288d8eb7eadecfad53ba74fc74`.
Its relocation offsets are 14, 106, and 132 and bind the same reviewed graph.

The aggregate package and accounting values below record this historical
checkpoint and are superseded by the `0x004161C6` retained-value closure.

This extends the runtime tranche to nineteen entries at
`[0x00415844,0x004161C6)`: 2,398 exact stock bytes, 114 authenticated caller
edges, 2,194 canonical compiled Thumb bytes, and 34 strict relocations. The
canonical overlay is 3,306 bytes with SHA-256
`0e80c65a68663922d1f95ba6a69d92ea759c7ec8b9572adeb888ab28390e61ed`.
The 151,906-byte provider hashes to
`0aaf2db3ed7f97c10b68e9e964c76d7024caa8789a7c5a0c06935d4f7f063a26`,
has CRC-32C/MSB `0xDAA6F28F`, and accounts for 3,299 source, 3,850 patch,
eight alignment, and 144,749 retained authenticated bytes. It ends at
`0x00435162`, leaving 11,934 bytes before Apollo main. The Linux overlay is
3,296 bytes with SHA-256
`aefcf9a88ccc654bd87e60d786d6fd4055eeb6c6f1ee82d597b6dde58098c7fc`;
its 151,896-byte provider hashes to
`3fcc14b8a383e316c07b08ea0d810bc266bbec2ce00786b11181eee8c3c069de`.

The canonical unsigned package is 4,733,484 bytes with SHA-256
`c49c629d118e883df8036649b54cfef16af3d57308049b652fdcbf9f8d285073`.
Its 4,343,316-byte flash plan hashes to
`49285a05b7e7749b4f2fa709b7a213ff715756fd5980b22c09f5fea33230d98b`
and records 6,256 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,484 bytes with
SHA-256
`284fc01e45a0c6b03aa1d5e7e43cc81a80699b7df1acb25797a935b35c945995`;
its 2,311,859-byte plan hashes to
`ada2e7908905611037944944732d1608d0af9b965ab7a6f294c4b9ca25964b2e`
and records 3,324 placed regions plus the same two unresolved boundaries.

The next distinct complete callable body begins at `0x004161C6`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
dispatcher, retained-path, caller-path, or concurrency claim and does not
declare bootloader or firmware-wide functional completeness.
