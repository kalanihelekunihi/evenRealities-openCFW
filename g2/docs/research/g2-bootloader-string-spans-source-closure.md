# G2 bootloader string-span source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The authenticated G2 2.2.6.10 bootloader contains adjacent `strcspn`- and
`strspn`-equivalent entries at `0x004157F8` and `0x0041581A`. Each stock span
is 34 bytes and has three whole-image direct callers. Clean-room freestanding C
implementations now replace both complete entries through reviewed `B.W` plus
NOP-fill redirects. The compiled leaves are relocation-free: 30 bytes at
`0x0043485C` for the reject-set span and 28 bytes at `0x0043487A` for the
accept-set span.

The canonical 1,054-byte overlay hashes to
`9ed00456644a69c561f5ae214450468b1048ddf0e96ff46eac28c60e1d4d39cc`.
Its 149,654-byte bootloader provider hashes to
`8427e3371f54dc25c846a103e77c5db16d5d6a8ddbcfdf04f63c3fc36b4ed83a`
and accounts for 1,049 compiled-source bytes, 1,388 generated redirect bytes,
six alignment bytes, and 147,211 retained authenticated bytes. The reviewed
Linux-clang provider hashes to
`739876489bb677e03bc06733442b4dfc73e3337bbc0a3bf64d11f4ad4f2a9694`.

The unsigned canonical package is 4,731,232 bytes with SHA-256
`67ee19e8ffd3710a40b2463feb96c46f1af8fe9ca95c15644678309f5f9ed8e2`;
its 4,313,007-byte flash plan hashes to
`2613d76330150ef0788ac562fe4a53a34063a11b6d13dde9ea5d7fd0a2c7ea55`
and contains 6,212 placed, two unresolved, five container-only, and six
protected regions. The Linux package is 4,507,242 bytes with SHA-256
`cb7a44df6ffed2654bf4e825eae4a31cd4e6596f4644940a13ba04a1c265a455`
and has 3,302 placed regions. No package was signed, transmitted, or flashed.

Software closure is complete for these two primitives. Live boot progression
through all six callers remains explicitly blocked because no authorized,
responsive G2 right temple with boot UART/debugger evidence is available. The
left temple remains on stock firmware.
