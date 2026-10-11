# Recovered EM9305 scheduler C candidate

The stock control flow at `0x311634..0x31166c` now has a C implementation,
including the halfword ready-set load, byte narrowing before every priority
comparison, returning zero without publishing when either guard rejects,
assertion metadata and continuation, and the one-byte next-priority write.
State offsets and the fixed SRAM address come from the authenticated listing.

Two imports remain explicit: the vendor `log2p1` operation and assertion handler.
Their declared interfaces are requirements for future port adapters, not claims
about the producing vendor C ABI. In particular, the custom stock instruction
consumes R0 and produces R13. Its arithmetic and zero-input behavior have not
been replaced by inferred highest-bit arithmetic.

`g2/firmware_c/build.py --image ble_em9305 --include-experimental` compiles this
body together with the queue initializer using the pinned ARC EM compiler,
then links a relocatable object. The experimental graph has three C exports and
two unresolved port imports. This is not a complete EM9305 controller image.

The accompanying `verify_scheduler_contract.c` passes 12 host contract cases:
byte-wrap values 256/257/511, threshold 17, guard rejection, assertion return,
and preservation of unrelated state bytes. The vendor operation is supplied
by the harness. These checks do not execute the original ARC instructions or
prove hardware semantics. Full controller source, producing port/configuration,
initialized data, startup and final placement remain unresolved.

`log2p1_port.c` now compiles a hardware operation adapter using the vendor
major7/minor0 two-operand declaration. GNU gas calls the no-suffix class
`SUFFIX_NONE`. The object emits exactly `3d2f1000 log2p1 r13,r0`, saves/restores
callee-owned R13, and returns its value through ordinary C R0. No software
highest-bit equation was substituted. Experimental composition now leaves
only the assertion import. This closes the C adapter source requirement, not
custom instruction arithmetic/exceptions, producing core profile, or original
instruction/device execution. See `em9305/log2p1-port-receipt.json`.

`activate.c` now reduces the entire retained QK_activate_ control flow at
0x311554..0x3115e4 into ARC C. Architectural `seti 0`, `clri 0`, `sync`,
and `bclr` operations retain their native instruction identities. The
activation candidate compiles/links with queue, scheduler and custom-operation
adapter. Event-get and garbage-collection bodies remain explicit imports,
alongside assertion; original instruction execution and whole controller
source/data/startup/layout remain unproved. See activation-receipt.json.

`assert.c` and `event_gc.c` reduce the returning callback dispatcher and
collector. The collector restores saved IRQ state before pool-return calls;
no product callback or pool configuration is guessed. Seven exports/two
imports after `em-event-gc-round`, with static native/compile evidence only.

`queue_pool.c` implements decoded active-get and pool-return paths, including
returning assertion behavior, byte/halfword counter truncation and saved IRQ
state. The small experimental graph now has nine exports/zero imports. This
does not cover remaining controller code or source-owned product initialization,
startup and layout. Strict aliasing is explicitly disabled for recovered
mixed-width RAM views. See queue-pool-receipt.json.

`framework_init.c` reduces actual framework initialization writes and
clear-call sizes, including the observed zero-length no-op, 68-byte active
table and eight-byte scheduler clear. Eleven exports/one genuine memory-fill
contract after its partial build. Product memory ownership, reset/startup and
complete record source are still open.

`memory_fill.c` closes the native fill child with byte/word access widths and
full-register pattern expansion, including behavior beyond ordinary libc
byte values. ARC compile and1,820 host contract checks pass; twelve exports
and zero imports in this small source graph. Native runtime, full controller
coverage/product initialization/startup and record layout remain unproved.

`resume.c` adds byte-bound native resume hook and resume-loop bodies. ARC
compile/link passes at18 exports/one genuine sleep contract. Source keeps
callback/IRQ/controller state semantics; producing configuration and complete
controller/reset/data/record layout remain open.
