# G2 bootloader per-instance hardware-initializer source closure

The authenticated body at `[0x0042308E,0x004232C8)` now compiles from a
maintained MIT C translation unit under both reviewed Cortex-M55 profiles. The
570-byte installed body has SHA-256
`80102228cb6a9eb99cd5bf229d5ca450331b2521a39e23e4e0671f7f928dbc46`;
its unrelocated image has SHA-256
`f08bff0cbc423ffc9408db313992c97fb4f181dadf7479f12820f8257e9a7826`.
Only the two strict `R_ARM_THM_CALL` relocations at offsets `0xE4` and `0x11A`
differ before placement. They bind the already source-owned mode-route service
at `0x004222F0` and clock-divider service at `0x00422E28`.

The service rejects a null or mismatched instance with status 2 and rejects an
unsupported configuration mode with status 6. It selects one of four
`0x40039000` register banks from instance word `0x28`, applies the authenticated
`0x0016E361` rate threshold and chip-revision gates, updates the global route
bit at `0x400201B0`, and supplies `(instance_mode, index + 11)` to the mode
route. Divider failures are returned unchanged before post-divider register
programming. Success programs the recovered fields at bank offsets `0x2C`,
`0x30`, and `0x34`, stores the actual divider result at instance offset `0x30`,
and enables bits 0, 8, and 9.

Nine focused tests pin the body, literals, source providers and relocation
locations; validate null/magic/mode/revision failure paths; cover both rate
branches, four register banks, global-route set/clear behavior, provider
arguments and divider failure propagation; verify all recovered configuration
bitfields; and cross-compile with both reviewed target compilers. The target
translation unit matches every authenticated byte after applying its two
declared call relocations. The host path is a pure C behavioral model with
injected register and provider state.

The canonical 163,840-byte bootloader provider remains byte-identical with
SHA-256 `8f24989979719b4c9f1273624240ba702a99decf735d099bfee1afcda16159e0`.
Accounting is now 28,495 source-owned, 16,474 generated patch-site, 16 generated
alignment, and 118,855 retained official bytes, including 12,802 exact in-place
and 468 cave bytes. The core-source manifest classifies this body as
`source_compiled` at its authenticated address.

No hardware operation occurred. Live chip revision, MMIO masks, clock-tree and
peripheral state, interrupt/concurrency behavior, provider side effects, and
cold-boot qualification are blocked by unavailable physical evidence.
Firmware-wide functional completeness and release readiness are not claimed.
