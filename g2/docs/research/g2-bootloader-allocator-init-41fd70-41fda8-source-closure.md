# G2 bootloader allocator initializer source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete executable entry at `[0x0041FD70,0x0041FDA8)` is now replaced
by maintained clean-room C in
`components/bootloader/core_overlay/runtime_allocator_init_41fd70.c`.
The 56 authenticated stock bytes have SHA-256
`e92241da4e692fb1acee34d31103f2aaf6439d88fd192b9ac0abf5f6785f2f2d`
and one direct caller at `0x0041B89E`. The preceding 122-byte non-executable
pool `[0x0041FCF6,0x0041FD70)` remains authenticated and separately classified
(SHA-256 `a336f9a95b7426fb8c078b298098471dcf02e7e7fd66730d0dcdc2d3427db2ec`).

Recovered behavior is bounded and deterministic: clear the 0x70800-byte pool
at `0x20081000`, create the TLSF control/pool object through the retained entry
at `0x00417241`, publish its handle to `0x2002718C`, emit the recovered
level-four diagnostic record through `0x004176CF`, and return zero. The
following literal pool authenticates the pool, handle, tag, format, argument,
line 0x13, and file pointers used by this reconstruction.

Host tests verify call order, all arguments, pool clearing, handle publication,
the diagnostic record, and the zero return. Cortex-M55 compilation is clean in
both reviewed profiles. Apple clang emits 88 relocation-free bytes with
SHA-256 `1a588b40d59408de4b8f541890868a18a827a77c7333c958687ebeae21f30ddc`;
Linux clang emits 88 bytes with SHA-256
`98ad36432a4e12f52535ab869d025cbbf03f57d63bdba9553541169b73a9e190`.

The Apple overlay/provider are 10,004 / 158,604 bytes with SHA-256
`a27f7ba39fdfe6a7364d59577cfa387a0a601aedf773612d1cb1b77700c6538d`
and `da312bd3b1a4105f75788107d147d5397edba0014c72d11584d5c9552c24cab7`.
The Linux overlay/provider are 9,988 / 158,588 bytes with SHA-256
`15784fef039b93caaa26b202c61b115b4d0947f0ec253b7232dd43e828787b50`
and `a64974dce84415f4031847e1f71b5397cd0c366a31b8786d6f6e311ff53bd7b2`.
Canonical accounting is 9,991 source-owned bytes, 11,366 generated patch-site
bytes, 14 alignment bytes, and 137,233 retained official bytes across 159
functions, 140 relocated leaves, and 157 patch sites.

Unsigned Apple/Linux packages are 4,740,182 / 4,516,176 bytes with SHA-256
`8041ac27ae80d9cb331d27363281d7dfb259024a4276e80783bcca4b3e7a04a2`
and `7591a1ab14efac218d2610f2192f1b554c1f366ceb917ba911fc9059c8965bd6`.
Their flash plans contain 6,467 / 3,434 placed regions and two unresolved
boundaries each. No image was signed, flashed, installed, reset, booted, or
sent to hardware.

Live MRAM/SRAM initialization, TLSF operation under target timing, logging,
and cold-boot behavior remain hardware-blocked: no authorized responsive right
G2 temple is available, and the left temple must remain stock. Executable
bodies after `0x0041FDA8` remain software gaps, so firmware-wide functional
completeness is not claimed.
