# GX8002 UART boot stage-1 XIP transfer leaves (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime `0x10000000..0x10002000`).
Prior passes decoded the span (`gx8002-uart-boot-stage1-cd001-analysis.md`)
and closed the arithmetic/noop leaves (`gx8002-uart-stage1-divmod-source.md`:
128 stock bytes), the reset prologue (`gx8002-uart-stage1-reset-source.md`:
48 stock bytes), four PMU trim-bit leaves
(`gx8002-uart-stage1-pmubits-source.md`: 72 stock bytes), four polled-UART
leaves (`gx8002-uart-stage1-serial-source.md`: 124 stock bytes), and the
ID-cell/clock-source leaves (`gx8002-uart-stage1-idbit-source.md`: 42 stock
bytes). This tranche closes two further leaves as production-routed
reviewed source in the experimental codec candidate: **256 stock bytes
replaced by 250 compiled bytes plus 6 generated fill bytes**.

## Envelopes

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_xip_read` | `0x100018c0` | `0x1910` | 128 | 126 | compiled_c |
| `open_cfw_gx8002_uart_stage1_xip_write` | `0x10001940` | `0x1990` | 128 | 124 | compiled_c |

Both envelopes are self-contained: no literal pools (all addresses are
synthesized with `movih`/`movi`+shift, including the compiler-reproduced
`movi 32930` / `rotli 24` idiom for `0xA2000080`), no calls, six callers
of the read leaf and two of the write leaf elsewhere in the stage-1
image (image-receive area `0x100019c0..0x10001c00`).

Behavior, in upstream terms (XIP flash controller at `GX_REG_BASE_XIP`):

- `xip_read(cmd, dst, len)`: wait idle (status bit 0 at `+0x28`), store
  the masked idle snapshot (always zero at exit — the stock `andi`s the
  status before testing it) to `+0x08`/`+0x4c`, program control `0xC07`
  at `+0x00`, count `len - 1` at `+0x04`, `1` at `+0x10`, snapshot at
  `+0x18`, snapshot at `+0xF4`, `1` at `+0x08`, command at `+0x60`;
  then per byte poll data-ready bit 3, word-read `+0x60`, byte-store to
  `*dst++`; finish by waiting for zero residual at `+0x24` and idle.
- `xip_write(cmd, src, len)`: same prologue with control `0x407`,
  count `len`, `len << 16` at `+0x18`; per byte poll transmit-ready
  bit 1, byte-load from `*src++`, word-store to `+0x60`; residual wait
  at **`+0x20`** (asymmetric with the read leaf — recovered from the
  decoded bodies, not assumed).

The countdown loop (`while (len-- != 0)`) is a size measure only: the
stock uses an end-pointer compare, but that shape outlines the loop and
costs a 2-byte back-branch the 128-byte envelopes cannot afford. Trace
equivalence (below) is unaffected.

## Provenance

Clean-room MIT C in
`components/shared/gx8002/runtime_gx8002_uart_stage1_xip.c`, against
the pinned NationalChip grus SDK `arch/soc/grus/include/base_addr.h`
(`GX_REG_BASE_XIP = 0xA2000000`, commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, blob
`536d2e51e19f12f3a7f4e354fba53be906e05702`; SDK repo-level MIT LICENSE
blob `37a1e362999f2040c2c0cda1a3231b6b5913efbf`). Only the numeric
controller base crosses the boundary; every register offset, control
word, poll bit, the masked-snapshot behavior, and the asymmetric
residual registers were recovered from the decoded stock control flow.
The SDK SPL flash drivers (`spl_spinor.c`/`spl_spi.c`, proprietary
header) target different register blocks and were deliberately not
used: no SDK text is reproduced. See
`NATIONALCHIP-UART-BOOT-STAGE1-XIP-NOTICE.txt`.

## Verification

`g2/tools/verify_gx8002_uart_stage1_xip.py` (report
`docs/research/gx8002-uart-stage1-xip-verification.json`, 1,152 cases):

- Compiles the C with `-Os -mcpu=ck804ef -mhard-float -ffreestanding
  -fno-builtin -ffunction-sections -fdata-sections -fno-tree-loop-optimize`,
  links both sections at their runtime entries into one `xip.elf` with
  no undefined symbols and no relocations; each section fits its stock
  envelope at an aligned package offset.
- The stock span is rewrapped with the CK804EF ELF flags and shifted to
  its runtime base (the `gx8002-uart-boot-stage1-cd001-analysis.md`
  recipe) so decoded addresses are absolute on both sides.
- Decoded-target execution of stock vs linked bodies with a scripted
  XIP model (status/residual/data reads scripted with hold-last;
  writes recorded; RAM arena modeled): identical exact access traces
  (kind, address, width, value of every read/write), identical final
  RAM, source preservation for the write leaf, callee-saved registers
  preserved, no traffic outside the controller block, the unlock word,
  and the transfer arena.
- Independent Python oracle on every case: prologue write order/values
  (including the always-zero masked snapshot and `len - 1` vs `len`
  counts), per-byte narrowing/widening, and the per-kind residual
  register, stated from the documented controller behavior rather than
  the decoded instructions.
- Battery: lengths {0, 1, 2, 5} x commands {0, 0x9f, 0x12345678,
  all-ones} x 3 busy scripts x 3 ready scripts x 2 residual scripts x
  2 tail scripts, with seeded data words and source bytes.
- `g2/tests/test_gx8002_uart_stage1_xip.py` (8 tests): host execution
  of both C leaves against a redirected XIP block (documents the host
  DATA-FIFO aliasing: the prologue command word is what the loop reads
  back), interpreter unit checks for the new opcodes (`lsli`, `rotli`,
  `ldbi.b`, `stbi.b`, `cmpne`/`bt`), stock-envelope regression, and
  fit/no-relocation regression.

Accepted boundary (documented, not verified): controller reads are
scripted, not derived from prior writes; the `r0` return value is not
compared (both leaves are void and the stock leaves path-dependent
residue); concurrent status updates and timing are unmodeled. Hardware
timing and whole-device behavior remain unqualified
(`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-xip` in
`tools/build_gx8002_source_candidate.py` (artifact `xip.elf`, baseline
above) and in the `gx8002-source-candidate` test list in `g2/Makefile`.
The shared `make -C g2 gx8002-source-candidate` gate was not run here:
it currently fails before reaching any stage-1 tranche at a
pre-existing stale baseline owned elsewhere (same `rtc-init` pin drift
reported by the prior tranche; left for its owner). Tranche admission
was verified through the builder's exact `reviewed_replacements` +
`compose` path in a private output dir: 2 replacements, 250 compiled
bytes + 6 generated fill, ownership splits at package `0x1910..0x1990`
and `0x1990..0x1a10`, firmware size unchanged. The generated
`gx8002-source-candidate-build.{json,md}` and experimental manifest
pins regenerate from the green shared run, so they are deliberately not
hand-edited here.

## Remains (CD-001, still retained)

CD-001 is now 670/8192 bytes source-owned (414 prior + 256 here).
Still retained: vector table (`0x10000000..0x100000FF`, blocked on
unreconstructed trap targets), init routine (`0x100001BC`), the
chip-id/early-UART routine (`0x100001FC`), the image-receive routine
(`0x100002C8`), the PMU descriptor-fill routine (`0x10000780`, ~168
call-free bytes with a table lookup — analyzed this pass, next
candidate), the baud computation (`0x100004D0`, two retained lookup
callees at `0x10000D98` / `0x10000EA0`), the configure routine
(`0x100005C4`), the checksum helper (`0x1000065C`), the handshake
loop at `0x10001DDC..`, and everything else up to `0x10002000`.
Hardware qualification stays blocked by unavailable physical evidence.
