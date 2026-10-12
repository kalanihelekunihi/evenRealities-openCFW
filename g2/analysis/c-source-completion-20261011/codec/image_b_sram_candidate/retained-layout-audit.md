# Image-B retained SRAM placement audit

The source-owned GSC angle/create/process code graph is 228 C-SKY units with
zero unresolved GSC code entries. The separate 228-unit build receipt is
`build-gsc-process-ram-binding-round/receipt.json`; linked object SHA-256 is
`ee7554b1e8273a82aa972892367562c46c4583a0d8d79ddbd8f8f680678afd5c`.

Native CRT `0x10003128..0x1000313e` clears
`[0x20017090,0x2002d79c)`. The native process energy flag at
`0x2002d79c` is read at `0x1000ccce` and written to one at `0x1000ccf8`;
the ring counter at `0x2002d7a0` is read at `0x1000d596` and updated by
the process. The four operation words occupy `0x2002d7a4..0x2002d7b3`;
native `0x1000deb4..0x1000dec8` copies them from the source-owned
initializer `0x1000b800`. The IMCRA setting word at `0x2002d7b4` is read
at `0x1000e7cc`; no image-B source producer or initial value is known.

`backup_runtime_retained_slots.c` gives these four regions typed extents
without initializers. The experimental `image_b_retained_layout_candidate.ld`
maps them to exact addresses as `NOLOAD` and binds the two exact stock CRT
bounds. The C-SKY relocatable layout audit links successfully; SHA-256 is
`565716899d98f6cf070cc25182e1ea5c5a3e249caa10f19d519c25306226e84e`.
Object section flags are `ALLOC` without `CONTENTS` or `LOAD` for all four
retained regions; sizes are 4, 4, 16, and 4 bytes. Its only unresolved names
are the callable `native_word_at_zero_1000ada6` and
`uart_dma_ambient_direction_100040e8` contracts. This partial relocatable
is not a bootable image.

The current source `.data` totals 0x7f8 bytes, while the stock normal-copy
initialized range is only 0x12c bytes (`0x20016f60..0x2001708c`). Three
translation units include pinned `clk_priv.h` and each instantiate its static
clock tables, in addition to one explicit source table. These duplicated
mutable C tables account for 0x7a0 bytes; the remaining typed initialized
state is 0x58 bytes. The stock clock tables are in the instruction image at
`0x1001699c..0x10016b84`. A final custom linker/startup must place one
source-owned clock table in loaded ROM or otherwise prove relocation and
normal-copy behavior, preserve fixed SRAM literal users, provide vector/reset
source, and establish initialized-data copy. Placing the current 0x7f8-byte
`.data` at the stock start would overwrite the native BSS beginning at
`0x20017090`. The unknown IMCRA setting contents and two callable ambient
contracts remain genuine behavior inputs; this layout does not assign values.

## Single-owner source placement probe

An experimental relocatable uses `backup_clock_single_owner_experiment.c`
to instantiate the pinned clock tables once and export the three native
table names as assembler aliases. Its 226-object link starts from the
coherent 228-unit receipt, replaces the four clock-related objects and
initialized-data object with the aggregate clock object and a
`-fdata-sections` compile of the same typed data, and adds the retained
slots. `image_b_source_placement_probe.ld` asserts the clock table extents
(0x1a0, 3, 0x44), gsensor (4) and IMCRA profile (0x54) extents, no generic
initialized `.data`, and four retained NOLOAD extents. The partial
relocatable places `.text` (0xe6ec) at 0x10003100, `.rodata` (0x22c0)
at 0x100117ec, and the clock tables at 0x1001699c, 0x10016b3c,
and 0x10016b40. It does not provide vector, reset, or normal-copy
payload source and is not a bootable ELF.

The stock normal-copy range is 300 bytes. Typed roles are now attributable
for all 300 bytes: gsensor workstate (4), audio runtime state (16),
LVP_APP selector and record (36),
mutable BUXX audio UART TX packet (32), IMCRA profile (84), and two RFFT
descriptors (40), and fdlibm kernel coefficients (88). The BUXX initializer compiles to the exact stock bytes
at 0x20016f98..0x20016fb7 (32/32; SHA-256
`8b01930ac4be34abf334d84980b37a69d63aad53b436527da6fa3d014c428fbe`).
The audio runtime state at 0x20016f64..0x20016f73 is a typed pair of
UART RX header progress counters, one-shot audio flag, and signed callback
counter. Its compiled 16 bytes equal stock exactly, SHA-256
`a8f493a17d108b7990f6efde8f9d6f7d73c35d56778dbb9d89ca65e0a97fa359`.
The last 88 bytes at 0x20017034..0x2001708b match pinned Android bionic
fdlibm `k_sin.c` S2..S6 and `k_cos.c` C1..C6, commit
`a27d2baa0c1a2ec70f47ea9199b1dd6762c8a349`. The typed C record
`backup_trigonometry_kernel_coefficients.c` compiles to exact stock bytes
(88/88; SHA-256
`4a1eeeac5f3da50912682f58a23def82f95d14808cbaf8646ebc91469f69d478`).
The reproducible target check and source hashes are in
`new-initialized-records-receipt.json` and its companion verifier.
This closes normal-copy *record attribution*, not startup copy behavior,
final linker placement, or image-wide runtime semantics.

The reproducible `build_full_initialized_layout_probe.py` experiment now
hash-checks and reuses 225 selected objects from the 231-unit separate
target receipt, recompiles eleven experimental units, and links 236 objects
with `image_b_full_initialized_layout_probe.ld`. Every one of the nine
normal-copy records has an exact target SRAM address and size assertion;
the size sum is 300 bytes. The one-owner clock tables and four retained
NOLOAD cells are placed independently. The partial relocatable SHA-256 is
`7583d418f12b5042172a59e5fa2cd7d3bddc443009089dd95bcf6af79f5c2582`.
Its two unresolved names are the native address-zero read contract and
UART out-of-domain direction contract. The sample-app audio callback
has a complete experimental C body with real MMIO and audio-output
interfaces, but its native arithmetic branches and indirect audio effects
have not yet passed a whole-body original/source oracle. The rebased host
fixture `sample-audio-callback-host-receipt.json` passes three source-state
cuts (initial/recovery, direct frame, timestamp wrap) with stubbed output,
logger, and nonzero divider; it is not native or hardware evidence.
The five-command UART callback is source-reduced into experimental C but
does not yet have a bounded native-effects oracle. The sample-app event
callback is expressed in a C
translation unit with faithful C-SKY inline assembly, preserving native
SP+8/+12 as untouched ambient words before the indirect audio operation.
This source placement is not a bootable
ELF and still lacks vector/reset/loader integration, qualified callbacks,
and hardware FP qualification.
The LVP_APP record and callback units remain experimental; the BUXX
template is now selected in the separate 231-unit graph. The remaining
callback qualification and final initialized-data placement remain open.

The native stage2 byte image is 0x1408c bytes and begins at 0x10003000;
its final 300 bytes therefore occupy 0x10016f60..0x1001708b. Pinned
NationalChip `arch/soc/grus/link.ld` and `spl/spl.c` model a contiguous
stage2 text+data load with a DRAM placement hold. The **stock B stage-1**
normal branch at `0x10000d4c` now independently proves the packaged
`0x1408c`-byte transfer to `0x10003000` using native flash reader
`0x10000fdc` (`stock-stage1-loader-receipt.json`). That establishes the
copy issuer and load extent; the 0x10016f60 load address and 0x20016f60
runtime address form the SDK-supported linker/alias pair. Physical alias
behavior and the alternate marker-selected boot branch remain unqualified.
The experimental linker script now states `AT(0x10016f60)` through
`AT(0x10017034)` for all nine initialized records. C-SKY `ld -r` retains
their VMAs and exact sizes but reports LMA=VMA for a relocatable output,
so its receipt explicitly marks load addresses unverified by that link.
A separate data-only **final** ELF links three relocation-free records
under `image_b_data_lma_probe.ld`; target `objdump -h` confirms their
32-bit VMAs and distinct IRAM LMAs exactly (16B, 32B, 88B). Its SHA-256
is `de95a5cec1c90719d45beff73e10e15ca76beaa612ba577e6364036adc5c8eb9`.
This proves the toolchain/linker can express the alias placement for those
three records; it does not establish a full 300-byte final data image or
the exact custom-image loader behavior.
