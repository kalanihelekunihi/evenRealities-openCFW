# R1 native sleep-interval dispatcher in C

`native_gomore_dispatch.c` supplies stock entry `0x67bbc` (110 bytes), resolving
the wake caller's interval-dispatch dependency. [The review receipt](gomore-dispatch-c-review.json)
binds source, production object, REA bytes, startup initialization and replays.
The wake caller's declaration now expresses the observed integer return; its
machine object remains unchanged.

The dispatcher clears a 32-byte copy buffer, loads the current context pointer,
and calls the selector with addresses context+4400, +400 and +396. The stock
selector writes all 32 output bytes on every normal return: its exits copy a
complete candidate or cached record. The dispatcher copies those bytes into
its cleared buffer. A zero byte at offset 26 returns `UINT32_MAX` without
accessing the caller's workspace or count.

For any nonzero byte 26, it saves the workspace payload word at +8, reloads the
live context pointer and calls packed output with context+5112, context+436,
the copied record, count pointer and workspace pointer. It restores the saved
payload word after the call, even on error or when count/workspace fields alias.
Backend zero returns zero; every nonzero status becomes `UINT32_MAX`. The
context pointer cell at `0x20007c4c` is the only new RAM ownership: executed
startup handlers, independent RW decoding and guarded initialization confirm
its four cold bytes are zero. The pointed-to context and its producers remain
separate dependencies.

There are 306 paired native/C cases covering zero/nonzero record flags, context
address wraparound and changes during providers, backend statuses, payload
values, aliasing count/workspace/context cells, unaligned workspaces, logical
null faults and interrupt masks. They compare calls, arguments, state, copied
bytes, result, preserved registers, SP and masks. Six compiled defects are
rejected: wrong flag offset, wrong empty result, unnormalized error return,
omitted payload restoration, stale context and short clearing.

Another 144 pairs execute the actual C wake caller, new dispatcher and `memcpy`.
They cover output flags, backend errors, output count zero/nonzero, authorization,
logging and payload allocation failure. The caller still proceeds to final
publication after dispatch, including error/empty cases, as stock does. Lower
selection, packed output, interval update, final publication, allocation and
logging remain modeled boundaries.

The source/copy buffers match native addresses at caller SP-88 and SP-56. C
provider calls add eight bytes of stack. Native reuses its unused source buffer's
first word for an outgoing fifth argument, whereas C keeps that argument
separate; these private unused bytes, caller-clobbered registers and flags are
excluded. This is not full stack or asynchronous-consumer identity.

The selector `0x72572` and packed-output provider `0x726c4` retain explicit native
interfaces, rather than the incompatible analysis-plan API routes. The adjacent
interval updater also exposes a raw scratch slot and remains separate work.
All 626 units compile and both relocatable payloads compose without duplicate
strong symbols. All 625 prior objects are unchanged. Resolving this dispatcher
exposes its two lower providers, changing application imports from 167 to 168;
bootloader imports remain 34.

Exact qualification rejects the new body. The canonical source plan remains
unchanged; a fresh hybrid retains 4,295 source-built bytes and locked application
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Physical execution, concurrent context changes, a complete source-only link and
instruction identity remain open.

The [subsequent staging review](gomore-stage-c-review.md) now supplies the packed-
output wrapper in C and qualifies the selector's four-byte word-store leaf. Its
lower consumer remains explicit.
