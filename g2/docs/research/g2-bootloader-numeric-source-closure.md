# G2 bootloader numeric, formatter, dispatch, and string source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The aggregate identities below are the substring promotion checkpoint; the
later critical-context promotion supersedes them. Current aggregate pins are
in `g2-bootloader-critical-context-source-closure.md`.

Thirteen authenticated entries at `[0x00415844,0x00416026)` are now
source-owned. They implement unsigned 64-bit division by ten, decimal and
hexadecimal digit counts, wrapping decimal parsing, decimal and hexadecimal
output, nullable string length, repeated-character output, fixed-point float
conversion, the complete IAR logging formatter core, and its variadic dispatch
wrapper and substring search.

The stock boundaries contain 1,986 bytes and have 84 direct caller edges. Apple
clang emits 1,818 Thumb bytes at `[0x004348D0,0x00434FEA)`. Twenty strict
relocations bind only calls among these already placed source leaves. The
formatter preserves the raw AAPCS argument cursor, `ll` alignment, `%c`, `%s`,
`%x/%X`, `%u`, `%d/%i`, `%f/%F`, width, zero fill, precision, `*`, nullable
output sizing, CRLF control at `0x200271C4`, float fallback strings, and the
stock null-output float behavior.

Host tests cover arithmetic boundaries and deterministic inputs, signed
extrema, parser consumption and wrap behavior, decimal/hex output, nullable
destinations and strings, padding, every supported conversion class, 32/64-bit
arguments, string precision, CRLF insertion, float success/error fallbacks,
and null-output quirks. Target gates authenticate every stock span and caller,
compile each leaf freestanding for Cortex-M55, verify every relocation and
full-span redirect, and reproduce both reviewed compiler profiles.

The canonical overlay is 2,930 bytes with SHA-256
`1f2ec82849242aad68a4237e81032792153da0b7939c88bc7d445a10f9afb5c6`.
The 151,530-byte provider hashes to
`e6cfa18432d3e51608a273b3e2e666f68629489e9417e0cc2c52902fc4256519`
and accounts for 2,923 compiled-source bytes, 3,438 generated patch bytes,
eight alignment bytes, and 145,161 retained authenticated bytes. It ends at
`0x00434FEA`, leaving 12,310 bytes before Apollo main.

The canonical unsigned package is 4,733,108 bytes with SHA-256
`591f2280c97ca68dca9be07f9310b2f8c60404c04140eecc24ff304e25ac1722`.
Its 4,334,189-byte flash plan hashes to
`9872769764f0c650ac51fe4cfef47da9ab3d0b7ce3dfe2ba28555ab89a1d2e7d`
and contains 6,243 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,110 bytes with
SHA-256
`ad67d411dc72f77a5ead5178e89b75f6cd934d77d55f6e4db721fd38abcdf738`;
its 2,306,724-byte flash plan hashes to
`e1da97398986ac4682589bc884724c0da240f594b120205bf869d82f558476c9`
and contains 3,317 placed regions with the same unresolved and protected
boundaries.

This closes only the bounded numeric/formatter/dispatch/string cluster. The
literal pool at `[0x00415FDA,0x00415FFA)` remains authenticated data; the
stubs from `0x00416026` and later runtime/platform-service executable bodies
remain software gaps. Physical
boot and caller-path evidence is explicitly blocked
because no authorized responsive G2 right temple is available; the left
temple remains stock. Nothing was signed, transmitted, or flashed.
