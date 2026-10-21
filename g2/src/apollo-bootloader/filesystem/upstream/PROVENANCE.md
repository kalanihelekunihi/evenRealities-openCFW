# littlefs source provenance and compile record

This directory contains only the upstream littlefs core and its license, copied
from the GitHub codeload archive for the exact superproject-pinned commit.
No submodule worktree, gitlink, index entry, or firmware/component source was
changed.

## Source identity

- Repository: <https://github.com/littlefs-project/littlefs>
- Pinned commit from `git ls-tree HEAD third-party/upstream/littlefs`:
  `0494ce7169f06a734a7bd7585f49a9fa91fa7318`
- Download URL:
  <https://codeload.github.com/littlefs-project/littlefs/tar.gz/0494ce7169f06a734a7bd7585f49a9fa91fa7318>
- Downloaded archive SHA-256:
  `2609c3531a88e8f4fbc242bc0a4be1fe70d9428d423f2b8d8c581f8d72a7e100`
- Source fingerprint: v2.10.1 (the repository's recovered attribution is
  recorded in `g2/docs/reference/libraries.md` and is independently associated
  with this exact pinned commit).

SHA-256 of the copied upstream files:

| File | SHA-256 |
| --- | --- |
| `lfs.c` | `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `lfs.h` | `ee44e99d6b19119b3e577b969b80c9d5e6f96410c9593794afddf6d4b314c486` |
| `lfs_util.c` | `f2fbde533670560434bd9f5a547174cc7c5a4670a02c47b4bd85180dced8b2ec` |
| `lfs_util.h` | `f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e` |
| `LICENSE.md` | `0cb4ff1daf5fdc1359c6a6ee3116092f08fc100c9d58b1b77ab17bfd801f856d` |

The archive was fetched on 2026-10-06 and extracted without modifications.
The download SHA verifies the fetched archive bytes; per-file hashes identify
the exact copied source/license files.

## Independent translation-unit compile

Both upstream implementation files compiled independently for host and ARM.
The compile used the upstream default configuration: no `LFS_CONFIG`,
`LFS_DEFINES`, or `LFS_*` configuration override was supplied. This is a
compile smoke check only; it does not reproduce the bootloader's IAR objects.

- Host compiler: Apple clang 21.0.0; target `arm64-apple-darwin27.2.0`.
- ARM compiler: Apple clang 21.0.0; target `arm-none-eabi`, Cortex-M55,
  Thumb, EABI5. `/Applications/Xcode-beta.app/.../MacOSX.sdk/usr/include`
  supplied standard C declaration headers because this environment has no
  bare-metal sysroot; the produced objects are freestanding ELF, not linked
  against the macOS SDK.
- Common options: `-std=c99 -O2`; ARM additionally used
  `-ffreestanding -fno-builtin`.
- Result: both `lfs.c` and `lfs_util.c` compiled successfully for both targets.
  Output object files were written to `/tmp/littlefs-host/` and
  `/tmp/littlefs-arm/` and are not part of this source snapshot.

Host object SHA-256: `lfs.o`
`b9105d308a7c553a774ad50c78f9f27b6df2782cf59edd237d866f74e47cdac4`,
`lfs_util.o`
`6f8613a6ffdadeb05b0c3bac303f681d26ec688bb1382b2807438126034bac43`.

ARM object SHA-256: `lfs.o`
`7f204eab8aa59ee3807d51661adb9f93ab40224a2200299f26a0777bae4a304b`,
`lfs_util.o`
`ec32d9da53543f1d31363628709ca1f21ffc87d2e651e33b7a6fcd358b49c480`.

## Scope limit

This establishes availability of the pinned open source and successful host
and ARM translation-unit builds. It does not establish the bootloader's exact
littlefs configuration, compiler settings, IAR code generation, selected
object/link order, placement, or byte identity.
