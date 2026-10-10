# NationalChip provider closure, fourth frontier

Private P2 dependency evidence, ready for independent review. No canonical
coverage, source implementation, gate, authenticated input, or installed tool
was changed. Runtime addresses retain the predecessor's conditional XIP/SRAM
mapping; this pass supplies no additional hardware mapping proof.

## New results

The registered `libdriver_release_v1.0.6.a` contains 41 members, rather than
only the eleven examined previously. `closure.py` now inventories and compares
all 585 sized executable function symbols against both authenticated images.
It preserves only declared relocation masks and native-decoded LRW layout
differences. LRW destination register, encoding width, actual referenced pool
word and unrelocated constants must agree. Relocated pools record their symbol,
explicit addend, linked value and scoped base evidence. Named branch targets
are pruned iteratively; an unavailable target stays unresolved.

**23 of the previous 40 unresolved call sites now have an archive provider
candidate at the independently decoded linked destination.** These are 16
symbols: seven analog PGA/ADC setters; `reg_get_val`, `reg_set_val`;
`gx_spi_flash_otp_read`; IRQ save/restore; `gx_request_irq`; `gx_mdelay`;
`gx_get_time_us`; and `gx_pmu_osc_clock_ref_enable`. See every caller/site and
callee extent in `closure.json:prior_unresolved`. This is provider correlation,
not complete semantics or source recovery.

| Selected provider | Conditional stock entry | Symbol extent |
| --- | --- | --- |
| `gx_request_irq` | `0x1002553c` | 30 bytes |
| `gx_irq_handler` | `0x10025574` | 70 bytes |
| `gx_get_time_us` | `0x1002585c` | 104 bytes |
| `gx_mdelay` | `0x1002598c` | 14 bytes |
| `gx_pmu_osc_clock_ref_enable` | `0x10024a10` | 12 bytes |
| `gx_spi_flash_otp_read` | `0x100247f4` | 28 bytes |
| `gx_snpu_init` | `0x10205cf4` | 64 bytes |
| `gx_snpu_get_state` | `0x10205e28` | 6 bytes |
| `snpu_isr` | `0x10205ce0` | 16 bytes |
| `_AudioInISR` | `0x10025e48` | 642 bytes |

Pool normalization closes the earlier SNPU-init/get-state matching limitation:
init's three LRW sites use a BSS pointer `0x20027350`, constant `0xa0c00190`,
and ISR pointer `0x10205ce0`; get-state loads word zero through the same BSS
pointer. The init ISR pointer is independently tied to `snpu_isr` by section
symbol plus addend `0x3f8` and a matching native function body. Audio init's
registered ISR pointer similarly lands on `_AudioInISR`. Their bodies and
transitive effects still require pseudocode review.

The IRQ archive establishes a concrete callback boundary. `gx_request_irq`
rejects IRQ numbers >=32 or null callbacks, stores callback and argument into
eight-byte entries rooted at `0x20026ef4`, and calls `csi_vic_enable_irq`.
`gx_irq_handler` derives the active exception index minus 32, retrieves that
entry, and calls its callback with the derived index in r0 and saved argument
in r1. Its null callback path skips the call. Neither the archive nor this
comparison establishes all runtime table writers, interrupt routing, or
hardware behavior. The table's scoped `.bss` base is `0x20026eec`, with the
registration-table relocation addend +8.

## Metadata correction and false-positive discipline

The predecessor's ELF parser enumerated RELA entries but omitted their explicit
addends, treating raw pool words as if they contained those addends. Its linked
word observations remain evidence; general symbol-base deductions must now use
the real `SHT_RELA` addend. This pass reads both REL and RELA correctly, and
scopes local `.bss`/`.rodata`/section symbols per archive object. Same-named local
symbols in different objects do not identify the same allocated region.

The corrected script still rejects `npu_dis_interrupt` at `0x1020566c`: all
seven linked calls reach `reg_set_bit`, contradicting its `reg_clr_bit` contract.
An assertion protects this discriminator. No unrelated instruction, LRW
register, LRW width, or unrelocated constant is discarded.

The raw permissive inventory retains 3,360 surviving candidate occurrences for
321 symbols; 253 symbols have exactly one surviving candidate and a stable
anchor of at least eight bytes. **These numbers are search inventory, not
accepted identification or additive coverage.** Tiny common wrappers produce
many coincidental interior matches, and identical console wrappers can remain
indistinguishable. Graph-consistent means only that known targets do not
contradict the candidate, not that every target is proved. Unknown relocated
literal bases, multiple candidate targets, and masked ADDR32 fields remain
visible. Callback pointers are recorded only when section/addend resolves an
archive symbol and the linked destination has its matching candidate.

## Remaining 17 sites and public-source discriminators

Five symbols account for all remaining archive-unresolved sites: `memset`,
`printf_`, `strlen`, `strncmp`, and `clk_switch_1m`. Their implementation C is
already present in the pinned public tree, so another download adds nothing.
`source_receipt.py` retains seven bounded native listings, seven source hashes
and the actual stock clock-source table.

- `strlen` and `strncmp` have the public routines' byte-scan and unsigned-byte
  subtraction behavior, including zero-length `strncmp` returning zero. These
  are generic operations and do not uniquely fingerprint this source tree.
- Stock `printf_` calls a three-argument function with `(0, fmt, varargs)`;
  this agrees with `utility/libc/tinyprintf.c`'s `vfprintf` wrapper. The other
  registered `utility/libc/printf.c` wrapper calls a five-argument `_vsnprintf`
  with an output callback, scratch buffer and maximum count, so that direct
  producing-wrapper interpretation is contradicted. The stock callee's full
  formatting implementation remains outside this bounded wrapper inference.
- Stock `memset` first writes up to three bytes to align an initially unaligned
  pointer and then enters word-fill loops. Public `utility/libc/memset.c`
  tests original alignment once and keeps an initially unaligned destination
  on the byte path. This is a useful negative source discriminator even though
  their ordinary memory result agrees; do not claim exact producing source.
- Stock `clk_switch_1m` copies table words `[28,0,18,1]` from `0x10025cd0`,
  calls the archive-correlated clock-source setter twice, scans modules 11..25,
  and performs the PLL disable/restore sequence. Public board C and clock-v2
  enum values agree. Multiple public board variants share this skeleton, and
  the exact producing board/configuration cannot be selected from it alone.

These source discriminators explain the remaining sites without calling them
exact archive matches. Further semantic obligations involve the formatting
callee, precise producing configurations, private driver C and complete
first-party callback/event behavior.

## Reproduction and stopping boundary

Run `python3 closure.py` and `python3 source_receipt.py` from any directory.
They write only this owned output directory. Native tools read the pinned
archive and authenticated images; neither original is modified. `receipt.json`
records the closure-output hash, and `SHA256MANIFEST.json` seals scoped outputs.
The XIP hash remains `49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584`;
SRAM remains `53860d6974097ad494c6697df52f95b796360131fab63cd8bfd7efc9c5596de8`.

Native ELF metadata and GNU decoding supply this branch's independent oracle;
private Ghidra, Ablation and REA do not add a stronger source-identity oracle
here. No new attributable source was found, so there was no download or
submodule proposal. The registered private driver objects supply boundaries
and relocations but not their missing implementation C. Whole-corpus semantic
review, private producing inputs, first-party logic and hardware effects remain
separate work. This is finite closure of the inspected archive/source branch,
not an assertion that nothing remains to learn from the firmware itself.
