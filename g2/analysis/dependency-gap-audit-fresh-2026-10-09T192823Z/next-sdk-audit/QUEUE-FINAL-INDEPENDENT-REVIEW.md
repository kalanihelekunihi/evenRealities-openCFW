# Queue ABI and finite FDNB stopping boundary

All 18 independent static checks PASS in QUEUE-FINAL-INDEPENDENT-VERIFICATION.json, reproduced by verify_queue_final.py. Four complete image extents and serialized listing bytes match the locked input. Transaction arguments, field offsets, masks, conditional branch and three BL targets were independently checked. No firmware execution, extraction, canonical admission, source, index, pin, Git or device changes occurred.

## Candidate correction

My prior FDNB lineage review proposed 55CC1C–55CF2E as a possible ordinary nonblocking entry, pending body classification. It is now resolved as ordinary BLOCKING transfer. Both 55CC68 and 55CF80 pass r2=1 to the validator at 55C1E0. Polling, saved interrupt enables and restoration support that role. The earlier candidate must not remain an open nonblocking lead. No authenticated ordinary nonblocking entry emerged from this scoped search.

## Offsets and reachability

The validator retains the transaction in r5 and blocking flag in r7. At 55C25E it truncates the flag to a byte; the nonzero branch at 55C262 reaches successful return at 55C280. Only blocking=false reaches the pause byte read at transaction+36 and status word read at +40. The masks are E0 and 00E0E0E0. A byte read is sufficient to test the low reserved bits of a declared 32-bit field; it does not establish byte-sized storage.

Application 52DF50–52E058 builds a transaction at sp+8. Its stores to sp+44 and sp+48 establish transaction offsets +36/+40 independently of the 48-byte initialization size. The caller passes this pointer and wrapper handle to blocking full-duplex provider 55CF40. Both known validator callers bypass the queue checks. Initialized fields therefore do not establish an actual queued transaction or execution of their validation.

## Three source candidates

The observed offsets fit the registered pre-FDNB source and public TX-DMA/RX-IRQ source. They exclude only the conditional SDK layout where a four-byte eFdnbMode shifts queue fields to +40/+44. With short enums, that field can occupy former padding at +35 while queue offsets stay unchanged. Neither the direction-byte access nor total size proves enum allocation. Producer enum, packing and alignment options remain unknown.

The selected stock interrupt service lacks the active-FDNB prefix required by both newer source service bodies. That excludes those unchanged paths in this provider, not unused or separate APIs, private patches, inlining or other images. The blocking full-duplex source body is identical across inspected old/new inputs and cannot choose a producer revision.

## Bounded stop

The metadata hash and 7,449 records were verified. Its two direct validator callers agree with authenticated BL targets. The owner's 25-record IOM island search is an explicit scope, not a complete callgraph. Indirect calls, unrecognized functions and other payloads remain outside it.

No actual unresolved address-bound ABI discriminator remains from this candidate: the proposed caller proved blocking, the offset check is complete, and the three source lineages have bounded local results. Stop the 12-fixture proposal unexecuted. Reopening requires a separately authenticated FDNB entry/caller, new target evidence, or producing configuration for a specific ABI question. There is no justified additional download, compiler sweep or broader IOM hunt here.

This closes the selected FDNB shortcut goal. It does not establish global API absence, whole-firmware source completeness, byte identity or universal public-source exhaustion.
