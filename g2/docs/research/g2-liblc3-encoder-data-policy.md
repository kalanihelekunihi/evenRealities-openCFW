# G2 Apollo specialized LC3 pointer-table data policy

Status date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Result: 404-byte writable-data policy closed as immutable relocated XIP;
placement and routing remain blocked

## Result

The safely specialized LC3 encoder's complete 404-byte `SHF_WRITE` section is
not runtime state. It contains five initialized pointer tables. Every nonzero
word is covered by one internal `R_ARM_ABS32` relocation to the encoder's
read-only table section, and retained encoder code only loads from the five
tables. There is no runtime initializer and no retained write.

The admitted specialized builder therefore keeps the 404 bytes in flash as a
distinct 8-byte-aligned `.lc3_table_rodata` section. It authenticates the
pre-policy closure, clears `SHF_WRITE`, authenticates the post-policy closure,
and refuses to emit final XIP section bytes until an explicit finalizer has
applied every relocation. Load and run addresses are equal. The policy needs
zero runtime-copy bytes and zero writable RAM bytes.

This closes the data load/run and reusable software-finalizer policy
independently. The deterministic finalizer qualification uses synthetic
addresses and synthetic runtime bindings; it does not select a stock flash
address, authenticate stock imports, emit a firmware image, or route
`service_audio`.

## Exact contents

The specialized template is 404 bytes, SHA-256
`c4c45a0ea2a6895b34d21adc0a20928de754948d66e8270883ddb3a9a5e8372a`.
Its five contiguous Arm32 objects are:

| Object | Offset | Bytes | Purpose |
|---|---:|---:|---|
| `lc3_band_lim` | `0x000` | 112 | duration/sample-rate band-limit pointers |
| `lc3_fft_twiddles_bf2` | `0x070` | 60 | radix-2 FFT twiddle pointers |
| `lc3_fft_twiddles_bf3` | `0x0AC` | 8 | radix-3 FFT twiddle pointers |
| `lc3_mdct_rot` | `0x0B4` | 112 | MDCT rotation-definition pointers |
| `lc3_mdct_win` | `0x124` | 112 | MDCT window pointers |

The objects exactly cover `[0x000,0x194)`. Of 101 words, 78 are initialized
pointers and 23 are configuration-dependent null entries. The 78 relocation
offsets are unique, word-aligned, and equal the complete set of nonzero words.
Every addend is four-byte aligned and falls inside the 60,316-byte specialized
read-only section. Apple and Linux builds produce the same template bytes,
relocation offsets, and relocation record SHA-256
`e47150cbdfca56d7575ed556bffcf46e2f5e54795a7499d62ec4f51e28a0373a`.

A bounded relocation model checks exact size, count, uniqueness, word
alignment, nonzero-word coverage, rodata bounds, base alignment, and uint32
overflow. At a non-placement synthetic rodata base of `0x00600000`, both
profiles produce relocated-table SHA-256
`e4be491719ee3382e1487e4f119edd7e464d46b6a0c8c3cdc790b46bbfc7a6d7`.
That synthetic address is a deterministic test vector, not placement
authority.

## Mutability proof

The upstream declarations expose arrays of pointers to const data rather than
const pointer arrays, which is why Clang initially emits `SHF_WRITE`. The
authenticated source closure contains no assignment through any of the five
symbols:

- `energy.c` and `sns.c` each load `lc3_band_lim[dt][sr]`;
- the retained FFT reads the two twiddle tables;
- `lc3_mdct_forward` reads one rotation and one window pointer; and
- `tables.c` supplies only the initializers.

The retained object has six address sites, encoded as exactly six
`R_ARM_THM_MOVW_ABS_NC`/`R_ARM_THM_MOVT_ABS` pairs. Four relocation records
name `lc3_band_lim`; each other table has two. Disassembly at every site loads
the selected pointer. There is no store reference, runtime initializer, or
external relocation into a table object.

The policy remains fail-closed against future source growth. Source hashes and
reference counts are pinned, the linker admits only the five exact input
sections, an assertion rejects any other retained `.data`, and the analyzer
rejects new symbols, references, writes, relocation kinds, relocation cells,
or runtime imports.

## Production linker policy

`data_policy_linker.ld` first produces the exact table section while retaining
the input write flag. Only after the analyzer authenticates the section,
symbols, xrefs, and 78 relocations does the reviewed `llvm-objcopy` step clear
`SHF_WRITE`. This sequencing prevents a newly writable object from being
silently classified as read-only.

The resulting deterministic receipts are:

| Profile | Pre-policy object | Read-only policy object | Text |
|---|---:|---:|---:|
| Apple Clang 21.0.0 | 116,560 bytes, `ac1f8d7e8e0f81e12b6b47b05dd6659d468a41181ab926c239237449a7326767` | 116,268 bytes, `bc548b0578f87d43c38def5fb727533a73d7e2f31105e5e8bd0d0a1fef336b7d` | 40,880 |
| Homebrew Clang 22.1.8 | 117,728 bytes, `2ecc5b6d399663d484c2274b8c60706c16211e207e871c4fc6ae38edbadddd08` | 117,436 bytes, `7806bcb4959759e5377d892ff1ccfeda6c6947876b31cb92e2dc5e65aa99615e` | 42,016 |

Both read-only objects contain no allocated writable section and retain the
same 11 specialized runtime imports. The read-only tables remain 60,316 bytes
with SHA-256
`9ad7f0d2de1c6468fcd36dc447699f4df7fd86988e87e4df4200f893d5879f59`.

The specialized builder now exercises the production finalizer with an exact
synthetic layout. The input has 484 relocations, including all 78 table
entries and 12 text references; the final ELF has zero relocations and zero
undefined symbols. Before emitting the qualification XIP binaries, the
finalizer checks all 78 table words against the assigned rodata base. Its
synthetic final table SHA-256 is
`7a45677ec32a00f9e572fa1da79b45b2fd00933f1228f1e9252709b3c0e78c89`.

That proves relocation ordering and binary emission, not stock placement. A
production caller must still supply authenticated aligned text/rodata/table
addresses and exact stock runtime bindings. The same finalizer rejects missing
or additional bindings, even/non-Thumb targets, branch-range escape, section
overlap, noncanonical padding, retained relocations, undefined symbols, or
word-level table relocation mismatch. Raw policy objects and qualification
artifacts are not firmware images.

## Composition with service state

The table policy consumes 404 flash bytes and **zero RAM bytes**. Four compact
service-audio adapter states require `4 × 2,628 = 10,512` writable bytes. The
four authenticated stock slots are exactly the same size, so the additional
RAM requirement and adapter-state deficit are both zero.

All four adapter-state addresses are authenticated and assigned to their
existing stock slots. The XIP layout validator rejects table misalignment,
rodata/table overlap, non-adjacent table placement, uint32 overflow,
flash-bound escape, or protected-range overlap. The state validator separately
rejects misalignment, RAM-bound escape, incorrect context count, and overlap
with occupied SRAM.

This policy does not reduce the current 30,516-byte flash-capacity shortfall:
the 404 bytes were already counted in the specialized flash span. It removes
the former requirement for an unproven data-copy initializer and RAM run
address. No core builder, package manifest, call site, flash plan, or firmware
image was changed. No hardware operation or validation was attempted.

## Reproduction

```sh
python3 g2/tools/analyze_g2_liblc3_encoder_data_policy.py --pretty
python3 -m unittest -v g2.tests.test_analyze_g2_liblc3_encoder_data_policy
python3 -m unittest -v g2.tests.test_apollo_liblc3_specialized_xip
```

The machine-readable contract is
`components/apollo_main/liblc3_encoder/data_policy_admission.json`.
