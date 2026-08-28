# G2 FreeType non-local-jump ABI evidence

The provider is an MIT-licensed clean-room implementation derived from bounded
behavioral evidence in the official G2 2.2.6.10 Apollo-main image. No IAR
source or library object is copied. The exact IAR release remains unknown and
no attributable open-source IAR implementation was found locally or in IAR's
public source repositories.

## Authenticated leaves

The official image is 3,523,396 bytes with SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Runtime addresses map to file offsets by subtracting `0x00437FE0`.

- `0x0056777C..0x0056778E` is the 18-byte save leaf, SHA-256
  `205f3a06127e5125d848bcbcf69d4faddb5504e5477e5b28d49e0ea601df66bd`.
  It saves `r4-r11`, the entry `sp`, `lr`, and `d8-d15`, in that order, then
  returns zero.
- `0x00567790..0x005677A8` is the 24-byte restore leaf, SHA-256
  `720424552af7541d51b4eb65dbdfd5a7f65c4f6f1c4d871d2f27e5e02559c0bb`.
  It changes a requested return value of zero to one, restores precisely the
  same register set, moves the saved value back to `sp`, and returns through
  the saved `lr` with the requested/nonzero-normalized value in `r0`.

The write footprint is 104 bytes:

| Offset | Bytes | State |
|---:|---:|---|
| `0x00` | 32 | `r4-r11` |
| `0x20` | 4 | entry `sp` |
| `0x24` | 4 | `lr` |
| `0x28` | 64 | `d8-d15` |
| `0x68` | 24 | reserved, not read or written by either leaf |

## Independent buffer-size and ownership evidence

The stock `ft_validator_init` leaf at `0x00524F70..0x00524F84` has SHA-256
`ceff9037d72ed544f9a460ff557f1707f89d13009ca63a0731a1187dd8064d1a`.
It writes the fields following `FT_ValidatorRec.jump_buffer` at offsets
`0x80`, `0x84`, `0x88`, and `0x8C`. The authenticated FreeType 2.9.1 structure
places those fields immediately after `jmp_buf`, independently proving a
128-byte buffer. The core cmap caller passes an eight-byte-aligned stack
address; the smooth raster record also places its first post-buffer field at
`0x80`. OpenCFW consequently requires eight-byte alignment for the saved VFP
block. This is a provider requirement; exact IAR type spelling is not claimed.

The complete direct ingress topology in the official image is:

- save: `BL` at `0x005DED32` (SFNT cmap validation) and `0x005E1F14`
  (smooth raster conversion);
- restore: `BL` at `0x00524F90` (validator error) and `0x005E15D6`
  (smooth raster cell overflow).

These roles match the authenticated FreeType 2.9.1 source. The restore sites
both pass one, while the zero-to-one normalization remains implemented because
it is part of the observed leaf and the C `longjmp` contract.

## Scope and residual qualification

This closes the software link ABI for the selected Cortex-M55 hard-float
FreeType graph. It does not claim byte identity with a specific proprietary IAR
archive. Production admission still requires stack/WCET review, scheduler
policy confirming jumps never cross task or exception boundaries, and final
toolchain/link placement. No hardware behavior is involved.
