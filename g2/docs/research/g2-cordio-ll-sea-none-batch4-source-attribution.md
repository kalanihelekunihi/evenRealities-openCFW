# Apollo `0x5Dxxxx` none-group source attribution: batch 4

Status: research-only, software-only, not production-routed.

Batch 4 resolves the largest next coherent community: 33 census functions /
2,124 bytes from FreeType `src/pshinter/pshrec.c`.  They cover hint and mask
allocation, bit operations, mask merging, dimension state, Type 1/Type 2 hint
recording, and both exported provider-table initializers.

The evidence is an uninterrupted compiled source order with six explicitly
accounted census omissions.  Every claimed body has an authenticated
decompilation signature and an image-body SHA-256.  Distinctive behavior
includes eight-element growth padding, MSB-first masks, ordered mask union and
compaction, the `-21` ghost-stem rule, three-way counter masks, the Type 1
fixed-to-integer path, and exact provider pointer order.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 154 | 25,924 |
| Exact source recovered in batch 4 | 33 | 2,124 |
| Cumulative none-group source | 77 | 9,844 |
| Typed external remainder | 121 | 23,800 |

Six compiled intervals / 304 bytes are absent from the function census:
`ps_hints_t1reset`, `ps_hints_close`, `t1_hints_open`, `t1_hints_stem`,
`t2_hints_open`, and `t2_hints_stems`.  Source order and provider pointers
support those candidates, but the adapter deliberately rejects their
addresses because the authenticated decompiler did not expose complete
function records.  The analyzer pins every interval and reports each as an
unclaimed typed external.

The upstream implementation remains under the FreeType Project License.  The
Apache-2.0 research adapter contains only identity/provider metadata.  No
production component, global census, package, overlay, Makefile, or hardware
path is modified.
