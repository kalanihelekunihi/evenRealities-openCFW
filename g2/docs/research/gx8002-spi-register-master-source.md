# SPI master registration candidate

Stock0xf688/runtime0x102060fc,104-byte envelope. SDKdevice.o identifies the
routine and spi.h defines master/list/flash layouts. The C candidate preserves
validation order:NULL returns-19; zero num_chipselect or negative bus returns
-22. It appends the master to the SPI list using four ordered stores, traverses
the flash list with the observed next-pointer read before sentinel comparison,
and binds the first matching bus with chip_select<num_chipselect. It then
returns0; it does not bind all matching devices.

Authenticated spi.h/list.h/types.h are used for ABI definitions. The old SDK
integer typedefs replace conflicting compiler stdint typedefs in this source.
A generated string.h supplies only a memset declaration for unused SDK inline
helpers; there is no replacement implementation or unresolved memset call.
SDK include directories are system includes, suppressing warnings inside those
unchanged headers. Local source retains-Wall/-Wextra/-Werror.

Native macOS compilation fits92bytes, SHA
bddd3b535a23ea53957073abde1498c0e354ab800fb12798e766756f5e44273d.
The candidate is unregistered and unqualified. Next independently model list
insertion and flash selection, verify decoded stock/C traversal and memory
ordering, reject malformed lists rather than inventing supported behavior.

Independent model_gx8002_spi_register_master.py now represents bounded valid
circular SPI/flash lists, distinct word/byte reads, full retained fields and
ordered writes. Five tests pass:validation short-circuiting, nonempty-tail
append, first-match-only binding, bus/chip-select filtering and the sentinel
next-pointer read. Decoded target comparison remains pending. The model does
not authorize arbitrary invalid pointers, repeated registration or cyclic
malformed lists as supported inputs.

Decoded qualification now passes2,593 cases:bus/sign boundaries, chip-select
counts including0/255/256/allbits,0..3 existing masters, six flash-list shapes
including8nodes, three memory seeds and NULL rejection. Full read32/read8/
write32 trace and final memory match; leaf ABI preserved. Ten model/target
tests pass, including wrong tail read, wrong chip-select comparison and ABI
corruption. The reviewed report pins the model. Candidate remains unregistered
pending initializer integration completion; malformed/repeated/concurrent
registration is outside this valid-list qualification.
