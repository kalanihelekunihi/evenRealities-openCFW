# G2 bootloader DFU payload programmer source closure

The authenticated interval `[0x0042DAE8,0x0042DC90)` is production-routed from
`runtime_dfu_payload_program_42dae8.c`. Apple clang 21 and Homebrew clang 22
reproduce all 424 stock bytes after fourteen strict Thumb-call relocations. Its
sole caller is `0x0042E004`; no interior or stored-pointer ingress exists.
Thirteen literal cells pin image paths, buffers, log context, and configuration.

The service masks the encoded size to 24 bits, skips the 32-byte header, runs
the pre-program traversal, opens and seeks the image, processes full configured
chunks plus a remainder, logs progress and short reads, calls the authenticated
indirect programming callback, compares each programmed chunk, advances the
destination, closes and clears the handle, and reports completion. Portable
tests cover open failure, bounds, full chunks, remainder, short reads, compare
errors, callback/compare accounting, close, and final address.

Offline compilation, portable behavior, provider identity, manifest ownership,
and unsigned firmware assembly are verified. Live storage contents, filesystem
I/O, destination memory, the indirect programming callback, coherency, power
loss, timing, reset, and cold boot are blocked by unavailable physical evidence.
No signing, flashing, reset, or hardware access occurred; functional
completeness is not claimed.
