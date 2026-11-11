# QMA step configuration in C

`r1_qma_steps` now uses ordinary C instead of naked assembly. Stock entry
`0x87250` writes `13=80`, delays one unit and writes `13=7f`. When disabled
it returns that last write's full result without accessing chip ID.

When enabled, the live ID selects three writes:

| ID | Register `0x12` | Register `0x14` | Register `0x15` |
| --- | --- | --- | --- |
| `0x90` | `0x89` | `0x0b` | `0x0c` |
| `0xfa` | `0x89` | `0x0b` | `0x0e` |
| Other | 0 | 0 | 0 |

The routine reads register `0x1e` into a zero-initialized byte, masks it
with `0x3f`, stores that byte and writes it back. It then reloads the live
ID. ID `0x90` writes `1f=a9`; ID `0xfa` writes `1f=aa`; both return that
write's full result. Other final IDs return the ID byte itself. Read and
earlier write statuses are ignored. REA/Ghidra confirms the flow but
infers a void return; instructions and execution establish the return
paths described here.

Stock/source comparison passes 3,584 scenarios. Coverage includes every
initial/final ID and read byte across the matrix, disabled/nonzero enable
values, non-writing reads, full-width helper results and interrupt masks.
The initial ID is changed by a callback before the first lookup, and the
final ID is changed during write-back. A retained read pointer observes
the masked scratch byte before write-back, proving that store remains
visible. Probes independently check the complete call plan, both live
ID reads, arguments and return path, then compare ordered accesses,
state/guards, callee-saved registers, restored stack and masks. Mocked
calls clobber caller-saved registers/flags and require eight-byte alignment.

The C body is 152 bytes versus 144 stock bytes. Every other configuration
function retains its previous instruction body. All 562 R1 units compile
without failures or duplicate strong symbols in
`build/sources-goal-r1-qma-steps/report.json`; imports remain 227 application
and 34 bootloader.

Only the initialized read byte is owned, not surrounding saved-register
bytes. Controlled state placement does not prove final layout. Physical
step-counter operation, timing, complete fault state, final linking and
byte identity remain unverified. No source-plan selection or G2 workflow
gate changed. [Machine-readable evidence](qma-c-steps-review.json) binds
source/build/native hashes, REA observations and ignored probes under
`build/goal-r1-qma-steps/`.
