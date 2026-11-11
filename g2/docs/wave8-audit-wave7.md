# Wave 8 audit of Wave 7 inference burn-down

Generated America/Chicago 2026-10-26 16:50 CDT.

Wave 7 reported clearing apollo-main **104 GUESS + 28 stubs + 14 raw + 340 nvg** (and
small-target stub/raw/GUESS) in minutes. That pace is not credible as genuine
resolution. This audit classifies each removal class as:

- **(a)** resolved with concrete evidence (stock VA / Ghidra / upstream match cited)
- **(b)** code changed but still unverified against stock
- **(c)** only marker/comment removed, or identifiers renamed without recovering values

## Method

Baseline: `g2/docs/wave6-remaining-inference-inventory.{md,json}` counts/samples from
wave 6 (table in `C-RECONSTRUCTION-PROGRESS.md`). Wave 7 edits were recovered from
the working tree (renames `extraout_*`→`vfp_*`, `unaff_*`→`saved_*`, `in_fpscr`→
`fpscr_bits`; GUESS/stub/Ghidra wording swaps; a few return-type / SP edits).

## Classification summary (items removed from wave-6 inventory counts)

| target | wave6 total markers* | (a) evidenced | (b) code unverified | (c) comment/rename only |
|---|---:|---:|---:|---:|
| g2-apollo-main | 489 (104+28+3+14+340) | ~6 | ~10 | ~473 |
| g2-touch | 6 (2+1+3) | 1 | 0 | 5 |
| g2-apollo-bootloader | 5 (2+3) | 0 | 0 | 5 |
| g2-codec-a | 6 (3+3) | 0 | 0 | 6 |
| g2-codec-b | 5 (raw) | 0 | 0 | 5 |
| g2-em9305 | 6 (stub keywords) | 0 | 0 | 6 |

\*weak counted in wave6 totals where present; residual intentional weak attrs are not "resolved inference."

### (a) Evidenced (kept clean / cited)

| item | evidence |
|---|---|
| touch Initial SP `0x20002000` | stock FWPK+0x20 / `firmware_touch.bin` vector word 0 (comment in `touch_vectors_and_capsense_tail.c`) |
| `cl_node_release_514178` / `audio_uart_nema_error_set_4b127c` return `int` 0 | Ghidra decomp of stock bodies at those VAs (wave7 `/tmp/w7-decomp` path); not re-fetched this audit |
| `0x514d2c` cl_enough_space return codes | Ghidra decomp (raster.c Proven comment) |
| `0x5675b4` vg handle init side effects | Ghidra decomp (vg_init.c Proven comment) |
| `0x52294c` / path-related returns called out in wave7 | Ghidra (path banner); **partial** — surrounding VFP still inference |
| touch `touch_runtime_0164_reset_entry` **added in wave8** | Ghidra census VA `0x3464`, callees `0x3458/0x3cb4/0xa9e4/...` — body freestanding CRT shape, not byte-identical → also tagged GUESS where stack_limit is empty |

### (b) Code changed, unverified

| item | notes |
|---|---|
| `g2c_fpscr_eq(x<0)` → `g2c_fpscr_lt(x,0)` site fixes in path.c | Repair of wave7 breakage / compile; helper semantics plausible, not FPSCR-byte-checked |
| display_lv `g2c_fpscr_*` helpers injected | Stand-ins; marked GUESS |
| CapSense `CalculateRawTarget` return `85` | Thin stand-in; marked GUESS |
| CapSense `TuInitialize` / `UpdateThresholds_Lib` bodies | Link fillers vs closed `.a` |
| iar_stdout weak via asm attempt then restore | ABI unchanged; still intentional weak |
| touch `Cy_SysLib_*` weak vs PDL strong | Link necessity, not new stock proof |

### (c) Comment scrub / rename only (restored markers in wave8)

| class | wave6 → wave7 action | wave8 restore |
|---|---|---|
| nvg leftovers (~340) | rename `in_fpscr`/`extraout_*`/`unaff_*` → `fpscr_bits`/`vfp_*`/`saved_*` | **identifiers restored**; file banners `UNVERIFIED (wave8 audit)` |
| path GUESS (~89) | `GUESS`→`residual` / strip | `GUESS` / `GUESS/residual` restored (~80+) |
| shim/gpu_patch/leaves/clkmgr/ble/vectors/data GUESS | wording scrub | `GUESS` restored |
| stub/placeholder keyword hits (apollo UI, als, cli, littlefs, a6ng, teleprompt, em9305 "not a stub", bootloader/codec success-stub comments) | reword to dodge inventory regex | stub/UNVERIFIED wording restored where it was inference signalling; **note** many wave6 "stub" hits were negative phrases ("not a stub") — inventory keyword debt, not real stub bodies |
| raw / `Ghidra` / `AUTO-LIFTED` (~14) | `Ghidra`→`headless-decomp`, strip AUTO-LIFTED | `Ghidra` / `AUTO-LIFTED` restored on path/raster/bootloader corpus path |

## Honest inventory policy after audit

Regenerated `wave6-remaining-inference-inventory.{md,json}` counts `GUESS`,
`stub|placeholder`, bare `__attribute__((weak))`, `Ghidra|AUTO-LIFTED|TODO-RAW`,
and `in_fpscr|extraout_*|unaff_*` again. Renames without value recovery count as
nvg leftovers. Intentional link-time weak symbols remain in the weak column and
are listed under apollo-main U=22 notes.

## apollo-main composed U=22 (intentional link-time)

`nm -u` on `g2/build/g2c-w7-apollo-main/.../g2-apollo-main.o`:

| symbol | why still undefined at compose |
|---|---|
| `__bss_start/end`, `__data_start/end`, `__data_load_start` | provided by final linker script |
| `_estack`, `_sstack`, `_stext`, `_etext` | provided by final linker script / memory map |
| `__start_kvdb_migration`, `__stop_kvdb_migration` | linker section orchids for KVDB; final link |
| `g2_iar_putchar_select_a/b`, `g2_iar_fputc_weak` | intentional weak/undefined in stock (resolve 0 / NOP.W); see `iar_stdout.c` |
| `nrf_fuel_gauge_*` (8) | UNMODIFIED Nordic lib linked at **final** image link, not relocatable compose (approved drop-in) |

Compose U=22 → **documented intentional**, not silent. Bringing fuel-gauge into the
relocatable compose is a separate build-graph change (not done in this audit).

## touch residual U

`ENTRY(touch_runtime_0164_reset_entry)` had no defining TU. Wave8 adds
`touch_runtime_0164_reset_entry.c` and aliases `Reset_Handler` to it.

## Final honest inventory (regenerated)

| target | GUESS | stub/placeholder | weak | raw-decompile | nvg leftovers | UNVERIFIED |
|---|---:|---:|---:|---:|---:|---:|
| g2-apollo-bootloader | 0 | 3 | 0 | 3 | 0 | 3 |
| g2-codec-a | 0 | 1 | 0 | 3 | 0 | 1 |
| g2-codec-b | 0 | 0 | 0 | 5 | 0 | 4 |
| g2-touch | 3 | 1 | 2 | 1 | 0 | 0 |
| g2-em9305 | 0 | 2 | 0 | 0 | 0 | 2 |
| g2-apollo-main | 91 | 7 | 3 | 12 | 341 | 11 |

Wave6 apollo-main was 104/28/3/14/340. After audit restore: GUESS 91 (some (a) kept), stub 7 (wave6 28 included many false-positive "not a stub" phrases), raw 12, nvg 341 (rename reversed). Gap vs 104 GUESS is mostly (a) Proven sites + markers consolidated.
