# YHM2710 C providers qualified against stock bytes

The canonical source plan now includes three exact compiled YHM spans:

| C symbol | Native address | Qualified span |
| --- | --- | ---: |
| `r1_yhm_transport_acquire` | `0x50608` | 12 bytes |
| `r1_yhm_transport_release` | `0x507a0` | 12 bytes |
| `r1_yhm_block_word_set` | `0x5083c` | 12 bytes |

Each contains eight instruction bytes plus a four-byte literal. The Oz bodies
preserve the existing YHM context address, accessed device/callback field and
native registry dispatch boundary where applicable. Full linked bytes match
the independently named stock spans; no opcode arrays enter these providers.
The IRQ registration routine remains unqualified.

The official qualifier compiled all five Clang configurations (recorded, O2,
Os, Oz and Og). Its runner filters only candidate source inputs; named anchors,
relocation recovery, binding checks, linked equality and selection are unchanged.
A separate pinned GNU GCC 9 check compiled four configurations with no additional
matches. Its Oz configuration failed because that compiler does not support Oz;
this exploratory failure is retained in evidence and does not affect the normal
source-build result or the accepted Clang selections.

The selected spans have no overlap with the prior canonical plan. A merged
candidate plan passed the complete R1 hybrid build before the exact merged plan
was promoted. The generated 646,408-byte application remains byte-for-byte equal
to the locked stock application, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The hybrid report binds the promoted plan hash and verifies the expected source
provider for each new span.

The 36 added source-built bytes comprise 24 C instruction bytes and twelve
literal bytes. Current source-built accounting is 3,815 bytes: 384 compiled C
instruction bytes, 154 source-assembly instruction bytes and 3,277 compiled
non-executable bytes. Resource files supply 248 bytes. The remaining 642,345
bytes are unclassified binary pull-through, not all proven executable bytes.
Source completeness remains explicitly false despite exact hybrid output.

[Machine evidence](yhm-c-byte-qualification-review.json) binds both qualification
runs, compiler failure, scope, selected spans, canonical plan before/after,
source/state/registry files, hybrid report, coverage and application output.
The build is `build/hybrid-goal-r1-yhm-qualification`. Normal composition remains
the separately verified 571 R1 units with 197 application and 34 bootloader
imports. `make sources-check` and diff whitespace checks pass. Firmware C was
unchanged during this qualification run.

[Bounded callback behavior](yhm-c-callback-registration-review.md) remains a
separate evidence scope. Concrete callbacks, concurrency and electrical IRQ
validation, unqualified source implementations, complete source-only linking
and byte coverage, and G2 corpus gates remain outstanding.
