# G2 bootloader reflected CRC-32 source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The authenticated 56-byte entry at `[0x004157C0,0x004157F8)` performs a
three-argument incremental reflected CRC-32 update. Six whole-image direct
callers are pinned. Its literal at `0x004157F4` names the 16-word nibble table
at `0x0043174C`; table word eight is the standard reflected polynomial
`0xEDB88320`.

`runtime_crc32.c` implements the same update state with the equivalent
eight-bit recurrence and no implicit initial or final complement. Host tests
cross-check standard, all-byte, embedded-NUL, empty, and split-update inputs.
Apple clang 21 emits a relocation-free 44-byte leaf at `0x00434898`; a
two-byte generated alignment region precedes it. The complete stock entry is
replaced by one reviewed non-linking `B.W` and 26 NOPs.

The canonical 1,100-byte overlay hashes to
`fe3f120eb2c0e7ea169ef72306ed5d62485958bb6b9f02bccd642699fab92075`.
The 149,700-byte provider hashes to
`97734c7e1e268044b7be67cfe3f2bb24cb8fb19acfb4931bd27e4b22e2ad3eb4`
and accounts for 1,093 compiled-source bytes, 1,444 generated redirect bytes,
eight alignment bytes, and 147,155 retained authenticated bytes. The Linux
provider hashes to
`ae61d21c9583b1b135c9b1778e34f25ac292129f802aec701e3de0c14712237b`.

The unsigned canonical package is 4,731,278 bytes with SHA-256
`de341e896984741b7cf4ad18c5e3beba7f31c960ff11d897f81d350b69ef383e`;
its 4,314,298-byte flash plan hashes to
`c0433498eae744041e030cadad31af19d422472a70ba50a2c137f5bf530cbb56`
and contains 6,214 placed, two unresolved, five container-only, and six
protected regions. The Linux package is 4,507,288 bytes with SHA-256
`3d62b8b6aae4a1c2c499b4f68092bdd38d06caa05155857afe46f60d6067afb4`.
No package was signed, transmitted, or flashed.

Software closure is complete for this updater. Live CRC and boot-progression
evidence remains explicitly blocked because no authorized responsive G2 right
temple is available; the left temple remains on stock firmware.
