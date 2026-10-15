# Source-compiled memory/string provider candidate

Four unchanged musl v1.2.5 bodies (memcpy, memset, strcmp, strlen) and one R1 EABI
wrapper unit compile to eight entry points with no unresolved references.
The upstream commit is verified against the primary and mirror tag, and every
file and license hash is pinned. See the subset's provenance.json/COPYRIGHT.
The endian header is a narrow target-compiler bridge; vendor bodies are intact.

```
make -C r1 memory-runtime-candidate
make -C r1 memory-runtime-oracle PYTHON=/tmp/r1-source-venv/bin/python
```

All 3,320 comparisons pass, including 1,994 original-code comparisons for
memset, strcmp and general clear. Tests cover memory guards, zero/boundary
lengths, byte truncation, signed/non-ASCII string bytes, unaligned general
copies and aligned EABI copies/clears. memcpy overlap is excluded by contract.
Fault granularity, invalid pointers, EABI register side effects beyond normal
C ABI, exact cycles and original Arm runtime source/instructions remain gates.

The combined board build now consumes these source-compiled objects; its
54-comparison executable links no binary C runtime. Only r1_adc_error and
r1_st25_delay_ms remain undefined in that relocatable component. Other firmware
math/runtime requirements and full image linking remain unresolved.
