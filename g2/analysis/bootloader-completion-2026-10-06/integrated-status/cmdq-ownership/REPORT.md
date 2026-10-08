# Reachable CMDQ submission, cancellation and termination

Locked bootloader SHA256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, load0x410000. Shared image `4f111ccb9ed4131499a99a47af126d83f4b56f8abb54a5e6073cbc6566e93e8a` passes all seven integration cases and affected regressions. This family already has reconstructed source; this batch establishes callers and directly tests ownership paths instead of adding duplicate implementations.

## Actual callers and scope

Instruction addresses425d8a/425e26/425fda call reserve42790a;425dd2/425ea6/4260dc call post4279f0;425de8/425eba/4260f0 call cancel4279be. These reside in reconstructed MSPI control-request transaction handlers, not IOM-island TX submission. MSPI CQ termination wrapper423f64 calls generic term427ad6 at423f7a. Reconstructed source is `g2/components/bootloader/nor_mspi_init/control_request_transactions.c`, `control_request34.c`, `control_request_helpers.c`, and `nor_mspi_queue/queue_descriptors.c`/`nor_mspi_queue.c`. Exact instruction excerpts are in original-disassembly.txt. These direct edges do not prove every dynamic caller or all shutdown paths.

The retained IOM island42c034..42cdb0 has18 accounted bodies/3424 instruction bytes plus28 literal bytes. No standalone IOM nonblocking submit, full-pending gate, disable or uninitialize body remains there. Generic queue APIs must not be mistaken for an independently recovered IOM uninitialize path, nor should absent vendor SDK functions be fabricated.

## Concrete ownership transitions

| Operation | Proven transition | Meaning and limit |
|---|---|---|
| reserve42790a | Requires producer==reservation; refreshes consumer/index. On success returns existing buffer address, increments sequence and advances reservation by8*block_count. | Reserves caller-supplied queue storage; allocates no heap memory and copies no payload. |
| full/space rejection | Returns5 for signed sequence budget exhaustion or insufficient contiguous/wrapped space; returns7 when a prior reservation remains unpublished. | Sequence budget is computed as consumer_sequence+254-producer_sequence, independently of byte-space guards. Not the SDK IOM pending256 check. |
| post4279f0 | Writes two-word trailer: index-register address OR low8(kind)!=0, then sequence; commits producer=reservation and writes sequence low8 to hardware index register. | Publication commits command storage; it is not a payload buffer copy or release. |
| cancel4279be | Requires unpublished reservation; resets reservation=producer and decrements sequence. | Discards latest reservation only. After publication returns7. Does not free caller memory, clear callbacks or cancel already-published commands. |
| term427ad6 | Refreshes indices. Low8(force)==0 rejects unequal producer/consumer sequence with3. Otherwise clears claimed bit, hardware option bit0 and control mask. | Forced term does not drain commands, invoke callbacks, free buffers or restore application ownership. Software enabled flag is not independently cleared by this body. |
| MSPI term423f64 | If slot nonzero, calls generic term(queue,1) and clears handle slot, ignoring returned status. | Forced teardown of that queue slot, not proof that DMA/IRQ/task users are quiescent. |

All register behavior above describes issued instructions under supplied states, not a physical peripheral guarantee. Generic indices are monotonic sequence snapshots with an8-bit register epoch; arithmetic wrap is preserved.

## Validation

`cmdq-ownership-4f111c.json`:40 stock/source comparisons plus13 original-only termination fixtures. Term was linker-GC discarded from the shared image, despite existing source. A separate supplementary module then retained the exact frozen `dfu-storage-queue-compatible/nor_mspi_queue.o` termination section at0x3f000, linking critical-save to the shared-image source symbol. `cmdq-ownership-isolated-term-4f111c.json` passes all53 comparisons:40 against shared-image source,13 against the explicitly separate termination module. This does **not** claim termination is linked into the shared image. `term-module-provenance.json` records object/module hashes and reproduction command.

Fresh CPUs per fixture; finite RAM MMIO/index states. Cases include reservation/post/cancel ordering, count0/1/2/8 and byte-space boundaries, wrapped reservation, unpublished-busy/invalid/null-output guards, sequence budgets254..257, force low8 truthiness, and pending0/1/255 termination. No live consumer/DMA/IRQ scheduling or hardware-safe teardown claim. No firmware source changes, commits or device writes.

## Remaining boundary

CMDQ cancellation and forced termination are not true buffer reclamation. Before an ownership patch, establish actual peripheral stop/acknowledgment, interrupt masking and callback/task quiescence along the relevant lifecycle path. This artifact cannot provide those missing hardware/scheduling facts. For source reconstruction the next retained initializer gap430280 is pin/GPIO descriptor registration, not a missing IOM queue submission function.
