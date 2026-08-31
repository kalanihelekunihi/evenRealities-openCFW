# G2 FreeType CFF package-builder integration

## Result

The admitted FreeType 2.9.1 CFF closure now has a target-specific post-link
component stage.  The canonical Apollo core builder invokes that stage after
the liblc3 and product-test providers, using the pre-CFF component produced by
the same build.  Both reviewed compiler profiles build successfully and end at
`0x007FDED4`, below the `0x007FE000` update flag.

The package format does not block the scatter layout.  The two physical CFF
ranges are represented inside one contiguous entry-6 payload.  The unused
address span before the tail section is emitted as generated erased `0xFF`
padding, so section writes, the guarded module-class pointer update, nested
Apollo size/CRC, EVENOTA entry length/CRC, and the complete entry-6 payload are
one package-entry transaction.  No cross-entry mutation is required.

## Exact profile receipts

| profile | CFF source bytes | erased gap | component growth | component SHA-256 | package size | package SHA-256 | entry-6 CRC-32C/MSB |
|---|---:|---:|---:|---|---:|---|---|
| Apple clang | 20,416 | 66,684 | 70,800 | `aa3dbf59ad8912a92fcd9ea6e1ce33834da51989f5fb19257e7064871fb6a3b2` | 4,749,540 | `482756200d1b3c70685d7c1c29c422a5725436801e3600d7cf55fa3e16809128` | `0x0012B7B8` |
| Linux clang | 20,356 | 274,352 | 278,468 | `3255f998ea3c115803bf957e63b50e0b4a969cf478e64939610592c6fd4758f7` | 4,749,524 | `d9386d30c0c6b1bd706b36c9ee095ad6e2e9ee9b5dacf9c58a52357c7620a362` | `0xD90D86A3` |

The profile-specific base ends are `0x007ECA44` and `0x007B9F10`.  This is why
the canonical growth differs from the earlier research package’s obsolete
`+4,122` estimate even though the final linked sections and destinations are
unchanged.

The four finalized ranges remain:

- rodata/tables at `0x005ABEF8..0x005AD22E` (4,918 bytes);
- Apple text at `0x005AD230..0x005AFEA6` (11,382 bytes), or Linux text at
  `0x005AD230..0x005AFE6A` (11,322 bytes);
- tail text at `0x007FCEC0..0x007FDEC4` (4,100 bytes);
- exception index at `0x007FDEC4..0x007FDED4` (16 bytes).

The guarded route at `0x0073EF00` compares the authenticated stock bytes
`74cb6d00` before writing `14c05a00`.  The entire stock CFF interval is checked
against SHA-256
`58b8b5e4c1b801d7ac4c6883dc8afeccd7cf370e3e9cccdf95f938e20b91358b`
before any mutation.  The separately classified 360-byte old callback/table
pool remains unused.

## Ownership and fail-closed behavior

Each profile’s derived package plan has six CFF-owned rows: four compiled
sections, one four-byte generated pointer replacement, and one generated erased
gap.  The derived plans have zero unresolved rows, zero collisions, zero
protected-range overlaps, and a highest CFF byte at `0x007FDED4`.

Hostile tests repair both the nested Apollo CRC and the outer EVENOTA CRC after
altering stock bytes.  The build still rejects the modified stock CFF interval
and class pointer, demonstrating that those guards are independent of container
integrity.  Tests also reject dependency-pin drift and a base-end collision,
and read back every emitted section and every erased-gap byte.

## Published software route and remaining evidence boundary

The canonical component and package routes are enabled.  The checked release
manifest pins the exact dual-profile component and package identities above,
including the Apple region partition and Linux profile replacements.  The
package-integration verifier independently starts from each authenticated
pre-CFF package, reruns the isolated CFF builder, validates the resulting
component against the selected provider pins, reassembles the complete package,
and requires byte identity with the selected published package pins.  This
closes the prior software-publication boundary without treating the mutable
canonical build directory as evidence.

Schema-v3 canonical observations independently persist the pre-CFF
`pt-component.bin` and all four finalized CFF section artifacts.  Admission
replays those sections into the authenticated pre-CFF component, performs the
class-pointer compare/write, fills the profile-specific gap with `0xFF`, and
recomputes the Apollo header length and nested CRC to the exact final bytes.
The admission loader continues to accept legacy schema-v2 observations that do
not contain this CFF stage.  Two independent Apple observations and two
independent Linux observations passed that replay before the component,
package, and region pins were admitted together.

This is a software-only result.  It does not authenticate an external CFF font
payload, qualify stack or WCET, establish rollback behavior, or validate live
G2 hardware.
