# GX8002 UART boot stage-1 reset entry (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime `0x10000000..0x10002000`).
Prior passes decoded the span (`gx8002-uart-boot-stage1-cd001-analysis.md`)
and closed three leaf envelopes as reviewed C
(`gx8002-uart-stage1-divmod-source.md`: 128 stock bytes). This tranche closes
the 48-byte reset prologue as production-routed reviewed assembly in the
experimental codec candidate: **48 stock bytes replaced by 48 compiled bytes,
zero fill**.

## Envelope

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_boot_stage1_reset` | `0x10000100` | `0x150` | 48 | 48 | compiled_assembly |

34 bytes of code (`lrw`/`mtcr`/`mfcr`/`bclri`/`mov`/`bsr`), one zero-halfword
`bkpt` alignment pad, and a 12-byte literal pool (`0x80000200`, `0x10000000`,
`0x200027fc`). The envelope ends exactly where the shared exception trap
(`0x10000130`, `br self`) begins; the traps stay retained (trap stubs do not
count toward completion).

## Provenance

Reviewed MIT assembly in
`components/shared/gx8002/runtime_gx8002_uart_boot_stage1_reset.S`, derived
from the pinned NationalChip grus SDK `arch/cpu/csky/ck804/spl_start.S`
(`spl_reset_handler`, commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`,
MIT; blob `75ac5560f9f82af420c207ba33fde4f612c8e5d3` authenticated at
verify time, SDK `LICENSE` blob `37a1e362999f2040c2c0cda1a3231b6b5913efbf`).
No SDK text is reproduced beyond the instruction sequence the stock already
encodes; the file carries the UART-boot recovered configuration:

- vector base `0x10000000` (the stage-1 table at IRAM base),
- stack `0x200027fc` (recovered `CONFIG_STAGE1_STACK` value for this image;
  distinct from the image-A SPL value `0x20002ffc`),
- first call `0x100001bc` (stage-1 init),
- second call `0x10002900` (stage-2 code entry: load address `0x10002800`
  plus its 256-byte vector table, confirming the CD-001-analysis chain-load
  reading against CD-003's range).

Upstream `jbsr` is adapted to `bsr` to match the stock encoding, the same
adaptation the admitted image-A SPL reconstruction already uses. See
`NATIONALCHIP-UART-BOOT-STAGE1-RESET-NOTICE.txt`.

## Verification

`g2/tools/verify_gx8002_uart_stage1_reset.py` (baseline
`docs/research/gx8002-uart-stage1-reset-verification.json`, 108 cases):

- Assembles with `-mcpu=ck804ef -mhard-float`, links `.text` at `0x10000100`
  with all four symbols resolved to the documented addresses: no
  relocations, no undefined symbols, section length exactly 48 at
  4-byte alignment.
- Linked bytes are byte-exact against stock package `0x150..0x180`.
- Decoded-target execution of the linked body across 36 `CR31` inputs × 3
  register seeds: exact control-register/call trace (`PSR := 0x80000200`,
  `CR31 &= ~8`, `VBR := 0x10000000`, call init then stage-2 entry with
  `r14 = 0x200027fc` at both calls) against an independent oracle.

Accepted boundary (documented, not verified): init and the stage-2 entry
are genuine external call boundaries whose contents stay retained stock at
their own addresses; whatever they do to machine state is unmodeled.
Hardware timing and whole-device behavior remain unqualified
(`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-reset` in `tools/build_gx8002_source_candidate.py`
(artifact `reset.elf`, baseline above). `make -C g2 gx8002-source-candidate`
and `make -C g2 codec-source-experimental` pass; ownership splits the former
`retained_stock` span at package `0x150..0x180` into one `compiled_assembly`
section with no fill.

## Remains (CD-001, still retained)

Vector table (`0x10000000..0x100000ff`, blocked on unreconstructed trap
targets), init routine (`0x100001bc`, five retained callees), baud
computation (`0x100004d0`, two retained lookup callees), UART
handshake/receive loop, and everything else from `0x10000182` to
`0x10002000`. Hardware qualification stays blocked by unavailable physical
evidence.
