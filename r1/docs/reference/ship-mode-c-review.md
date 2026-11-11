# Ship-mode GPIO chain in C

`board/native_ship_mode.c` supplies three missing hardware C candidates:
port decode `0x79250`, raw GPIO configuration `0x78dea`, and the ship-mode
pulse at `0x50708`. One manifest unit owns these implementations.

Port decoding reads the pin word once. Values below 32 choose P0
(`0x50000000`) without writing that word; every other value selects P1
(`0x50000300`) and writes the low five bits back. Configuration combines raw
32-bit direction/input/pull/drive/sense words at shifts 0/1/2/8/16, without
additional masks, and stores the result to `PIN_CNF[decoded_pin]` at offset
`0x700`. These operations agree with stock bytes and the fetched Nordic HAL.

The pulse configures P0.5 with word 3, writes bit 5 to OUTSET at offset
`0x508`, calls `osDelay(200)`, then writes configuration word 2. Delay errors
do not skip the final configuration. The stock observed R0 value is five
on return, which the C candidate explicitly returns. No milliseconds or
physical shutdown behavior is inferred from the delay argument or function name.

The whole native and actual C helper chains pass 262 port-decode pairs,
3,310 raw-configuration pairs and ten complete pulse pairs. Cases cover every
pin value 0–255 plus high-word boundaries, raw all-ones/high-bit fields, 2,000
seeded configuration vectors, delay errors and a PIN_CNF mutation during the
delay. All ordered MMIO writes and final mapped register bytes match. Decoder
cell access order, pointer mutation, preserved registers, SP and interrupt
masks are checked. Wrong port mask, drive shift, delay argument and final input
configuration mutations are rejected.

All 581 R1 units compile; all 580 prior objects remain identical. Imports stay
164 application / 34 bootloader. Exact qualification selects none of this unit:
the C pulse uses a 32-byte frame instead of 24, while generic configuration
uses 32 instead of 40. Caller-clobbered state and arbitrary stack aliases are
not established. MMIO fixtures do not model electrical GPIO response, RTOS
scheduling or actual delay time. The unchanged canonical hybrid still has
4,061 source bytes and the locked stock application hash. Reproducible probes
and REA readbacks are under `build/goal-r1-ship-mode-c`; durable results are in
the adjacent JSON. Full source-only rebuilding remains incomplete.

The later [frame closure review](ship-frame-c-review.md) supersedes the C frame
measurements above, with native 24/40-byte frames and restored provider state.
Initial stack-save ordering remains a verified exactness boundary.
