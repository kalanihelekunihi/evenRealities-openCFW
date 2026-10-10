# SmpHandler isolated C candidate

Handwritten source-defined dispatch candidate for authenticated stock main
`0x537d0c..0x537e9e` (exclusive end). `g2_candidate_smp_handler` uses explicitly
supplied providers and literal values. It is isolated from the firmware build.
Caller event/message shape follows the authenticated SDK's `SmpHandler(0,
pMsg)` call and is independently bound to stock r1 message loads. The stock
body ignores r0's incoming event value. The candidate returns void.

The message and connection control block are readable byte storage with
observed offsets; the callbacks own full allocation, lifetime, connection
lookup, logging, database and state-machine contracts. Connection lookup must
provide valid readable storage through byte65, including the closed-connection
case. There is no invented null-CCB behavior. CMAC pointer words and queued
message addresses remain 32-bit words, allowing the provider to resolve them
on a native host. The handler does not own these buffers.

Providers required (11 unique call targets; 24 call sites):

| Callback | Stock target | Observed contract |
| --- | --- | --- |
| database_service | 0x542960 | Database event32 service |
| buffer_free | 0x5304d4 | Free nonzero CMAC message+8 pointer |
| ccb_by_id | 0x5375fc | Message param low byte to readable CCB |
| state_machine | 0x56ee62 | CCB and unchanged message |
| log_gate | 0x4c9c50 | Observed carry r0; returned value controls branch |
| compare | 0x44b610 | Two pointer words and length; zero means match |
| log_flags | 0x43d0ce | Bit1 controls extended log emission |
| log_extended | 0x43d574 | Four register arguments plus four stack words |
| log_fallback | 0x52a63c | category, format, token, message status |
| message_dequeue | 0x4bf9ec | AES queue pointer, in/out handler ID; zero empty |
| message_free | 0x4bf9b0 | Free each dequeued message address |

Literal values are read/authenticated in the validator from stock literal
slots 0x537ea0, 0x537eb0, 0x537eac, 0x537ee0, 0x537ee4 and 0x537ee8. Embedded
inline-data addresses 0x537eb4, 0x537eb8 and 0x537ec0 are data identities passed
to providers, not executable byte arrays. Relocatable production data mapping
remains integration work.

Run `sh g2/analysis/smp-dispatch-candidate-20261010/build.sh` at repository root.
The build emits a Cortex-M55 freestanding object and a native shared library.
Only source list: this directory's `smp_dispatch.c`. Exported namespace:
`g2_candidate_smp_handler`; helper symbols are static. No undefined external
functions are linked into the object because provider calls are explicit.

Validation and finite boundaries are in
`g2/analysis/smp-dispatch-candidate-20261010/REPORT.md`.
