# Native macOS C-SKY decompilation and processor correction

Date: 2026-09-07. `make -C g2 gx8002-known-function-harvest` now exports 24
named image-B functions at their actual SRAM addresses. The output is analysis
evidence, not automatically admitted C or firmware input.

The processor source is
[taligentx/ghidra_csky_WinnerMicro](https://github.com/taligentx/ghidra_csky_WinnerMicro)
at commit `0daaa056e8c570ba514fc0d0226384ecf9f9df05`, based on leommxj's
C-SKY module. It includes CK804EF/DSP support and fixes beyond the original
module. This repository is fetched only under `build/`; it is not vendored
or represented as a firmware dependency. Its complete module licensing has
not been established by this inspection.

The runner authenticates the SDK/firmware candidates and processor revision,
copies tracked processor files into its build directory, and compiles Sleigh
with the installed Ghidra 12.1.3 and Homebrew JDK 21. Settings and caches stay
under the workspace. Ghidra loads the local module through its external-module
property; no global Ghidra installation or user settings are changed.

## A reproduced processor bug

The upstream `movih` rule widened the result of a 16-bit left shift:

```text
zext( immediate:2 << 16 )
```

That truncates the shift to zero before extending it. The codec instruction
`movih r3,0xa0a0` therefore incorrectly became address zero, even though GNU
objdump and the target instruction encode `0xA0A00000`.

The local analysis copy now zero-extends first, then shifts at register width:

```text
zext( immediate:2 ) << 16
```

The input `32b_data.sinc` SHA-256 is
`3dde82aa3bc3bfbb70dc8950705cd0c2a59173e924ee6f92f9005ed880d5210b`;
the patched file is
`0135b93175df811b7b97484d1c6ddb3df0120c35089d4e60c86a061de28fe68f`.
The runner rejects an unexpected original rule. `CheckCskyMovih.java` checks
the actual firmware instruction bytes and evaluates its constant p-code;
`0xA0A00000` is required before the harvest is accepted. This is a local fix,
not an upstream commit or a submitted upstream report.

## Hardware access preservation

The image-B text/data copy is mapped at `0x10003000`, with the existing
`0x1001651C` data boundary. Known RTC, analog, audio-in and CSI cache MMIO
windows are marked volatile. These windows are analysis classifications, not
claims that every offset is a physically implemented register.

This matters for `gx_audio_in_set_fftvad_curve_1`: the machine code performs
read/write/read/write to `0xA0A00184`. Without volatility the decompiler merges
the updates into one assignment. After the correction, both updates remain.
The corrected audio I2S setter also references `0xA0A00000`, not address zero.

## Evidence and remaining limits

The [harvest report](gx8002-known-function-harvest.json) records revision,
script and analysis-image hashes, load address, and the passing processor
regression. The decompilation files and per-function JSONL are under
`build/gx8002-known-functions/export/`. All 24 named functions decompile;
this does not establish that all their semantics are correct.

Literal-load operands are exposed as scalars by this processor. The preparation
script now defines their read-only pool words, and this harvest explicitly opts
into the decompiler’s read-only memory propagation. A regression check requires
the analog register reference to resolve to `0xA0005088` instead of an unresolved
pool global. Other exporter callers retain their existing options.

Function boundaries, signatures, volatile accesses outside the classified
windows, control-register/DSP instructions, and runtime data require review.
Do not copy these exports directly into a production build. Use the native
C-SKY disassembler and compiled target comparisons to qualify each recovery.
The experimental package continues to contain only the twenty-seven implementations
qualified independently of this decompiler.
