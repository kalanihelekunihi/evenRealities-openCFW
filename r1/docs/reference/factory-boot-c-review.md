# R1 configuration-driven factory boot scheduling in C

The stock routine at `0x48ba4` (38 bytes) now has the C candidate
`r1_factory_boot_mode_schedule`. Its earlier recovered name,
`r1_wear_state_buffer_fill`, did not describe the observed instructions.
The factory worker now references the corrected symbol, with one implementation
for that stock routine. The delayed callback at `0x883ee` (10 bytes) has the C
candidate `r1_factory_delayed_mode_start` in the same source unit,
`runtime/native_factory_boot.c`. [Machine receipt](factory-boot-c-review.json).

The gate calls the configuration-byte getter at `0x7b9ec`, preserves its full
return value, and calls the configuration-word getter at `0x7ba08` even though
that second result is ignored. It schedules the actual callback with argument
zero and delay 30,720 when `(value >> 6) != 0` and bit `0x10` is clear. The
callback ignores its incoming argument and tail-forwards to factory-mode start
at `0x48bd0` with handle `0xffff` and mode argument zero. No buffer filling or
flash operation is established by this routine.

The two configuration getters remain explicit dependencies with valid C
candidate names in the frontier. Native evidence shows each reserves 124 stack
bytes, calls the cached-class reader, ignores status, then extracts byte offset
`0x78` or word offset `0x74`. A failed or partial read can expose the original
stack contents. This step does not replace that ABI with an uninitialized C
array or an invented default configuration. Getter implementation and factory
mode activation remain unfinished work.

Verification passed 3,072 paired gate cases, covering every byte value plus
256 full-width provider results, varying ignored word results and both
interrupt-mask states. Another 30 paired callback cases verify fixed outgoing
arguments and tail return behavior. Getter calls use the native eight-byte
frame; scheduler and mode-start tails use zero-byte frames. Void gate return
registers, APSR and private stack bytes are outside the comparison.

The renamed factory worker passed its current 860-case replay. Another 96
paired cases execute the actual native/C worker and boot gate together, varying
gating values, flag paths, masks and handle mutations. Other initialization
callees, raw getters, delayed scheduler, RTOS, timer, record dispatch and watchdog
remain modeled. These tests establish neither actual delayed callback execution
by the event loop nor physical factory-mode entry. Five mutants were rejected:
skipping the ignored word read, wrong threshold, wrong bit, wrong delay and wrong
callback handle. Production replay passed again after the negative controls.

All 606 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. Of the preceding 605 objects, 604 remain
identical; the factory task object changes its initialization symbol binding.
The historical startup import is resolved and three dependencies become explicit:
the two getters and factory-mode start. There are now 163 application imports
and 34 bootloader imports. The getter rows remain unresolved candidates, not
accepted source providers.

The scoped qualifier selects no executable bytes. The canonical source plan
is unchanged, and the fresh hybrid matches the locked application using 4,271
source-built bytes, 641,889 executable pull-through bytes and 248 resource bytes.
This is not candidate byte identity, source-only completion, real cached-storage
validation or physical hardware proof.

The subsequent [factory-mode activation](factory-mode-c-review.md) supplies
mode start in C with a retained frame gap and deeper configuration-writer,
stream-registration and callback dependencies.
