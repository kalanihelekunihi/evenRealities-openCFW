# Timer auxiliary ownership and actual allocator sizing

**50 PASS lifecycle comparisons and 38 PASS allocator-size comparisons**, reproduced against locked Apollo instructions and independently compiled C. [Source](../../components/audio/timer_aux_lifetime_offline/aux.c), [lifecycle cases](results.json), [allocator cases](allocator-size-results.json), [bytes/provenance](provenance.json), [disassembly](original-disassembly.txt), [build receipt](reproduction-receipt.json).

## Allocation size correction

Original allocator `0x456110` reads header size 8 at `0x78F118`. Instructions `0x456134..0x456138` calculate extra = `16 - (payload & 7)` and add this to a nonzero payload, with overflow and high-bit rejection. **An 8-byte callback request needs a minimum 24-byte block; a 680-byte queue request needs a minimum 696-byte block.** A remainder of at most 16 bytes is consumed with the whole free block; only a larger remainder is split. These are minimum block sizes, not a physical heap capacity limit.

This explicitly corrects any inference that the prior 688-byte constructed queue block represented the actual result of `malloc(680)`. That older cleanup fixture contained 680 payload bytes, but did not execute this allocation; the task-configuration batch stopped at the request. Prior sealed sources/results remain unchanged. The new 38 cases execute actual allocator arithmetic and allocation for eight payload sizes with four remainders, plus six failure/boundary requests. Boundary cases stop before original malloc-failure hook `0x46D85E`; they do not replace it with a successful/NULL return. Independent C reconstructs minimum-size arithmetic, not the entire allocator.

## Lifetime table

| Resource | Allocation/ownership | Delete wrapper | Deferred daemon |
| --- | --- | --- | --- |
| Timer object | Static ownership in Timer.status bit 1; dynamic object minimum 56-byte block for 44-byte timer | Enqueues command 5; does not clear ID, unlink timer or free object | Original `0x47E97A` unlinks active timer and frees dynamic object; static object retained |
| Callback auxiliary `{callback, argument}` | 8-byte payload; dynamic ownership in Timer.ID bit 0, independently of static timer flag | Original `0x44953E` frees `ID & ~1` immediately after successful enqueue | No additional auxiliary release in this daemon branch |
| Delete queue message | 16 bytes copied by `0x47E7B0`, zero wait in wrapper | Failed enqueue returns -3 and retains auxiliary; successful enqueue returns 0 after release | Message consumed later; no daemon scheduling simulated |

`0x449398` gets Timer.ID, masks bit 0, loads argument at +4 and callback at +0, and calls it. It performs no generation/ownership check. Static analysis of `osTimerNew` `0x4493B0` shows cbMem/cbSize ≥52 can contain inline auxiliary at cbMem+44. cbSize 44..51 can supply a static timer object while auxiliary is dynamically allocated. Thus the two ownership bits must not be conflated. Creation branches are disassembled evidence, not fresh creation tests in this batch.

## Original execution and synthetic interleaving

The 50 lifecycle comparisons vary static/dynamic timer, static/dynamic auxiliary, empty/full/absent command queue, thread/ISR context, and drain/due phase, plus two auxiliary-reuse cases. Actual queue initialization/copy, critical sections, allocation/free, list removal, timer ID access, time sample and selected scheduler suspend/resume peers execute in coherent constructed state. The independent daemon drain is the already sealed timer-command C peer; its historical coverage is not counted again.

After successful delete publication, a dynamically allocated auxiliary is released while Timer.ID and the active timer list still reference it. In a **constructed late-due interleaving**, actual `0x47E88C → 0x47E83A → 0x449398` reaches user callback entry `0x53C2A4` with the old auxiliary argument. Two cases allocate the same 8-byte payload through the real allocator, overwrite it with the same valid callback and a different argument, then reach that user entry with the replacement argument. This establishes software reads/order under the chosen interleaving. It does **not** demonstrate that hardware or the live daemon takes that interleaving; daemon scheduling, command-vs-expiry selection in a live task, actual concurrent reuse and callback body execution remain unverified.

Each drain/due case starts fresh; the tests do not continue a stopped callback into a later daemon iteration. Single-shot, no-wrap timers are tested, with empty pending-ready state and zero modeled task count. Original callback first instruction is an execution boundary, never a stubbed return. Memory, queue/list state, free ordering, callback argument, last tick and critical state are compared. These facts motivate cancellation/quiescence requirements; they do not establish a safe patch or a hardware lifetime failure.

## Remaining concrete dependencies

Trace live daemon expiry-vs-command ordering and scheduler/context switching before claiming runtime reachability. Hardware-stop providers, file-close and encoder setup remain separate available source leads. This batch adds bounded helpers and evidence, not full firmware/source completeness or a byte-identical rebuild.
