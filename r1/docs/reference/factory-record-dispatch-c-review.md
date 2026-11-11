# R1 factory record dispatcher in C

The factory queue consumer at stock application address `0x45f3c` is now
implemented by `r1_factory_input_record_plan_dispatch` in
`r1/src/application/runtime/native_factory_task.c`. It drains the existing
factory queue at `0x200066bc`, which carries pointers to twelve-byte message
headers followed by payload bytes. A null dequeued pointer is skipped. The
current pointer slot is freed after dispatch and cleared before the next queue
read; a callback that changes the slot also changes which pointer is freed.

For records longer than three bytes whose payload starts `AT^`, the stock
routine writes a trailing zero at the declared payload length and calls the
existing C tokenizer. Other records are passed to the Nordic hexdump logger
with tag `0x001c0004`, then to the **factory** legacy command router. That
router is the stock function at `0x625c0`; the BLE receive router at
`0x4e258` is a different function and is not substituted here. The caller
passes the low sixteen bits of the record handle and length to the router.
The record pointer remains volatile across provider calls, preserving the
stock routine's reloads if a callback changes the live stack slot.

An ignored emulator probe at
`build/r1-factory-dispatch-probe-20261110/verify.py` compared the locked
stock function with the compiled C object in 165 paired cases. These cover
zero through 32-byte lengths, three high-bit lengths with non-AT payloads,
AT and non-AT prefixes, null queue items,
multiple records, empty queue, randomized payloads, and a hexdump callback
that replaces the pointer slot. Call traces and both record buffers match.
The machine receipt is
`build/r1-factory-dispatch-probe-20261110/results.json`.

The authoritative R1 rebuild compiles 883 application and 82 bootloader
units with no failures or duplicate strong symbols. The strict bootloader
link passes with a valid 512-byte C vector. The strict application link
still has 37 unresolved symbols: this unit replaces the dispatcher import
with the newly exposed factory router import. The full flash load overflow
is 28,760 bytes, 144 bytes above the prior checkpoint. The strict receipts
are under `build/r1-factory-dispatch-corrected-20261110/`.
The full `make sources` run also passed using the fresh ignored output at
`build/sources-factory-dispatch-20261110/`; it added no failures or duplicate
strong symbols in either device tree.

Queue, logger, router, tokenizer and free providers were modeled in the
paired replay. The AT terminator was tested only within mapped record
storage, while the stock allocation path does not itself prove an extra
byte exists. Actual RTOS scheduling, physical factory transport, full
application linking, live hardware behavior and byte identity remain open.
