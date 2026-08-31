# G2 bootloader pin-group dispatcher source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete bootloader entry at `[0x0041FADC,0x0041FCF6)` is now replaced
by maintained clean-room C. The 538-byte stock body hashes to
`5fa7352e1bdc3dffcdda275c9fe7102d92c41fbc2a6384e407f6a68e920a35ce`;
authenticated aligned Thumb scans identify exactly two callers at
`0x004203B8` and `0x00420E84`.

`runtime_pin_groups_41fadc.c` is 4,772 bytes, SHA-256
`2608a97a8a2fc3e8e63e3eeae78dbec81646e4d650b407bbcb9ebae86e9fff86`,
under MIT. It preserves the complete two-bank dispatch policy:
the low byte of subtype selects cumulative nine/pair/quad/common pin groups;
each ordered pin call reads its authenticated word at `0x20000000+offset`
and forwards it to pin-configure seam `0x0041D92D`; odd, unsupported, and
banks two/three/other values are no-ops. Host tests pin the maximum 19-call
bank-zero path, 11-call bank-one path, subtype truncation, ordered pin/config
pairs, and no-op cases. A warning-clean freestanding Cortex-M55 compile gate
passes.

Apple Clang 21 and Linux Clang 22.1.8 emit the same relocation-free 428-byte
leaf, SHA-256
`e792fc1fbd6ae3a13b8e2edd4f37a3498752bb07f8293f761c331b1fbe017ea7`,
at offsets 9,488 / 9,472. Apple overlay/provider identities are 9,916 /
158,516 bytes with SHA-256
`f00be08414c7e4731ed8e2e61ed1f8041f105c520d941c0b26d16ba4f4e8143a`
and `5ec3947c373c9d765d8c3385c0f7d436f8c4599ddae90429bc48263f1f80783a`;
Linux identities are 9,900 / 158,500 bytes with SHA-256
`1b531362e7f7ce06225ecdc068dcc0b124eeb5c84a1570f7f071e11497acdd93`
and `06e369900458478ec088319400809d6bfb7883c3ddeb0808e3fff0f8bb52e4f5`.
Canonical accounting is 9,903 source-owned, 11,310 generated patch, 14
alignment, and 137,289 retained official bytes across 158 functions, 139
relocated leaves, and 156 patch sites. Apple headroom is 5,324 bytes.

The unsigned Apple/Linux packages are 4,740,094 / 4,516,088 bytes with
SHA-256 `f76455fc72574e0c8357b14b7f0c422931ae65896eb642e61787d0df40cb8c7f`
and `72935d6882098e5d65e30bdf6630214c5fb428bff20dbabca7e4988ba2aefc37`.
Their flash plans are 4,496,054 / 2,394,814 bytes with SHA-256
`944cc1d9b7bee4bd5fe76f79c81cd2d00eea0aec0e49990c8701b193c62b1eb7`
and `be170da7e2c4aaea360f296ac5b2622f334bdf2629ce0665568e73cb3278dc8c`,
containing 6,464 / 3,432 placed regions, two unresolved, five container-only,
and six protected regions.

No hardware operation occurred. Live pinmux/GPIO/electrical behavior and
caller-path/cold-boot validation remain blocked because no authorized
responsive right G2 temple exists and the left temple must remain stock.
Later retained bootloader bodies remain software gaps; firmware-wide
completeness is not claimed.
