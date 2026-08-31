# G2 bootloader TLSF public-API source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The seven complete authenticated entries at `[0x0041711C,0x004172DA)` now
route to compilable freestanding C in
`components/bootloader/core_overlay/runtime_tlsf_public_41711c.c`. The
14,942-byte source hashes to
`2bbe538edad18945e173a4bd2fe620eee4e93a98c7583cf8fdd4b8731c8c385b`
and is a bounded BSD-3-Clause adaptation of Matthew Conte TLSF v3.1.

| Entry | Stock bytes | Apple text bytes |
| --- | ---: | ---: |
| control construction | 48 | 48 |
| pool overhead | 16 | 4 |
| add pool | 172 | 140 |
| create | 56 | 40 |
| create with pool | 42 | 28 |
| malloc | 38 | 36 |
| free | 74 | 80 |

The 446 stock bytes become 376 Thumb bytes under seven strict relocations.
Host tests cover zeroed control construction, pool bounds/alignment and
sentinel setup, creation failure/success, malloc exhaustion, user/block
pointer conversion, null-free, coalescing, and free-list reinsertion. The
freestanding Cortex-M55 gate pins the recovered ILP32 control and block ABI.

Canonical Apple output is a 6,944-byte overlay
(`bb89cb1587eff14c620b34a511f47fcdaa7b5a9d030c39fe701a0014e2dc60bc`)
and 155,544-byte provider
(`7da4698d31de6079b92a6020bf7cbb6fdce98dcc2b4dcbab1e0ac9c0ebbc8ac8`).
The unsigned Apple package is 4,737,122 bytes (`099dbe07…694b`) with 6,391
placed and two unresolved regions. Linux emits a 6,924-byte overlay and
155,524-byte provider; its unsigned package has 3,391 placed and the same two
unresolved regions.

No image was signed, flashed, installed, reset, or booted. Live heap,
fragmentation, allocation-caller, and boot validation is explicitly blocked
because no authorized responsive G2 right temple is available. The next 98
bytes are authenticated transition data; EasyLogger executable source closure
resumes at `0x0041733C`. Firmware-wide functional completeness is not claimed.
