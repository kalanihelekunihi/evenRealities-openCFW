# G2 bootloader BL-006 tail leaves 0x0042647C/0x004278BC..0x00427C02 source closure

70 more of the retained `official_blob` bytes -- six single-exit,
call-free, branch-free, literal-free stock tails that survive as
unreachable bytes after entry-redirect-replaced heads -- are now
produced from reviewed MIT C through the component's
`in_place_leaves` mechanism. All six payloads compile
relocation-free under the reviewed Apple-clang Cortex-M55 leaf
flags and reproduce the authenticated stock bytes exactly, so
`expected.sha256` equals `stock.sha256` for every leaf.

| Tail | Bytes | Leaf symbol |
| --- | --- | --- |
| `0x004278BC..0x004278C8` | 12 | `open_cfw_bootloader_cmdq_enable_tail_4278bc` |
| `0x004278FC..0x0042790A` | 14 | `open_cfw_bootloader_cmdq_disable_tail_4278fc` |
| `0x00427A4C..0x00427A56` | 10 | `open_cfw_bootloader_cmdq_post_tail_427a4c` |
| `0x00427B2E..0x00427B38` | 10 | `open_cfw_bootloader_cmdq_term_tail_427b2e` |
| `0x00427C02..0x00427C12` | 16 | `open_cfw_bootloader_cmdq_reset_rem_tail_427c02` |
| `0x0042647C..0x00426484` | 8 | `open_cfw_bootloader_mspi_irq_enable_tail_42647c` |

The single new source is
`components/bootloader/core_overlay/runtime_bl006_cmdq_irq_tails_4278bc.c`.
Each leaf carries the naked-assembly target body (explicit
instruction widths, so the integrated assembler reproduces the
stock encodings bit-for-bit) plus a portable C twin compiled for
the host behavior tests. The verifier is
`g2/tests/test_runtime_bootloader_bl006_cmdq_irq_tails.py` (11
tests: stock-SHA authentication, byte-exact rebuilds,
relocation-free checks, overlay registration checks,
survey-verdict pins, a whole-image `bl`-caller sweep, and ctypes
host-behavior cases against independent inline oracles).

## Why leaves, not data

Same precedent as the 424AB2/4250E6 tail cluster: these six spans
are executable tails with no literal loads at all, so there is no
pool to name -- only behavior to reconstruct. The
`in_place_leaves` route (303 leaves now admitted) is the
established mechanism for exact in-place behavior reproduction.

## Tail semantics (from anchored Capstone decode)

- E `0x004278BC` (command-queue enable remainder; r1 = enable-word
  pointer): `r0 = *r1; r0 |= 0x2000000; *r1 = r0; return 0`.
- F `0x004278FC` (command-queue disable remainder; r0 = value,
  r1 = enable-word pointer, r2 = destination slot):
  `*r2 = r0; r0 = *r1; r0 &= ~0x2000000; *r1 = r0; return 0`.
- G `0x00427A4C` (command-queue block-post remainder; r0 = value,
  r2 = queue state): `t = *(r2+0x24); t = *(t+0x0C); *t = r0;
  return 0` (same shape as the tail-D twin, word store).
- H `0x00427B2E` (command-queue termination remainder; r1 = value,
  r4 = head-owned state slot): `t = *(r4+0x24); t = *(t+0x10);
  *t = r1; return 0` via `pop {r1, r4, r5, pc}`. The host twin
  takes the slot explicitly since r4 is not an incoming argument;
  the divergence is documented in source (same pattern as the
  MSPI enable epilogue).
- I `0x00427C02` (command-queue reset remainder; r0 = value,
  r1 = enable-word pointer, r2 = queue state):
  `t = *(r2+4); *t = r0; r0 = *r1; r0 &= ~0x2000000; *r1 = r0;
  return 0`.
- J `0x0042647C` (MSPI interrupt-enable remainder; r1 = value,
  r2 = register base): `*(r2+0x200) = r1; return 0` via a 32-bit
  `str.w` (offset too large for a 16-bit encoding).

Every span's stock SHA-256 matches the pin already recorded in
the whole-image retained survey (no survey edit needed).

## Deadness evidence

All six spans sit in regions the whole-image retained survey
(`g2/tools/analyze_g2_bootloader_bl006_retained_survey.py`)
grades `corroborated_unreachable_control_flow`, pinned by the
verifier importing the survey. A whole-image Capstone `bl` sweep
finds no caller of any of the six entries (linear-sweep
desynchronization inside data is noted in the test; the sweep
corroborates the survey verdict rather than standing alone). No
live traffic is claimed: the reconstructions document dead bytes
from reviewed source and pin the behavior the replaced heads must
cover.

## Host behavior verification

The same source compiles for host (`cc -std=c11 -shared -fPIC`;
the `__arm__`/`__thumb__` target branches are excluded) and the
verifier drives all six twins through ctypes: tail E over five
merge values including `0xFFFFFFFF`; tail F over four
publish/clear pairs with disjoint objects; tails G and H over
four publishes through host pointer chains (native 8-byte slots
versus 4-byte on target; identical shape, documented in the
test); tail I over three publish/clear triples; tail J over four
values at base + `0x200` with a stray-write check over the whole
1 KiB model.

## License and toolchain

The source is MIT (new openCFW code, no vendor text). The overlay
pins the reviewed Apple-clang Cortex-M55 leaf flags (`-Oz
-fno-jump-tables -fomit-frame-pointer -fno-builtin
-mno-unaligned-access -fropi`, `strict_relocation_contract`,
zero relocations) plus the standard linux-clang profile
expectation; the bodies are assembler-transcribed (no compiler
codegen involved), so the cross-toolchain expectation is a
falsifiable pin the Linux gate will check. No hardware operation
occurred. Hardware qualification stays blocked by unavailable
physical evidence.

## What remains (BL-006)

This pass brings BL-006 to 1,572 of 5,892 source-owned bytes
(1,502 prior plus 70 here); 58 of the 77 survey regions are fully
closed (1,484 bytes), with 88 source-owned bytes of partial
coverage inside still-open regions (chiefly the syspll/queue gap
at `0x00427588`). Still retained: 19 regions (4,408 bytes): the
large unreachable MSPI tails (`0x0042423C..0x0042488E`,
`0x004248E2..0x00424976`, `0x00424E84..0x00425066`,
`0x0042612C..0x004262E0`), the mixed code/data disable tail
(`0x00425160`), the interrupt disable/status tails
(`0x004264B0`, `0x004264F6`), the CLKGEN/memset terminal returns
(`0x00426C22`, `0x00426C70`, `0x00426CC4`), the syspll/queue gap
remainder (`0x00427588..0x004275EA`), the command-queue head
(`0x0042784C`), the branch-back alloc/error-resume remainders
(`0x0042799E`, `0x00427B90`, not self-contained: they branch into
replaced heads), the status remainder (`0x00427ABE`, same head-owned-slot
pattern as tail H plus flag-byte publishes; left for a follow-up),
the block-release remainder
(`0x004279EE`, 2 bytes), the binary32 remainder tail
(`0x00427D84..0x00427D98`, tail-branches into `0x004275C4`), and
the 1,316-byte SPOT-trim span (`0x00427E54..0x00428378`,
surveyed, needs a fill primitive or full reconstruction).
Firmware-wide completeness is not claimed.
