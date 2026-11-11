# R1 BAE8 service and link-context state in C

The existing `native_bae8_context.c` unit now supplies one shared
`r1_native_bae8_service` object, its link-storage descriptor and its three
four-byte link contexts. This resolves the service import used by both the
priority-2 BLE observer table and the notification sender. The lookup's code
and relocations are unchanged from the [lookup review](bae8-context-c-review.md).

## Stock state and ownership

| Object | Native address | Bytes | Initial state |
| --- | --- | --- | --- |
| Service | `0x20006504` | 48 | Forty zero prefix bytes, descriptor pointer, zero callback slot |
| Link-storage descriptor | `0x20006534` | 8 | Pool pointer, capacity 3, zero padding, size 4 |
| Link contexts | `0x200086e4` | 12 | Three zeroed four-byte slots |

The native priority-2 table at `0xc4598` contains the BAE8 record at
`0xc45b0`, with handler `0x52b21` and context `0x20006504`. The service's
descriptor pointer occupies offset 40, and the callback slot occupies offset
44. The prefix remains opaque; this change does not invent field meanings.
The descriptor starts immediately after the 48-byte service allocation.

Both authenticated scatter descriptors were executed against poisoned RAM:
RW decompression at `0x286f4` and zero initialization at `0x3bc68`. Guards
survived both operations. The linked C owner bytes, including both relocated
pointers, match the resulting 68 native bytes. REA reads of the observer and
scatter tables match the locked application. The test link places objects at
native addresses to establish this comparison; it is not a final firmware link.

## Runtime and build checks

The actual production observer table, C sender, C context lookup, and compiled
SDK connection index/validity functions are linked together in the replay.
The sender receives the service pointer read from the actual table. In 5,184
paired executions, stock and C match status, flag queries, HVX parameter bytes,
length storage, service, descriptor and pool state. Cases cover valid and
invalid/wide handles, both notification selectors, zero/nonzero client flags,
lengths 0/244/245, HVX statuses 0/19/8, service-handle mutation during connection
lookup, and both PRIMASK states. The current lookup object separately passes
the prior 11,520 descriptor/alias/mutation replay cases.

Four negative controls reject capacity two, stride eight, a missing descriptor
pointer and an initially nonzero callback slot. The stock initialization
comparison rejects these controls before runtime acceptance.

This is bounded behavior evidence. Flag lookup, zero-fill, log mode zero and
SVC174 are modeled. Native sender provider depths are 112 bytes at the flag
query and 88 at HVX; the existing C sender uses 88 and 64 respectively. These
frames are recorded, not treated as equal. Private spills, nonargument register
state, APSR, timing, nonzero logging modes, observer execution, interrupts,
controller behavior and physical BLE operation are outside this replay.

`build/sources-goal-r1-bae8-state-c/report.json` reports all 591 units compiled
and composed without failures or duplicate strong symbols. Application imports
fall from 156 to 155; bootloader imports remain 34. The manifest and the other
590 objects are unchanged. Existing allocated sections and relocations in the
changed unit are unchanged; only three owner sections were added. `make
sources-check` passes with 395 R1 source files.

Qualification compiled the unit but selected no exact regions. The canonical
source plan is unchanged. A fresh hybrid build retains application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and totals of 4,269 source-built, 641,891 binary-pull-through and 248 resource
bytes. Full C source completeness and byte-identical source reconstruction
remain unproven. The subsequent [raw-observer review](bae8-observer-c-review.md)
supplies dispatch and credit handling in C; its event-handler bodies remain work.

The [receipt](bae8-state-c-review.json) records current object hashes, REA
provenance, initialization, replay, negative controls and build audits.
Reproducible probes are under ignored `build/goal-r1-bae8-state-c/`.

The newer [typed SDK call review](radio-sdk-c-review.md) reruns these regressions
while replacing handwritten radio supervisor-call wrappers.
