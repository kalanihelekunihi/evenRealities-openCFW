# Native touch request adapters in C

`board/native_touch_transport.c` supplies the read adapter at `0x9338c` and
previously omitted write entry at `0x933b4`. They share one 20-byte request
owner at native `0x2000680c` and use the existing volatile touch-bus cell at
`0x200067fc`. The historical contextual registry helper remains a separate
API; no second fixed-address request owner is added.

The initial state is authenticated by executing the locked native scatter
decoder at `0x286f4` on flash `0xc4610`, into `0x200064a8` for 0x195c bytes.
Its request bytes are `5600000000000000010000000000000001000000`.
The manifest C object's complete 20-byte initializer matches that output:
command 0x56, both lengths one, and other fields zero. No wire-address
interpretation is inferred from that command byte.

Both wrappers store the register's low halfword first. Read then stores the
low-halfword read length at +16 and output pointer at +12; write stores the
write length at +8 and input pointer at +4. Command, reserved bytes and other
direction's fields are retained. Write always stores its pointer, including
NULL. The bus handle is loaded after these stores. Registry operation arguments
are `(handle,0,&request,0)`, using slot 0x10 or 0x14; only raw status zero maps
to success. Empty R4 constraints preserve the native eight-byte frame and
provider-visible registers; every executed operation is C.

The actual request and existing bus owners are linked at their native addresses
in the fixture. It passes 6,912 paired three-call sequences, or 20,736 paired
invocations, covering alternating reads/writes, NULL/self pointers, 16-bit
narrowing boundaries, full-word statuses, seeded retained fields and callback
mutations to the request and bus handle. Tests compare ordered request/handle/
saved-frame accesses, provider arguments and R4–R11, final owner/guard bytes,
returns, SP and interrupt masks. Wrong cold command, command rewriting, skipped
NULL store, narrowed status and wrong-device variants are rejected.

All 587 R1 units compile. All 586 prior objects and 164 application / 34
bootloader import sets remain unchanged. Neither function qualifies exactly;
no source-plan region is added. The canonical hybrid and locked application
hash remain unchanged at 4,245 source-built bytes. Registry dispatch is modeled;
actual I2C traffic/electrical behavior, caller-clobbered registers/flags except
R0, arbitrary aliases/faults/concurrency and complete source-only rebuilding
remain unproven. The touch-ready reader and full identity probe remain separate
reconstruction dependencies. Probes, REA evidence and audit are under
`build/goal-r1-touch-request-c`; durable results are in the adjacent JSON.

The subsequent [touch identity review](touch-identity-c-review.md) adds both
remaining C candidates and validates their integrated request chain. The prior
request functions and data remain unchanged; exactness gaps remain explicit.
