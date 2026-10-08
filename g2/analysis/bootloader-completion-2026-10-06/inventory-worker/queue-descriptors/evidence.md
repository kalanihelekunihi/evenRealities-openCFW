# Apollo CMDQ descriptor helper recovery

Pinned image: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, loaded
at `0x410000`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

`queue_descriptors.c` provides readable C for stock `0x42790a` block
reservation, `0x4279f0` descriptor posting, and `0x427baa` queue reset.
Reservation follows the ring's producer/read/end pointers, checks space for
the required descriptor words and optional wrap marker, increments the stock
sequence counter, writes the caller's output pointer/count, and returns the
stock status. Posting commits the descriptor and current count, updates the
hardware index register, and uses the stock DMB threshold. Reset rejects an
active queue, clears the sequence/index state and resets the command registers.

The isolated comparison executes the pinned instructions and compiled source
against the same synthetic queue state and mapped MMIO. Current result:
15 cases and 436 distinct original instruction bytes pass. Cases include normal
and wrap-marker allocation, insufficient space, stale producer state, null
output, count zero, valid/invalid post, full post, active reset, and invalid
queue. Results are recorded in `result.json`.

The three helpers update descriptors and registers only. Actual CQ DMA
execution, asynchronous progress, timing, and device status remain outside this
fixture. The adjacent request-33 helper at `0x4240aa` enters shared continuation
code at `0x4240d2`, which calls `0x423fb8` for CQ pause/poll and may then call
`0x42403e` for DMA setup. Those paths include physical status polling and
delay/clock behavior; this module does not replace them with assumed success.
