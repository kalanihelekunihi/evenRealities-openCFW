# GX8002 analog C reconstruction on macOS

Date: 2026-09-07. Seven codec leaves now have reviewed C implementations and
native macOS target compilation. They remain outside the production firmware
provider until integration is qualified.

## Native compiler

`make -C g2 csky-macos-toolchain` builds C-SKY binutils and freestanding C GCC
using Apple Clang on this Mac, installing under `g2/build/csky-macos/install`.
The toolchain driver pins the C-SKY builder, binutils and GCC revisions.
The local build succeeded with Apple Clang 21.0.0 on Darwin arm64. Binutils is
2.40.50.20230112 and GCC is 13.0.1. Target is `csky-unknown-elf`, CK804EF,
little-endian, hard-float. Target libc and libgcc are not yet qualified.

The unmodified upstream GCC fix
[9970b576b7e4ae337af1268395ff221348c4b34a](https://gcc.gnu.org/pipermail/gcc-cvs/2024-March/399600.html)
is applied to prevent newer libc++ headers from being poisoned by ctype macros.
Its original patch and provenance are in `tools/toolchain-patches/`.
System zlib avoids the older bundled zlib's macOS `fdopen` macro conflict.
No Linux host or guest is required.

## Recovered behavior

`components/shared/gx8002/runtime_gx8002_analog.c` implements:

| Function suffix (`gx_analog_set_`) | MMIO word | Transformation before 32-bit write |
| --- | --- | --- |
| `pga_itrim` | `0xA0005088` | low byte of `(old & 0xC0) OR min(input,63)` |
| `pga_bypass` | `0xA0005088` | low byte of `(old & 0xBF) OR (input << 6)` |
| `pga_enable` | `0xA0005090` | low byte of `(old & 0xBF) OR (input << 6)` |
| `adc_sample_clk_sel` | `0xA0005094` | low byte of `(old & 0xFE) OR input` |
| `adc_out_at_clk` | `0xA0005094` | low byte of `(old & 0xFD) OR (input << 1)` |
| `adc_in_sel` | `0xA0005094` | low byte of `(old & 0xFB) OR (input << 2)` |
| `adc_rstn` | `0xA0005094` | low byte of `(old & 0xF7) OR (input << 3)` |

Each performs one volatile 32-bit read and one volatile 32-bit write, returning
zero. The input ABI is unsigned 32-bit. Flags are not converted to booleans;
upper bits of the old register are cleared by byte narrowing. These details
come from the authenticated NationalChip ADC object sections that exactly
match both codec images, not guessed register semantics. Public SDK headers
provide the function names and ABI. No SDK object is linked into our output.

## Validation and limits

`make -C g2 gx8002-analog-source-check` regenerates the target object and report
and runs 13 tests. The [checked report](gx8002-analog-source-verification.json)
records source/header hashes, flags, target section hashes and stock offsets.
All seven functions fit their original sections: 172 bytes of compiled code,
corresponding to 344 bytes across the two stock occurrences. The ELF flags
match `0x21006009`; no relocations or undefined symbols are required.

The compiler changes some register allocation and replaces AND-immediate with
AND-NOT-immediate. These changes retain the final byte-narrowed result.
A restricted instruction interpreter compares decoded original and compiled
return values and MMIO traces on 29,855 boundary/random cases. Unsupported
instructions, unexpected addresses, missing returns, relocations, and changed
function inventories fail closed. Separate host C tests exercise all seven
functions against decoded register-transfer expectations.

## LDO analog voltage: a second object, pinned as assembly (CD-004)

`drivers_lib/analog/ldo.o` is a separate NationalChip SDK object from the
`adc.o` leaves above; the whole-image upstream-object scan
(`analyze_gx8002_upstream_objects.py`) found exactly one of its fifteen
functions with a byte-exact stock occurrence inside this repository's
current work scope: `gx_analog_set_ldo_ana_voltage`. It has a sentinel input
(`UINT32_MAX` means "leave the register unchanged", returned as-is rather
than the usual zero success code), then merges the low nibble of the voltage
argument into the upper nibble of the control byte at `0xA0005054` and writes
it back.

As with `gx_dcache_disable`, the pinned toolchain's C lowering of that
mask/OR/narrow sequence chooses a different destination register than the
stock object (it accumulates the merged byte in `r3` and stores from `r3`;
stock accumulates in `r0` and stores from `r0`), even though the mask
constant itself lowers identically (`andi ..., 240`). Fighting the register
allocator through C rewrites did not converge, so
`runtime_gx8002_analog_ldo.c` pins the reviewed algorithm as inline assembly,
matching the pattern used for `gx_dcache_disable`. `verify_gx8002_analog_ldo.py`
authenticates the compiled result against the pinned SDK's `ldo.o` byte for
byte, then differentially checks 144 boundary-value `(voltage, previous)`
pairs against the decoded stock instruction stream (mirroring the
`adc.o` restricted interpreter's approach, extended with `cmpne`/`bf`/`subi`
for the sentinel branch this leaf needs).

The resulting 32-byte section exactly matches the stock object at two package
offsets: 17,496 (boot stage 2 IRAM, the span this closes part of for work
item CD-004) and 91,908 (image A SRAM). There are no relocations or undefined
symbols. `make -C g2 gx8002-source-candidate` now routes both occurrences as
`compiled_assembly`. The other fourteen `ldo.o` leaves
(`gx_analog_set_ldo_fla_*`, `gx_analog_set_ldo_dig_*`,
`gx_analog_get_ldo_*`, `gx_analog_set_ldo_ana_ctrl`, ...) have no byte-exact
occurrence inside this item's target range and are out of scope here; a
future tranche can extend this file's coverage the same way if a
byte-exact occurrence for one of them is found.

This is finite differential testing and manual leaf review, not a complete
C-SKY emulator or an all-input proof. Startup, call-site boundaries, interrupts,
whole-image placement and actual hardware behavior remain unqualified. The
report emits no firmware and admits no production source bytes. The codec's
other code, runtime data, accelerator commands, and model remain incomplete.
