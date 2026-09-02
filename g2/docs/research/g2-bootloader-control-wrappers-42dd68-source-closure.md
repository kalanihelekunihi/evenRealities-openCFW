# G2 bootloader runtime-control wrapper source closure

Five small runtime functions are now source-owned MIT C: the context getter wrapper at `0x0042DD68`, constant-one control wrappers at `0x0042DD9A` and `0x0042DDA4`, the bit-22/bit-23 dispatcher at `0x0042E1C4`, and the non-returning terminal notification loop at `0x0042E1DA`.

The Arm implementation contains only reviewable Thumb-2 mnemonics and explicit provider relocations. Apple clang 21 and Homebrew clang 22 reproduce the authenticated 8-, 10-, 10-, 22-, and 18-byte bodies exactly. The portable path tests return propagation, constant arguments, all four dispatch combinations, and one bounded terminal/notification iteration; the actual non-returning loop is not executed on the host. Live provider and terminal behavior is blocked by unavailable physical evidence.
