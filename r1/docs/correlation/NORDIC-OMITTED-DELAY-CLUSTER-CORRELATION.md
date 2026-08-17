# Nordic omitted delay-cluster correlation

The complete compiler-emitted Nordic nRF5 SDK 17.1.0 microsecond-delay cluster
contains six `nrfx_coredep_delay_us` wrappers and six translation-unit-local
delay arrays. Ghidra exported only the last two wrappers and none of the six
arrays, so ten exact bodies are manual provenance supplements.

| Wrapper extent | Delay-array extent | Wrapper provenance | Registration/call evidence |
| --- | --- | --- | --- |
| `0x0007A6DC..<0x0007A6E8` | `0x0009A640..<0x0009A646` | manual supplement | Thumb pointer at decompressed `0x20007428` |
| `0x0007A6EC..<0x0007A6F8` | `0x0009A650..<0x0009A656` | manual supplement | Thumb pointer at decompressed `0x20007498` |
| `0x0007A6FC..<0x0007A708` | `0x0009A660..<0x0009A666` | manual supplement | `R1PowerEvidence.java` seed; Thumb pointer at decompressed `0x200075E8` |
| `0x0007A70C..<0x0007A718` | `0x0009C790..<0x0009C796` | manual supplement | direct calls at `0x0007B0FC`, `0x0007B18A` |
| `0x0007A71C..<0x0007A728` | `0x0009C7A0..<0x0009C7A6` | Ghidra inventory | four direct calls at `0x00093906...0x00093950` |
| `0x0007A72C..<0x0007A738` | `0x0009D3D0..<0x0009D3D6` | Ghidra inventory | direct branches at `0x0002EB40`, `0x0002EB4A` |

All six 12-byte wrappers have SHA-256
`365d45f07ec7fae67922708c6a9ba072af22db02bb8419756150378123dcbf7d`.
They return immediately for zero; otherwise they multiply microseconds by the
recovered 64 MHz CPU frequency and branch through the adjacent Thumb literal.
All six target arrays contain `03 38 FD D8 70 47` (`SUBS #3; BHI; BX LR`) and
have SHA-256
`583d680532875ef2b855cbedbdfcdbdd74329d19ba88d3e52c36b6b634a75165`.

The closure therefore covers 12 functions / 108 executable bytes: two Ghidra
rows / 24 bytes and ten manual supplements / 84 bytes. Every body routes to
`modules/nrfx/soc/nrfx_coredep.h`; no local busy-wait implementation is
admitted.

Reproduce the body, literal-target, caller, and decompressed-pointer checks
with:

```sh
python3 tools/evidence/summarize_r1_nordic_omitted_delay_cluster.py
```
