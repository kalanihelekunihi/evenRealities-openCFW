# G2 bootloader BL-006 tail leaves 0x00424AB2/0x00424B88/0x004250E6/0x00427C72 source closure

156 of the retained `official_blob` bytes -- four single-exit,
call-free, literal-free stock tails that survive as unreachable
bytes after entry-redirect-replaced heads -- are now produced from
reviewed MIT C through the component's `in_place_leaves`
mechanism. All four payloads compile relocation-free under the
reviewed Apple-clang Cortex-M55 leaf flags and reproduce the
authenticated stock bytes exactly, so `expected.sha256` equals
`stock.sha256` for every leaf.

| Tail | Bytes | Leaf symbol |
| --- | --- | --- |
| `0x00424AB2..0x00424AEA` | 56 | `open_cfw_bootloader_mspi_state_init_tail_424ab2` |
| `0x00424B88..0x00424BD4` | 76 | `open_cfw_bootloader_mspi_config_pre_tail_424b88` |
| `0x004250E6..0x004250F0` | 10 | `open_cfw_bootloader_mspi_enable_tail_4250e6` |
| `0x00427C72..0x00427C80` | 14 | `open_cfw_bootloader_cmdq_reset_tail_427c72` |

Sources (both new):
`components/bootloader/core_overlay/runtime_bl006_mspi_state_tails_424ab2.c`
(tails A and B) and
`components/bootloader/core_overlay/runtime_bl006_epilogue_tails_4250e6.c`
(tails C and D). Each source carries the naked-assembly target
body (explicit instruction widths, so the integrated assembler
reproduces the stock encodings bit-for-bit) plus a portable C
twin compiled for the host behavior tests. The verifier is
`g2/tests/test_runtime_bootloader_bl006_tail_leaves.py` (stock-SHA
authentication, byte-exact rebuilds, relocation-free checks,
overlay registration checks, survey-verdict pins, a whole-image
`bl`-caller sweep, and ctypes host-behavior cases against an
independent Python oracle).

## Why leaves, not data

The prior BL-006 pools were literal/alignment islands admitted as
named-field `in_place_data`. These four spans are the opposite:
executable tails with no literal loads at all, so there is no
pool to name -- only behavior to reconstruct. The
`in_place_leaves` route (293 leaves already admitted, including
the BL-006 range-error/div-zero tails) is the established
mechanism for exact in-place behavior reproduction, and the
range-error tail is the direct precedent for admitting a dead
tail: unreachable, understood, byte-exact, behavior-tested.

## Tail semantics (from anchored Capstone decode)

- A `0x00424AB2` (MSPI per-instance state-initializer tail; entry
  registers set by the replaced initialize head: r0 = stride,
  r1 = out slot, r3 = index, r4 = state base, r5 = scratch):
  `p = base + index*stride`; `p->u8[0x0C] = 0`;
  `p->u32[0x18] = 0`; `p->u8[0x8C9] = 7`;
  `p->u32[0x8CC] = 8`; `*out = p`; return 0. Each store
  recomputes `p` from `(base, index, stride)`; the out-slot store
  recomputes it once more. The already-admitted 6 bytes at
  `0x00424AEA` (pad plus the `0x2001CAA0` state-base word) follow
  immediately, consistent with the initialize/configure area.
- B `0x00424B88` (public device-configuration pre-step tail;
  r0 = value, r1 = config source, r2 = destination, r3 = key,
  r5 = state base): `k = key + 0x42A`; `[dst+0x858] = value`;
  `q = [base+k*key+0x858]`, clamped to `0x100` when `>= 0x101`;
  `[base+k*key+9] = cfg[8]`; `[base+k*key+8] = 1`;
  `[base+k*key+0xA] = 0x1A`; return 0. One internal forward
  branch (`blo` over the clamp store); no calls.
- C `0x004250E6` (MSPI enable epilogue; r0 = control word,
  r4 = head-owned device-word slot): `r0 |= 0x2000000`;
  `*slot = r0`; return 0. Ten bytes, no stack traffic of its
  own. The host twin takes the slot explicitly since r4 is not
  an incoming argument; the divergence is documented in source.
- D `0x00427C72` (command-queue reset epilogue; r0 = status,
  r2 = queue state): `v = r0 & 0xFF`; `t = *(r2+0x24)`;
  `t = *(t+0x0C)`; `*t = v`; return 0. Its `bx lr` lands exactly
  on the already-admitted suffix pool at `0x00427C80`.

## Deadness evidence

All four spans sit in regions the whole-image retained survey
(`g2/tools/analyze_g2_bootloader_bl006_retained_survey.py`)
grades `corroborated_unreachable_control_flow`, pinned by the
verifier importing the survey. A whole-image Capstone `bl` sweep
finds no caller of any of the four entries (linear-sweep
desynchronization inside data is noted in the test; the sweep
corroborates the survey verdict rather than standing alone).
No entry appears as an image pointer word outside its own span
(the span-427e54 survey established the method; these tails
additionally take no address constants at all). No live traffic
is claimed: the reconstructions document dead bytes from
reviewed source and pin the behavior the replaced heads must
cover.

## Host behavior verification

The same sources compile for host (`cc -std=c11 -shared
-fPIC`; the `__arm__`/`__thumb__` target branches are excluded)
and the verifier drives all four twins through ctypes against
an independent Python oracle: tail A over four stride/index
combinations with a stray-write check over the whole 16 KiB
model; tail B over below/at/above-clamp field values with
exact publish/clamp/copy assertions; tail C over five merge
values including `0xFFFFFFFF`; tail D over four narrow values
through a host pointer chain. The host pointer slots are
natively wide (8-byte) versus 4-byte on target; identical
shape, documented in the test.

## License and toolchain

Both sources are MIT (new openCFW code, no vendor text). The
overlay pins the reviewed Apple-clang Cortex-M55 leaf flags
(`-Oz -fno-jump-tables -fomit-frame-pointer -fno-builtin
-mno-unaligned-access -fropi`, `strict_relocation_contract`,
zero relocations) plus the standard linux-clang profile
expectation; the bodies are assembler-transcribed (no compiler
codegen involved), so the cross-toolchain expectation is a
falsifiable pin the Linux gate will check. No hardware
operation occurred. Hardware qualification stays blocked by
unavailable physical evidence.

## What remains (BL-006)

This pass brings BL-006 to 1,502 of 5,892 bytes from reviewed
source (1,346 prior plus 156 here). Still retained: the large
unreachable MSPI tails (`0x0042423C..0x0042488E`,
`0x004248E2..0x00424976`, `0x00424E84..0x00425066`,
`0x0042612C..0x004262E0`), the command-queue remainders
(`0x0042784C..0x00427C12`, 190 B), the blocking-transfer tail
with live calls (`0x004263E0..0x00426450`), the interrupt
enable/disable/status tails, the CLKGEN/memset terminal
returns, the `0x00425160` disable-tail literal, the syspll/queue
gap (`0x00427588..0x004275EA` remainder), the binary32
remainder tail (`0x00427D84..0x00427D98`, tail-branches into
`0x004275C4`), and the 1,316-byte SPOT-trim span
(`0x00427E54..0x00428378`, surveyed, needs a fill primitive or
full reconstruction). Firmware-wide completeness is not
claimed.
