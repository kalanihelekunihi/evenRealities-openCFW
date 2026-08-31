# G2 bootloader LittleFS directory-bootstrap source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Scope and authenticated boundary

This increment replaces the complete Apollo510B bootloader body
`[0x004210C8,0x004211B0)` with clean-room compilable C. The 232-byte stock
body has SHA-256
`f4f1aea508ed9f9a63a310c36cf80053a49b45324d8872cd5507116db495be8c`.
The 214-byte predecessor literal/alignment pool
`[0x00420FF2,0x004210C8)` remains retained with SHA-256
`21ac43cfda25ec0bc55b6df8e70c3341923392c939cf989b96f0945e7b151ba3`.
The 96-byte successor initialization entry `[0x004211B0,0x00421210)` remains
retained with SHA-256
`9c3d0c94a411e7e0a666d918d23a0c8f4eefecd2d5a32761767786bf1f47bc08`.
Its direct calls to this service are at `0x004211EC` and `0x00421252`.

## Recovered behavior

The routine checks four initialized read-only paths: `/firmware`, `/ota`,
`/user`, and `/log`. For each path it invokes the bootloader LittleFS
directory-open wrapper using the filesystem object at `0x20026878` and a
52-byte directory handle.

- `LFS_ERR_NOENT` (`-2`) causes one mkdir attempt. Status `0` logs creation;
  `LFS_ERR_EXIST` (`-17`) logs the concurrent/already-existing case; every
  other mkdir error is logged but deliberately does not fail the overall
  iteration.
- Status `0` means the directory is present. The routine closes the directory,
  ignores the close status, logs presence, and continues.
- Any other directory-open status is logged, stops iteration, and returns
  `-1`.
- Completion of all four paths returns `0`.

The retained ABI seams are the LittleFS wrappers at `0x00415288` (directory
open), `0x0041527E` (mkdir), and `0x0041531C` (directory close), the fixed
filesystem object, and authenticated path/logging literals. Logging routes to
the already source-owned EasyLogger output function. The clean-room source
contains no stock implementation bytes.

## Production routing and reproducibility

The stock span is replaced by a wide Thumb branch plus NOP fill. Apple clang
emits a 220-byte leaf at overlay offset 14,592 / address `0x00437D78`; its
unrelocated SHA-256 is
`39fdef6b959bb5771f637ac6084bc6ce5f357aa7a32288e6a15cbe0f90d569d8`
and relocated SHA-256 is
`456bcb6e3fb5bb820e3f400352787f03419828d247956407e06ca3fadb853f72`.
Homebrew clang emits a 224-byte leaf at offset 14,568 / address `0x00437D60`;
its unrelocated SHA-256 is
`483c3eae1b1705449789eaa79d38b00095c2b0487ecb0c7c21dcbda390202b73`
and relocated SHA-256 is
`a484dd2c786d362aa148cca79100264d1bda289ecddc73affcf4d7ebdd304edf`.
Both profiles pin two strict calls to the profile-specific source-owned
EasyLogger output leaf.

Apple/Linux overlays are 14,812 / 14,792 bytes with SHA-256
`b905e2c189923c066846c170cea5a7cc0846d46167e7776b365fa4847b341077`
and `0771eb5b5e297b6d5cb2336cd5f9b3f0ad75ac40021f30621f5c73e79b01e341`.
Providers are 163,412 / 163,392 bytes with SHA-256
`bc6a6219ba7e2122b85226f4e6410fd4c3d8d12a19669ad8088efd8f5db657ff`
and `a6f58437a7ed56269d11aabb89df892f1478c10601b30e0594acf66d2a640cf8`.
Provider accounting is 14,797 source-owned, 16,044 generated redirect, 16
generated alignment, and 132,555 retained official bytes.

Unsigned Apple/Linux packages are 4,744,990 / 4,520,980 bytes with SHA-256
`c4ba624de37c01d582906ccb12e0f32754e26aa56e81cc07f64baeeb5611f4ff`
and `383530bba102ce67f95626d87344cba4bc2c382904d3ff76616ad51b67b2d35c`.
The Apple flash plan is 4,558,294 bytes with SHA-256
`dc4b362e725457613d19bb82bd2ea4280b4151ecc50617d98acce6b44eb130e8`;
it records 6,551 placed, two unresolved, five container-only, and six
protected regions.

Five focused tests authenticate boundaries, literals and callers; cover all
present, created, concurrent-existence, nonfatal mkdir-error, ignored-close,
fatal directory-check, and early-stop branches; and compile the source for
Cortex-M55. The aggregate bootloader closure includes these tests plus all
dependency, routing, provider, package, analyzer, and manifest gates.

## Physical-evidence block

No signing, flashing, erase, reset, boot, filesystem mutation, MSPI command,
or other hardware operation occurred. There is no authorized responsive right
G2 temple, and the left temple must remain stock. Live mount state, directory
creation/close behavior, power-loss behavior, external-flash persistence,
logging, and cold-boot qualification are therefore explicitly blocked by
unavailable physical evidence. This closes one software gap only. The next
authenticated executable frontier is `0x004211B0`.
