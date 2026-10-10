# DSP C kernel lineage and deliberate assembly selection

## Resolved bounded source question

The four authentic C definitions are **already present** in registered NationalChip lvp_kws pin `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`:

- `utility/libdsp/Source/TransformFunctions/csky_radix4_butterfly_q15.c`: forward definition line91, inverse line1005.
- `utility/libdsp/Source/TransformFunctions/csky_split_rfft_q15.c`: forward split line95, inverse split line261.

These are different translation units from the wrapper-only csky_cfft_radix4_q15.c and csky_rfft_q15.c compiled by the predecessor. Undefined references in those wrapper objects demonstrate a missing linked unit in that experiment, not absent C definitions from this SDK. No new duplicate kernel download is required. File hashes are recorded in PROVENANCE.json.

Build recipe explicitly selects assembly: utility/libdsp/Makefile lines310 and321 comment out the C butterfly/split objects; lines326–327 select `Source.asm/TransformFunctions/csky_cfft_radix4_q15.o` and `Source.asm/TransformFunctions/csky_rfft_q15.o`. The corresponding .S files export exactly those four kernel symbols (lines37/275 and37/100). Wrapper objects remain selected at297/319. C shift/copy/fill selections are likewise disabled in favor of assembly. The top Makefile source-build flags include the literal spelling `-DCSKY_SIMID`; the C kernels test CSKY_SIMD, CSKY_MATH_NO_SIMD and endian branches. Treat those separately; do not silently correct a producer recipe.

The C headers explicitly state that butterfly/inverse functions were extracted and renamed from `arm_cfft_radix4_q15.c`, and split functions from `arm_rfft_q15.c`; they retain CMSIS V1.5.1 January2017 and Apache-2.0 notices with T-HEAD2016–2020 adaptation attribution. This establishes declared algorithm/source lineage. It does not imply portable CMSIS C should generate the compact hand-written C-SKY assembly bytes.

## Authentic history evidence

Read-only GitHub official commit-history endpoints for each of the two C paths and the DSP Makefile each return the same single public import `a47076981e6c1ac3b9b1073c3e3e9466d8de7ea8` dated2025-04-27. Its message records updating the SDK from upstream-mainline commit `ec66ba4f101fb8dccf0dfed92a3b0b15402dd44c`; that identifier is a historical reference, not an acquired public source revision. An immutable raw Makefile at a470... was acquired and is byte-identical to the registered current Makefile. The public import therefore already contains the explicit C-disabled/assembly-selected recipe. Public history supplies no earlier producing C configuration for these paths in the returned history. API receipts and the immutable Makefile are retained with hashes; no registered checkout/history was modified.

URLs:
- https://github.com/NationalChip/lvp_kws/tree/8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5/utility/libdsp
- https://raw.githubusercontent.com/NationalChip/lvp_kws/a47076981e6c1ac3b9b1073c3e3e9466d8de7ea8/utility/libdsp/Makefile
- https://api.github.com/repos/NationalChip/lvp_kws/commits?path=utility/libdsp/Makefile&per_page=100
- analogous API paths for the two C source filenames, captured in butterfly-history.json and split-history.json.

Focused primary-source web searches for the exact kernel symbols under official c-sky and T-head-Semi returned no additional source. Existing CMSIS references were deduplicated; no broad toolchain/flag search was reopened.

## What remains and what stops here

Deliberate assembly selection in the public SDK is established; stock matching assembly is already independently rebuilt in the owner evidence. The C alternatives exist and are a distinct implementation path. Whether those separate C kernel units compile or match stock under any configuration was not tested by this source track and cannot be inferred from wrapper-only compilation. There is no evidence that a producing C configuration exists for these particular stock bytes. Consequently further flags are not justified as the explanation for assembly selection. A later finite compiler test may use these existing C files, but that is owner work and is separate from this resolved lineage question. Public history does not expose pre-import SDK lineage; current official documentation describes private LVP GitLab release requiring manufacturer authorization. No private access, code execution, reconstruction, Git index edits, seal changes or new submodule was needed.
