# Output GPIO C adapter qualification

Five existing pure-C table adapters now supply their native six-byte regions:

| C function | Native entry |
| --- | --- |
| `r1_output_gpio_driver10` | `0x54d8c` |
| `r1_output_gpio_driver0c` | `0x54d92` |
| `r1_output_gpio_high` | `0x54f3c` |
| `r1_output_gpio_low` | `0x54f42` |
| `r1_output_gpio_toggle` | `0x54f8a` |

Each loads the pin word at record offset 8 and tail-calls the corresponding
Nordic GPIO/GPIOTE implementation. No firmware C source, manifest or assembly
was changed for these admissions. The complete official scatter loader was
executed again against the locked application; its initialized output table
independently identifies these five entries. Fresh REA observations confirm
their bodies and call targets.

The frontier gains nine observed manual entries and updates one previously
unrouted GPIO helper: the five table adapters and five GPIO/GPIOTE targets
needed to describe their source routes. These are inventory supplements and
bounded contracts, not complete pseudocode/source readiness certificates.
The qualifier now includes named frontier supplements when validating recovered
branch targets; small table-referenced thunks absent from the decompiler's
function CSV no longer disappear from that check. Unnamed targets still fail.

All 440 stock/C comparisons pass through the actual Nordic implementations.
Cases cover five adapters, two record pointers, representative pins on both
ports and four initial OUT patterns. The peripheral model applies OUTSET/OUTCLR
to ordinary-memory OUT. Tests compare the complete ordered GPIO reads/writes,
final register memory, untouched record storage, R4-R11, SP and interrupt masks.
No GPIO provider stub substitutes for the real code. Physical electrical
behavior, invalid-pin faults and unrelated volatile register/private-stack
residue remain outside this void-interface proof.

Official qualification compiles all three relevant source units and selects
only the five table-adapter bodies. All 30 targeted qualifier checks pass,
including altered instructions, removed named targets, instruction-as-literal
misclassification and unsupported branch addends. Four wrappers depended on
manual helper entries absent from the raw decompiler inventory. The existing
19 build-tool tests also pass.

The canonical plan appends only those five official selections: 30 additional
source-built bytes. Existing plan units remain intact. The candidate-plan
hybrid application retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Its plan hash matches the promoted canonical plan. Source-built content is now
3,691 bytes, with 642,469 retained bytes and 248 resource bytes. The helper
implementations are not newly byte-qualified by this adapter admission; hybrid
equality does not establish a complete source-only rebuild.

The unchanged full R1 source report has 562 compiled units, zero failures or
duplicate strong symbols and 210 application / 34 bootloader imports. Source
checks pass and G2 remains `P2_INTERRUPTED` with no gate advanced. Exact table,
source, REA, compiler, qualification, negative-test and hybrid bindings are in
the [machine-readable review](output-gpio-c-driver-review.json).
