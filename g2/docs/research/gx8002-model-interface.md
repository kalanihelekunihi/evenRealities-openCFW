# GX8002 model task and buffer interface

Date: 2026-09-07. Ten interface functions now compile byte-for-byte identically
to the authenticated primary-image code. They supply 106 bytes from C in the
experimental firmware. This reconstructs the interface, not the model graph,
weights, or NPU instruction semantics.

## Upstream ABI

The C uses the unmodified `include/driver/gx_snpu.h` from NationalChip SDK
commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, compiled with
`CONFIG_ARCH_GRUS=1`. The 32-bit target task is eight words:

| Offset | Field |
| --- | --- |
| 0 | module_id |
| 4 | ops |
| 8 | data |
| 12 | input |
| 16 | output |
| 20 | cmd |
| 24 | tmp_mem |
| 28 | weight |

The verifier authenticates the header Git blob and pins its hash in the
[report](gx8002-model-interface-verification.json). A target static assertion
requires the 32-byte ABI. Corresponding SDK `ctc_model.c` functions provide
names and field roles; the actual firmware instructions establish this
configuration's values and addresses.

`LvpCTCModelInitSnpuTask` sets module ID 256 and copies ops/data/cmd/tmp/weight
from the saved task at `0x2002E85C`, masking each pointer to 28 bits. This agrees
with the SDK's `MCU_TO_DEV` conversion. Input and output fields are preserved.
Saved-task reads are explicitly volatile to preserve the decoded access order
under this compiler. The emitted function, including its pointer literal,
exactly matches all 56 original bytes.

## Recovered interface values

| Query | Result |
| --- | ---: |
| Command bytes | 9,164 |
| Weight bytes | 120,800 |
| MCU operation bytes | 0 |
| Working data bytes | 13,056 |
| Temporary bytes | 4 |
| Feature-value count | 520 |
| Feature buffer offset | 0 |
| State buffer offset | 1,040 |
| Output buffer offset | 8,464 |

Offsets do not establish the complete tensor layout, state partitioning,
quantization format, output interpretation, or training provenance. No opaque
model arrays are introduced. The retained saved-task copy wrapper and its
callers remain separate reconstruction work.

## Qualification

`verify_gx8002_model_interface.py` compiles the C on macOS, requires exact
stock bytes at ten reviewed offsets, rejects undefined symbols/relocations,
and checks section alignment. Alignment gaps are excluded rather than counted
as code. Host tests verify all queries and 2,048 task translation cases,
including source/destination aliasing and preservation of input/output fields.
The host structure follows its host pointer width; exact target compilation
and the target size assertion qualify the firmware layout.

During investigation, raw-binary GNU disassembly required explicit ELF
C-SKY ABI flags `0x21006009` to decode 32-bit instructions correctly. The
analysis-only ELF was generated under `build/`; it does not supply firmware
bytes. The final qualification compares the compiler's normal ELF sections
directly with the authenticated original.

The codec now contains 1,054 compiled C bytes, 80 generated metadata bytes,
42 generated fill bytes, and 324,916 retained stock bytes. Since these new
functions are byte-exact replacements, the candidate package hash is unchanged.
Package verification still does not establish source-only completion or
whole-device operation.
