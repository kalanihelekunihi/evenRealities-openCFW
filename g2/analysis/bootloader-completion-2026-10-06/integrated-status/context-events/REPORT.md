# Asynchronous IOM publisher, service and ownership

Reconstructed source/header: `g2/components/bootloader/initializer_callbacks/context_events.c` and `context_events.h`. Locked bootloader SHA256 f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5, load0x410000. [Authentic disassembly](original-disassembly.txt); [seven-function ownership ledger](../context-events-ownership-92619e.json). All seven bodies are retained in immutable source image92619ea6a92780848703d61cb91385c950b717089718aa6a82a13baf6fc1cda4. This is bootloader IOM/CQ analysis, not an assertion about application BLE/ring transport.

## Recovered interfaces and state

| Address | Behavior | Original instruction bytes |
| --- | --- | ---: |
|42c45a..42c4c6|Publish next descriptor to ordered registers|108|
|42c6f8..42c980|Descriptor/CQ completion and error service|648|
|42c076..42c0b2|Classify supplied events OR hardware status|60|
|42c0b2..42c222|FIFO drain/recovery and interrupt restoration|368|
|427a56..427ad6|Snapshot CQ indices and three flags|128|
|427b38..427baa|Find/patch resume command and clear CQ enable flag|114|
|427754..427794|Refresh completed index/current head under PRIMASK|64|

These1490 mapped instruction bytes are all visited across515 bounded comparisons, not every possible input or interleaving. Consolidated symbol ends for CQ status/resume were undersized; the authenticated return instructions at427ad4/427ba8 establish the actual ends above. Scalar pools following service42c980 are excluded from code ownership.

| Context offset | Recovered meaning |
| --- | --- |
|+4|Module; register base40050000+(module<<12)|
|+14|Saved interrupt enable word|
|+18|Accumulated descriptor event bits|
|+1c|CQ completion counter; low8 bits select callback slot|
|+24|CQ pending count|
|+28|256 serialized callback addresses|
|+428|256 corresponding callback context words|
|+828|Generic CQ handle|
|+82c byte|Value2 retains ordinary CQ callback pointers|
|+834 byte|Stop processing marker; service resets it after successful CQ snapshot|
|+83c byte|Descriptor mode active|
|+840|Descriptor pending count|
|+848|Descriptor capacity|
|+850|Descriptor completion/head counter|
|+854|Pointer to32-byte descriptor records|
|+864|Recovery-delay multiplier; configuration stores floor(1000000/clock_hz), or0|

Descriptors contain six register values followed by callback address/context, both32-bit CPU words. Publisher selects `(head+1)%capacity`, with wrapping32-bit arithmetic, then writes registers+128,+2c4,+218=0,+21c,+220,+218,+120 in that order. It neither advances head nor copies payload memory. Capacity0 behavior was tested with DIV_0_TRP clear; it is not a valid-capacity guarantee.

## Service call flow

Handle NULL or invalid magic returns2. Descriptor mode accumulates incoming events. With accumulated0x801 and either inactive DMA-enable bit0 or events0x4e7c, it advances head and decrements pending **before** calling the completed record's callback. Classification priority is0x6c→0x08000000, bit0x200→0x08000001, bit0x10→0x08000002, bits0x4800→1, otherwise0, after OR with status register+204. Descriptor callback/context are read again for the actual call; callback pointer is cleared after return. Descriptor mode ignores ordinary CQ retention mode2 for this clear.

Error bits0x4a7c clear DMA enable, zero trigger+224 and call recovery. Remaining pending records trigger publication of the next record after clearing accumulated events. Empty descriptor state clears active byte+83c, masks enable register withfffffbfe and writes800000 to+238. There is no pending-underflow guard.

Ordinary CQ mode snapshots indices, resets stop byte+834, then advances the completion counter and decrements pending for each completed slot. Callbacks receive(context,0). Their pointer is cleared **after return**, unless mode byte+82c is2. Callback changes to mode/stop metadata are reread; callback replacement in a mode other than2 can be overwritten by the post-return clear.

With error bits0x4a7c and no stop marker, another slot is advanced/decremented and its callback receives the classified status. Service then clears CQ/DMA enable bits, zeros trigger, applies recovery, patches resume, and enables CQ again if pending remains. Empty CQ disables the adapter and restores interrupts by writing enable0, clear-all, saved-enable. Callback stop metadata is not a standalone persistent cancellation protocol: entry resets that marker after a successful snapshot.

Recovery disables interrupts temporarily, can spin while waiting on FIFO/status, optionally resets interface control around delay argument `6*context[864]`, clears pending interrupts and restores the previous enable. Direct tests cut delay and supply finite FIFO/status transitions; elapsed time and physical peripheral progress are not established. Resume walks a finite command chain in tests, follows link commands or advances8 bytes, patches the command whose target matches the index register, writes the new head and clears CQ flag bit25. It has no scan bound and frees no memory.

## Ownership conclusions

| Operation | Proven effect | Remaining boundary |
| --- | --- | --- |
|Publish descriptor|Read six words into registers; no allocation/copy/free|Actual DMA payload-consumption boundary|
|Completion callback|Head/count already changed; callback sees context/status|Real callback body and its alloc/free effects|
|Descriptor completion|Callback pointer cleared after return; context and record retained|Who owns/reuses descriptor/data storage|
|Ordinary CQ completion|Pointer cleared after return, or retained when mode2; context retained|Submission/reuse contract|
|Error recovery/resume|State/MMIO recovery and command patching|Hardware abort/quiescence and cancellation safety|
|Service itself|No heap allocation/free call in recovered family|Callbacks can perform additional work; true uninitialize/release is separate|

Queue-full rejection and allocation failure are producer/initializer behavior, not service guarantees. Pending256 was included in ordinary CQ fixtures, but the service has no capacity rejection. No speculative release/clamp was added. Earlier semaphore failure free behavior does not imply any IOM record/buffer release policy.

Synthetic descriptor callback reentry with pending1 matches stock: outer completion makes pending0; nested service, while descriptor mode is still active, advances again and wraps pending to0xffffffff. Head becomes2; pointers for records1/2 are0. Ordinary CQ reentry drains three slots and clears their pointers. These execute original/source service instructions through a synthetic call stub. They do **not** show that stock callback bodies or hardware scheduling create these situations.

## Validation and reachable routing boundary

[505 principal comparisons](../context-events-92619e.json), [10 additional guard/flag/index comparisons](../context-events-guards-92619e.json),740 IOM child regressions,12 native semaphore heap cleanup regressions and2 conditional subtype cases PASS. Same-image normal2/malformed3/interruption2 cases PASS;355 alignment mappings pass and known bad placement is rejected.581 frozen files/144 objects remain unchanged. Synthetic callback bytes are excluded from original instruction coverage. Fresh emulator instances isolate independent fixtures after a persistent-CPU callback-mode mismatch; no firmware behavior change was made to address that harness condition.

Seven-case startup has no asynchronous IRQ delivery: its observed instruction footprint remains35468/148599 (23.86826%). Union with515 asynchronous direct traces gives37026 unique original bytes with **additional** callback/delay/FIFO assumptions; that is still not source completeness or whole-firmware coverage.

A verified stock call site is430636 inside IRQ wrapper430610..43063c. It loads module4 transfer handle from200003b8 (base20000374+44), gets enabled-only interrupt status through42c672, exits on failure/zero, clears it through42c6b6, then calls service42c6f8. IRQ wrapper, status-get, clear and vector delivery are not yet source-linked/recovered in this batch. They are the next reachable closure before interpreting an app-facing asynchronous path. Descriptor registration430280, submission/full/allocation paths, true uninitialize/release and wider scheduler/lifecycle gaps remain open.
