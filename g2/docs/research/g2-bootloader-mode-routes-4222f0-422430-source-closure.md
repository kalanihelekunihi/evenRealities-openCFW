# G2 bootloader mode routes and cleanup source closure

Four authenticated executable bodies in `[0x004222F0,0x00422430)` now compile
from maintained clean-room C at their exact stock addresses. Apple clang 21
and Homebrew clang 22.1.8 reproduce all 320 executable bytes exactly. The
preceding 30-byte and following 56-byte padding/literal pools remain separately
authenticated official data rather than being mislabeled as source code.

The enable and disable routers accept kinds `0..6`, reject every other kind
with status `6`, and reject client bit indices at or above `57` before
dispatching to the exact row-specific maintained service. The all-row cleanup
checks the same bit bound, queries each of the seven bitmap rows, and invokes
the disable router only where the client is present. The configuration helper
rejects a null source and otherwise copies exactly 20 bytes to the retained
configuration object at `0x20007C00`.

`runtime_mode_routes_4222f0.c` is 7,036 bytes with SHA-256
`750665e311ca52e75a71d39cdc0003de5c8f22dbcf70e51ea68dc30e81fd6b9e`.
The installed enable-route body is 116 bytes with SHA-256
`53cfb358989e68ae979d2814964a3e779ae0f0eba76836f99d409393d0e78d51`
and unrelocated SHA-256
`f3af3040562b398547cae8f8ec3b499ab5f3d98899fe161d63e0bfae61fa6370`.
The disable-route body is 116 bytes with SHA-256
`6a131868a276083764d4714178857124ccb4209a5f3e7552d874aba7f7c1a54e`
and unrelocated SHA-256
`cd4068554d79e3feac30e6da08adb502620ff09a2d52e1f9c19f18318298fb5b`.
The all-row cleanup body is 62 bytes with SHA-256
`97df45d0a88884e084088713a4325d6ce4b653e934a9c60ff72b13db31996fa1`
and unrelocated SHA-256
`51b38dff9b2200212ee9b9bcf6d84eafff50147bcfc3bad6407952729275373f`.
The fixed configuration-copy body is 26 bytes with SHA-256
`4d1631a1cd2b6aeb1ee196dd1039c51e339eb82c19bf0845a285f98839a00a8d`
and unrelocated SHA-256
`86dd8e3a4708a020f6e6ed9e97d3c09d04fbbd364a2acdd15e4b8ab163db08d9`.
Seventeen strict calls bind the seven maintained enable services, seven
maintained disable services, bitmap query, the reviewed disable-route alias,
and the retained fixed-size memcpy provider. Five focused tests pin all bodies
and the successor, exercise complete routing and bounds, selective cleanup,
copy/null behavior, and compile both reviewed profiles.

Canonical accounting becomes 19,291 source-owned, 16,528 generated patch, 16
alignment, and 128,005 retained official bytes, including 362 cave bytes and
3,704 exact in-place bytes across 236 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,598,235-byte flash plan has SHA-256
`e1a4ef389dec567d8afe71061e5659cfba7a016e3ed2d5fbae7323b198115df4`
with 6,607 placed, two unresolved, five container-only and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but live shared-bitmap ownership, row-specific service effects,
concurrent cleanup, retained configuration ownership and persistence require
authorized hardware evidence. That evidence is unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; after the
authenticated 56-byte literal pool, the next executable body begins at
`0x00422468`.
