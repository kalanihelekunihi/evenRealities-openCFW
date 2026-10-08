# Touch application callback and TX ownership

The locked touch application uses one static borrowed RX buffer (`0x200009a0`,16 bytes), one static TX buffer (`0x200009b0`,16 bytes), and context `0x200008ec`. Initializer `0x3678` registers event callback `0x3701` at context offset68, enables SCB1 (`0x40250000`) and IRQ7. Public PDL source is pinned in the preceding dependency-followup directory; compatible behavior does not establish the exact producing revision.

New independent C is `app_event.c` (bounded callback) and `report_publish.c` (internal publish slice); declarations are in `ownership.h`. The combined standalone source ELF is `eda59289afb08947773a6b7ba1d40b59985926cb4dd1d7042a4100cfd1740ea1`. Build receipt and authenticated original instruction ranges are included. No module was installed into the accepted 242-object bootloader checkpoint, a touch firmware image or the production payload.

## Recovered callback flow

`0x3700`: write-complete event0x20 reads the low8 bits of RX index. With no error0x40, count1..16 and opcode0..8 it enters the nine-entry table at0xb0c4. Actual `mov pc,r3` is an in-frame branch; decompiler function-call notation is misleading. Table entries: 0→370e,1→3746,2→382c,3→370e,4→384c,5→37a0,6→3766,7→37c8,8→3780. Existing interpretations call2 DFU,4 sensor report,5 save baseline,6 read baseline,7 gesture config,8 threshold read; this batch proves the indices but does not newly execute those bodies.

Opcode1 writes raw prefix `02 02 00 01`, leaves12 remaining TX bytes intact, and arms16-byte TX. No version-unit interpretation is imposed. Commands0/3 use fallback. All bounded write-complete paths then rearm RX16, including error cases. Read-complete0x10 fills TX16 with0x5a, rearms it and writes GPIO P4 DR_SET at0x40040440 with1, releasing active-low attention. Other event bits are ignored by these observed callback paths. With both completion bits, write handling precedes read handling.

`app_event.c` deliberately excludes valid commands2/4/5/6/7/8; a test guard rejects entry outside its contract. It is not a drop-in full callback implementation. RX index257 truncation is a raw-callee test, not proof of hardware count overflow.

## Ownership and publication

| Stage | Proven static/instruction behavior | Ownership implication |
| --- | --- | --- |
| Initial configuration | Caller pointers stored, TX size/index/count set; RX size/index set | Borrowed RAM; no allocation/free/ownership transfer in these APIs |
| Report production | Report at0x20000990 copied16 bytes into same TX buffer, descriptor rearmed, P4.0 DR_CLR asserted | Second producer shares callback TX storage |
| FIFO feeding | Driver copies bytes to FIFO, advances pointer/index, reduces remaining size | FIFO progress is distinct from completed host transfer |
| STOP/read completion | Driver derives transferred count from index minus FIFO/shift-register occupancy, returns idle, calls registered callback | Count is available at callback entry, before application rearm |
| Application read completion | Callback replaces contents with0x5a and rearms, resetting index/count | Deferred consumers must snapshot needed data/count before reuse |
| Reconfiguration | Descriptor stores are separate instructions | New thread-side buffer swaps require serialization with IRQ and producers |

The report publish slice `0x3c18..0x3c36` copies three loaded words followed by a fourth, calls real stock TX-arm0x9ad8, then asserts attention. Its independent source executes public descriptor-arm code. The slice excludes report construction, logger and subsequent application-state writes. `touch_product_09b4_run` at0x3cb4 enables interrupts and invokes report_builder at0x3d4c and0x3df2 after its sleep critical section exits. Neither publish slice nor descriptor setter supplies local exclusion; earlier children and physical IRQ state are not asserted globally. Main-loop report copies and IRQ callback copies therefore need an explicit ownership protocol in a future redesign, rather than relying on the descriptor API to make them atomic.

## Fresh validation

The combined standalone ELF was freshly tested: **336** callback comparisons; **96** actual IRQ/helper/registered-callback comparisons with no helper cuts; **32** actual internal publish-slice comparisons. Callback tests cover completion/error combinations, count boundaries and commands0/1/3/9. The composed suite compares full context and buffers, ordered events, SP and PRIMASK; only the registered code-pointer word is normalized. Example: seven bytes enqueued with three still in FIFO yields transferred count4 at callback entry; rearm subsequently zeroes counters. Synthetic FIFO occupancy and W1C register behavior are explicitly modeled.

A separate control/injection test pauses the descriptor setter after its pointer store and manually invokes the actual IRQ before size/index stores. New storage of capacity2 with old remaining16 permits eight synthetic FIFO copies: six guard bytes change. The resumed setter leaves an advanced pointer with reset count/index. Control without injection preserves guards. This is a constructed interleaving in a guest, **not physical exception preemption or proof of stock corruption**. Stock buffers here remain fixed16-byte storage. IRQ latency, host interleavings, heap lifetime and hardware fault manifestation remain unverified. Two callback mutants (ignore error/omit RX rearm) are rejected.

## Practical requirements and next boundary

CFW/application changes must preserve borrowed-buffer validity, serialize descriptor updates and content publication, snapshot completion metadata before rearming, and retain attention ordering. An owned-buffer design needs both descriptor and producer coordination; merely copying an input pointer is insufficient. An epoch check alone does not make these multi-store updates atomic. No firmware patch or memory-management change is proposed as safe from synthetic evidence alone.

Unexecuted command bodies2/4/5/6/7/8 and actual host/NVIC traces are separate remaining leads. Physical scheduling requires a trace of IRQ7, PRIMASK, report publication and host reads, or a faithful peripheral/exception simulator. Public-source behavioral compatibility and exact compiled attribution remain separate; this batch adds behavior tests, not exact callback-byte attribution or whole-image coverage.

All110 sealed audit inputs remain unchanged. Prior checkpoint, shared campaign, firmware and Git index were preserved.
