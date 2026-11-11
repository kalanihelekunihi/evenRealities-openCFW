# R1 ring-size legacy command in C, 2026-11-11

Stock `0x7c9e8` reads the one-byte `r_size` KV class, overwrites that byte
with its low input byte, writes the class, and calls the NV idle check. Stock
`0x628cc` reads the class for selector zero; selector one first sets the
requested packet byte and then rereads it. Both reply with five bytes.
Other selectors return zero without storage or reply work. The C owner for
both functions is `r1/src/application/board/native_ring_size_command.c`.

The ignored `build/r1-ring-size-command-c-20261111/probe.c` checks all 256
command selectors and a full-width setter input under AddressSanitizer and
UndefinedBehaviorSanitizer. It verifies read/write/idle/get/reply order,
low-byte storage, packet bytes, and invalid-selector behavior. The existing
source-owned `r_size` handle and getter supply the storage path.
