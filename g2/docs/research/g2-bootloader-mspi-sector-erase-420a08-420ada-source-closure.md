# G2 bootloader MX25U25643G sector-erase source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated sector-erase function `[0x00420A08,0x00420ADA)`
is now routed to compilable clean-room C. The 210-byte stock body has SHA-256
`0a0a96db9e3a1c6fcbdfcebd96db6f16e22c780940889677a16ebc880d0dd899`.
Its sole direct caller is the Thumb `BL` at `0x00421354`. The immediately
preceding 12-byte pool `[0x004209FC,0x00420A08)` remains authenticated
non-executable compatibility data with SHA-256
`24e3dd42d22fb00fcda8010047ae549a2110c8e5c77f230fb43a071466a26aa4`.

The maintained implementation rejects an unavailable device handle with
status 2, rejects non-4-KiB-aligned addresses with the exact stock EasyLogger
record and status 6, and rejects addresses at or above `0x02000000` with
status 5. Valid requests enter the source-owned MSPI guard, switch to serial
mode, wait for readiness, enable the write latch, submit command `0x20` with
the sector address and address flag 1, wait for completion, and disable the
write latch. Every guarded exit restores quad mode and releases the guard.
The pre-wait and post-wait failures map to statuses 3 and 4; command-stage
failures preserve their raw status. All five failure diagnostics retain the
authenticated format and argument policy.

Host tests pin all validation short circuits, the exact call order and cleanup
on every failure stage, the transfer tuple `(0x20, address, 1, NULL, 0)`, raw
status propagation, successful completion, pool/caller identities, and a
Cortex-M55 freestanding cross-compile. Apple Clang 21.0.0 emits a
relocation-free 244-byte leaf at `0x004377E4`, SHA-256
`673dea5391605a49b503acf81a1c3ab626fc70bbdfd92ad2b156902516fbb060`.
Linux Clang 22.1.8 emits a relocation-free 244-byte leaf at `0x004377D4`,
SHA-256
`f60676504f6e7c89f406cab8313a7355bfdb885f28aba88b4ef6b2d8046e32e2`.

Canonical and Linux overlay identities are 13,408 / 13,392 bytes with
SHA-256
`936b166f4eec07cbb3fe5d988e80593354892caf7a875c7f972ffdb24bbfc4f3`
and `fc0b9409eab2105fdfa6e22fad8f90660aff9f061452c8b5064e9f07333f9303`.
Provider identities are 162,008 / 161,992 bytes with SHA-256
`873e843b1b2dcb5c96cdaf7e42f8705563ed5a1ca436811e0c3081415d3a9a1e`
and `6510e26f2f627c2424dae20b13f856ef6ea3dcdf04223339f859364d259f1958`.
Canonical accounting is 13,393 source-owned, 14,654 generated patch, 16
alignment, and 133,945 retained official bytes across 188 functions, 169
relocated leaves, and 186 patch sites. The unsigned canonical package is
4,743,586 bytes with SHA-256
`9451c86c90a52643fa43cea465f2a82419a5d345b82f4b44e41ef02a5de39da0`;
its 4,543,948-byte flash plan hashes to
`19cf8b9cd9e701833431ee8addf6079702949129d5547bff37005025772a2b2d`
and contains 6,531 placed regions plus two unresolved physical boundaries.

No signing, flashing, installation, reset, boot, command submission, or other
hardware operation was performed. Live erase, write-latch, MSPI,
external-flash, XIP, error-path, and cold-boot validation is explicitly
blocked by the absence of an authorized responsive right-temple G2; the left
temple must remain stock. The 50-byte retained pool/gap after this function
precedes the program service at `0x00420B0C`, which was subsequently
source-closed. The next executable frontier begins at `0x00420C5C`. This
remains a historical increment, not a firmware-wide functional-completeness
claim.
