# G2 bootloader guarded-teardown source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete bootloader entry at `[0x0041FA98,0x0041FAD0)` is now replaced
by maintained clean-room C. It is a first-party G2 compatibility service; no
upstream identity is claimed.

## Authenticated stock and ingress bounds

The 56-byte stock body hashes to
`b3aa72e7385221b11e6f78cdc5c1926a08094d400a58924d75154deeaf2c0553`.
The whole-image aligned Thumb `BL` scan finds exactly one direct caller at
`0x0041FA54`. The following 12-byte literal pool at
`[0x0041FAD0,0x0041FADC)` contains `0x20027198`, `0x00433A9C`, and
`0x00434154`; it remains authenticated official non-executable data.

## Recovered contract

`runtime_guarded_teardown_41fa98.c` is 4,521 bytes, SHA-256
`ad8f5eba68fce82f9e3d7807f2aed0ef207e76fff8840e7497429f9c06e960e9`,
under MIT. It preserves the complete observable behavior:

- return without side effects unless guard byte `0x20027198` equals exactly
  one;
- call stage-one status seam `0x00423D21`, and fail-stop forever if it returns
  nonzero;
- call stage-two status seam `0x00423DD1`, with the same nonzero fail-stop
  policy;
- clear the source-owned state word through seam `0x0041583D`;
- configure pin `0x1C` through seam `0x0041D92D` using the word stored at
  `0x00434154`; and
- clear the guard byte only after both stages and pin reconciliation complete.

The host adapter turns each otherwise terminal fail-stop into an observable
test return. Tests cover inactive guard values zero and two, both independent
failure stages, the complete success sequence, arguments, and state effects.
A freestanding Cortex-M55 compile gate rejects warnings and language-runtime
dependencies.

## Dual-profile production evidence

Apple Clang 21 and exact-root Linux Clang 22.1.8 emit the same relocation-free
72-byte leaf, SHA-256
`075c10d5ae973c25ffaf80a383199f8aed52f9e53abcd817f480b52357fb2f83`,
at overlay offsets 9,320 and 9,304. Apple produces a 9,392-byte overlay ending
at `0x00436928`, SHA-256
`2764ebb28ccde7977522ee318869a03805dfa2e0bc718c16de51c2ce4579828f`,
and a 157,992-byte provider, SHA-256
`0fa99abd573ab6a8845c3807cef69d29ee29d46606f1044bae6b571971dff659`.
Linux produces 9,376 / 157,976 bytes with SHA-256
`66bb62b17d33dbdec3f1015299fee2f04cb435a15d8a335b98c64eb6d000dac6`
and `bddf904854256b0403d5750d756ca2b98d379434362918a94f876fa7c69e3427`.
Canonical accounting is 9,379 source-owned, 10,700 generated patch, 14
alignment, and 137,899 retained official bytes across 156 functions, 137
relocated leaves, and 154 patch sites. Apple retains 5,848 bytes of overlay
headroom.

The unsigned Apple package is 4,739,570 bytes, SHA-256
`f69e3c8e9d8fc2408a48eeff99e6d96cbbf55f77e052881a3260223bf2c7b779`.
Its 4,492,437-byte flash plan hashes to
`f3898b0c42dff965bc9e375595140d754df9546be23c13ed37cb137d3112692f`
and records 6,459 placed, two unresolved, five container-only, and six
protected regions. The Linux package is 4,515,564 bytes, SHA-256
`f92667c2f10b51cbd49129924bd4bf10c77145dccdc460e18840d4ebeadf8a72`;
its 2,392,572-byte plan hashes to
`5711b7ba6fbf512f9b3acd8e5fa76224f4014e2a0336727de1cd04105afb0d7a`
and records 3,429 placed regions with the same unresolved/container/protected
boundaries.

No signer, device, debugger, UART, transport, flasher, reset, or boot path was
accessed. Live teardown status, fail-stop behavior, pin reconfiguration, power
state, and caller-path evidence remain blocked: there is no authorized
responsive right G2 temple, and the authorized left temple must remain stock.
Later retained executable bootloader bodies remain software gaps, so
firmware-wide functional completeness is not claimed.
