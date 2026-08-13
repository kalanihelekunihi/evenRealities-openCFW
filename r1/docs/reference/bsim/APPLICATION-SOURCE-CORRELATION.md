# Application-to-SDK source correlation

This records a Ghidra BSim comparison between the SHA-pinned R1 application
`2.2.6.0009` and the symbol-bearing Nordic nRF5 SDK 17.1.0 secure bootloader
reference. The reference is not claimed to be the original application build; it
is a provider corpus compiled with Arm GCC 9.3.1.

The run's raw artifacts -- the comparison CSV, the Ghidra logs, and the generated
hash record -- are regenerable tool output and are not tracked in this repository.
Their pinned hashes are reproduced below so a fresh run can be checked against
this one.

## Result

- application image: 646,408 bytes at `0x00027000...0x000c4d07`;
- recovered application inventory: 2,687 functions;
- signature-bearing application functions: 2,648;
- reference functions in `0x000f8000...0x000fdfff`: 319;
- candidates retained per application function: 12;
- raw comparison rows: 31,776; and
- sole signature-generation failure: `0x000979dc`, whose manually recovered,
  compile-checked semantic body remains in the decompilation corpus.

The raw correlation CSV is candidate evidence, not an automatic name map. Perfect matches among tiny wrappers are frequently
non-unique: the first review found 39 unclassified functions with similarity 1.0,
including constant-setting product wrappers that clearly do not implement the
suggested SDK symbol. A provider attribution therefore still requires distinctive
constants, complete semantics, source diagnostics, or corroborating call topology.

## Input and output pins

| Artifact | SHA-256 |
| --- | --- |
| R1 application | `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a` |
| Nordic SDK reference ELF | `f105f2392c557805c93c4feb721a31449c398c044d7c410ce06c503dd3d764d3` |
| raw correlation CSV | `6dea8106e8965d038976cd2e380af41f9121ed625d5bdb2bc62a36841612c535` |

Reproduce the comparison after building the documented SDK overlay with
`run_r1_application_source_correlation.sh` from the upstream research workspace
(see [Analysis tooling](../../README.md#analysis-tooling)), passing the built
`nrf52840_xxaa_s140.out`.

The runner seeds all exact recovered application entries before analysis, so indirect-only
and optimized tail-entry functions are included instead of depending on a single discovery pass.
