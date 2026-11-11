# Goodix C providers qualified against stock bytes

The canonical source plan now includes three additional exact compiled spans:

| C symbol | Native address | Qualified span |
| --- | --- | ---: |
| `r1_goodix_i2c_close` | `0x509a4` | 12 bytes |
| `r1_goodix_i2c_open` | `0x509b0` | 12 bytes |
| `r1_gsensor_sample_sink_nop` | `0x2adfc` | 2 bytes |

The bus wrappers each include eight instruction bytes and their four-byte
literal. Their qualified Oz bodies recover the existing cached bus cell at
`0x200076cc` and the native registry dispatch entries, then pass full linked
byte equality at the independently named stock address. The sink compiles to
the stock-confirmed two-byte return. No opcode arrays or retained bytes enter
these C providers.

The official `tools/build/qualify_sources.py` evaluated four Goodix source
units under recorded/O2/Os/Oz/Og options: all 20 candidates compiled. The ignored
runner filters only candidate inputs; official native anchors, relocation
matching, scalar binding recovery, linked byte equality and selection logic
are unchanged. The other policy and callback bodies did not qualify. Equal
sizes and behavioral test results were not used as substitutes for equality.

The three selected spans have no overlap with the existing canonical plan.
A merged candidate plan passed the full R1 hybrid build before its exact bytes
were promoted into `tools/build/source-plan.json`. The generated application
is byte-for-byte equal to the 646,408-byte locked official application, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The hybrid report binds the promoted plan's exact hash and identifies each
new span as source-built by the expected provider.

Source-built accounting increases by 26 stored bytes: 18 C instruction bytes
and eight literal bytes. Current coverage is 342 compiled C instruction bytes,
154 source-assembly instruction bytes and 3,265 compiled non-executable bytes,
totaling 3,761 source-built bytes. Resource files supply 248 bytes. The remaining
642,399 bytes are unclassified binary pull-through; they must not all be labeled
executable. This remains a partial hybrid with source completeness explicitly
false, despite equality to the official output.

[Machine evidence](goodix-c-byte-qualification-review.json) binds the qualifier,
scope, selections, canonical plan before/after, sources, hybrid report, coverage
and generated application. The build is `build/hybrid-goal-r1-goodix-qualification`.
Normal composition remains the separately verified 569 R1 units with 197
application and 34 bootloader imports. `make sources-check` and diff whitespace
checks pass; no firmware C changed during qualification.

Final source-only linking, complete native source/byte coverage, physical
Goodix behavior and G2 pseudocode/freeze gates remain outstanding. Qualification
of these spans does not expand earlier bounded behavioral probes or prove
startup/concurrency behavior of their cached state. G2 gates are unchanged.
