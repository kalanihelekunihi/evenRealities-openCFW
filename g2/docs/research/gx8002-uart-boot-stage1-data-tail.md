# GX8002 UART-boot stage-one data tail (CD-002) — structural findings, no bytes closed

Work item CD-002: package `[0x00002050, 0x00002850)` (2,048 bytes) inside
`firmware_codec.bin`, runtime `0x10002000..0x10002800`, the last 2 KiB of the
10,240-byte "UART boot stage 1 (IRAM)" span already tracked as one
`retained_stock` block in `docs/research/gx8002-source-candidate-build.json`
(`{"offset": 0x50, "size": 0x3194, "kind": "retained_stock"}` covers it) and
described at a coarse level in `docs/research/gx8002-stage1-wave6-boundaries.md`
("The body remains opaque and externally supplied"). This note narrows that
opacity for the specific 2,048-byte tail and records a concrete, reproducible
reconstruction attempt. **No byte in the range is source-owned as a result of
this pass**; `runtime_gx8002_uart_boot_stage1_boundary.c` (the authenticated
whole-blob loader) remains the only production route, unchanged.

## 1. The tail is data, not instructions

`csky-unknown-elf-objdump -D -b binary -m csky --adjust-vma=0x10002000` on the
raw 2,048 bytes produces a stream dominated by `bkpt` (zero opcode) and
implausible operand patterns — not code. Treating the full 10,240-byte stage-1
blob (package `0x50..0x2850`) as 32-bit little-endian words instead shows a
standard C-SKY reset/exception vector table at the very base:

```
0x10000000 -> 0x10000100   (reset vector)
0x10000004..0x1000007c -> 0x10000130   (31 words, "default" handler)
0x10000080..0x100000fc -> 0x10000134   (32 words, second handler)
0x10000100: c0001009 c01f6420 ...      (first plausible instruction words)
```

This matches the public NationalChip `grus` SDK's vector-table layout
(`arch/cpu/csky/ck804/spl_start.S`: `.long spl_reset_handler`, `.rept 31
.long spl_default_handler`, `.rept NR_IRQS .long spl_default_handler`,
SDK commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, the commit already
pinned as `SDK_COMMIT` in `tools/analyze_gx8002_upstream_objects.py`), except
that the two rept blocks resolve to two different addresses (`0x130` and
`0x134`) in the stock image where the SDK source would emit the same symbol
address for both — a real, unexplained divergence noted here for whoever
picks up the *text* portion of this span (out of CD-002's scope: CD-002 owns
only `0x2050..0x2850`, the code/vector region is `0x50..0x2050`).

Structurally, our target range breaks into:
- `0x2050..~0x2270` (~544 B): repeating small records, one field incrementing
  1..0x1c (28) — consistent with an initialized array/struct table, not a
  jump table (no value in it resolves to an in-image address).
- `~0x2270..~0x22c0` (~80 B): a run of 16-18 32-bit words each shaped like
  `0x003fNNNN` — plausible MMIO register offsets, terminated by `0xffffffff`
  then `0x000000a1`.
- `0x2280..0x2470`, `0x24c0..0x27ef` (≈1,264 B total): all zero.
- `0x2470..0x24c0` (~80 B): a handful of small integers (1, 0x80, 0xdc, 0x6c,
  0xb70b, 2, 3, 4, 0x11, 1) then zero again.
- `0x27f0..0x2850` (final 16 B): mostly zero with a short non-zero tail.

1,792 of the 2,048 bytes (87.5%) are `0x00`. SHA-256 of the exact range:
`7636cc9e9502200fde2788f1f0d4d2bdeb59aef000084f5634fcf792a47f6180`.

## 2. A linker-script-scoped hypothesis: `.stage1_sram_data`

`arch/soc/grus/link.ld` (same pinned SDK commit) places stage-1's compiled
output in two sections, both scoped to a small, explicit object list:

```
.stage1_sram_text : { spl_start.o(.spl.vectors*,.text*,.rodata*)
                       spl*.o(.text*,.rodata*)
                       CONFIG_BOARD_PATH/boot_board.o(.text*,.rodata*) }
.stage1_sram_data : { spl_start.o(.data*)
                       spl*.o(.data*)
                       CONFIG_BOARD_PATH/boot_board.o(.data*) }
```

`arch/soc/grus/spl/*.c` (`spl.c`, `spl_clk.c`, `spl_counter.c`,
`spl_dw_dmac_ahb.c`, `spl_i2c.c`, `spl_osc.c`, `spl_spinor.c`, `spl_trim.c` —
`spl_spi.c` is *not* in `boot_objs`, so it is not linked) plus
`arch/cpu/csky/ck804/spl_start.S` and a board's `boot_board.c` are exactly
the "Secondary Program Loader" — i.e. the UART-boot stage-1 loader — in this
GPL-2.0+-licensed NationalChip tree, vendored (but not built) under
`build/upstream-nationalchip-lvp-kws` at the already-pinned `SDK_COMMIT`.
`spl.c:15` declares:

```c
unsigned int uart_new_baudrate = 115200;
```

`115200 == 0x0001C200`. The stock package bytes at offset `0x2060` (i.e.
`0x2050 + 0x10`, well inside CD-002's range) are `00 c2 01 00`, the exact
little-endian encoding of `0x0001C200`. This 4-byte value occurs **exactly
once** in the whole 10,240-byte stage-1 blob (checked exhaustively), so this
is a real, non-coincidental match, not noise.

## 3. Reconstruction attempt and result (does not close the range)

Using `build/csky-macos/install/bin/csky-unknown-elf-gcc` (our own pinned
toolchain, never the vendor's `.o`/`.a`) with flags mirroring
`build/upstream-nationalchip-lvp-kws/uart_boot.mk`
(`-mcpu=ck804ef -mhard-float -ffreestanding -fno-builtin -ffunction-sections
-nostdlib -fstrict-volatile-bitfields -DCONFIG_ARCH_GRUS`), the closest
available public board (`boards/nationalchip/grus_gx8002b_dev_1v`, the only
board named by a checked-in `.config` —
`configs/github_grus_gx8002b_dev_erji_english.config`, `CONFIG_GX8002B=y`),
and a hand-derived `autoconf.h` from that `.config` with `CONFIG_BOOT_BY_FLASH`
swapped for `CONFIG_BOOT_BY_UART` (the stock image is UART-boot per
`tools/manifests/g2-codec-fwpk-segment-map.tsv`), all nine translation units
compiled cleanly against the vendored public headers. Concatenating each
object's `.data` section in the linker script's file order
(`spl_start, spl_clk, spl, spl_spinor, spl_dw_dmac_ahb, spl_i2c, spl_counter,
spl_uart, spl_trim, spl_osc, boot_board`) reproduces the `uart_new_baudrate`
anchor at a consistent relative offset, confirming §2's identification, but
the surrounding bytes do **not** line up:

| `-O` level | reconstructed `.data` length | bytes matching stock (aligned on the anchor) |
|---|---:|---:|
| `-O0` | 652 B | 125 / 652 (19.2%) |
| `-O2` | 541 B | 102 / 541 (18.9%) |
| `-O3` | 541 B | 102 / 541 (18.9%) |
| `-Os` | 653 B | 112 / 653 (17.2%) |

Match rates are consistent with chance agreement on small/zero fields, not a
structural match. This is expected: `configs/github_grus_gx8002b_dev_erji_*`
is a public demo config (flash-boot, not UART-boot), the repository has no
copy of Even Realities' actual production `.config`/board tree, and this
firmware is evidently a customized product build (confirmed UART-boot,
`CONFIG_STAGE1_SRAM_SIZE` = `0x2800` here vs. the SDK's own default `0x3000`
in `arch/soc/grus/include/soc_config.h`) that this public SDK snapshot does
not, by itself, reproduce byte-for-byte.

## 4. Disposition

No byte in `0x10002000..0x10002800` is claimed as source-owned. The evidence
supports (but does not prove) that this tail is the compiled `.data`/padded
`.bss` of the vendored `arch/soc/grus/spl/*.c` + `spl_start.S` +
`<board>/boot_board.c` cluster; it does not identify the exact product board,
build flags, or possible product-specific source deltas needed for a
byte-exact, evidenced `generated_source_data`/`compiled_c` replacement.
Labeling this range source-owned without that convergence would be exactly
the "binary bytes encoded as C arrays" / "inferred without evidence" failure
mode the goal text rules out.

### Followups for whoever picks this range up next

- Systematically retry §3 across the other GX8002B board directories now
  present at `build/upstream-nationalchip-lvp-kws/boards/nationalchip/`
  (`grus_gx8002b_aiot_1v`, `grus_gx8002b_debug_1v`, `grus_gx8002b_k150_aopu_1v`,
  `grus_gx8002b_smartdog_1v`, `grus_gx8002c_dev_1v`) — none were tried this
  pass beyond `grus_gx8002b_dev_1v`, and `boot_board.c` differs per board.
- The repo's SDK checkout is a partial/promisor clone; `boards/` (115 files)
  was previously not materialized locally and was fetched this pass via
  `git -C build/upstream-nationalchip-lvp-kws checkout HEAD -- boards/`
  (content verified against the already-pinned `SDK_COMMIT` tree, so this is
  additive completion of the existing pin, not a new dependency). It is left
  checked out for reuse; `build/` is git-ignored in the outer repo so this
  does not touch tracked state.
- A more conclusive path than guessing board/optimization combinations:
  decompile the *text* portion of this same stage-1 image
  (`0x10000100..0x10002000`, out of CD-002's scope) far enough to find the
  `lrw`/`ld.w` sites that address `0x10002000..0x10002800`, and use those
  cross-references to identify each field by use rather than by matching a
  guessed rebuild.
- If Even Realities' actual production `.config`/board directory is ever
  obtained (it is not in this public SDK snapshot), rerun §3 directly against
  it instead of guessing.

## Verification performed

```sh
python3 -c "import json; d=json.load(open('build/source/flash-plan.json')); \
  a,b=0x10002000,0x10002800; [print(r['target_address_hex'], r['end_exclusive_hex'], \
  r['address_status'], r['function'][:90]) for r in d['flash_regions'] \
  if r['component']=='codec' and r['target_address']<b and r['end_exclusive']>a]"
# -> single region 0x10000000..0x10002800, confirmed_from_uart_boot_header_and_vectors,
#    address_status unchanged by this note.
```

No hardware operation of any kind occurred. `docs/research/gx8002-source-candidate-build.json`,
`overlay.json`, `Makefile`, and `tools/build_gx8002_source_candidate.py` are
unmodified — there is no verified source to register.
