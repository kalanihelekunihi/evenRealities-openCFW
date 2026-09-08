# GPIO trigger disable candidate

Stock package0xf600/runtime0x10206074,92-byte envelope. Rejects unsigned
port>=32 with-1. Valid ports call the direction helper with HIZ(2), then
clear the selected bit through separate read/write pairs at GPIO offsets
0x14,0x18,0x28,0x2c,0x24 in that order. Finally writes callback-record port255,
callback0,private0 and returns0. It does not clear the whole GPIO block or
unregister the shared IRQ handler.

C candidate uses the authenticated SDK GPIO header and compiles natively on
macOS to92bytes, SHA
d90ff2fcb331b40941b032845634f56061b4dd9869c722c650b3a75727543bdb.
Three independent boundary-model tests pass for rejection, register/cleanup
order and preservation of other pin bits. Decoded target/ABI qualification
is pending. Model reuses the trigger module's memory layout; direction helper
body remains modeled. Candidate is unregistered and not source-admitted.

Decoded qualification completed:1,225 stock/source comparisons pass all32
valid pins, unsigned rejection boundaries and35 register seeds. Exact MMIO
and callback cleanup ordering, direction helper calls/clobbers and8-byte
saved frame are checked. Five target tests plus three model tests pass,
including corrupt first clear, wrong helper target and damaged frame. The
report pins both the disable model and its shared trigger-memory model.
Candidate remains unregistered until the active enable integration finishes.

Integration completed:630tests pass. Full macOS apple-clang package rebuild
and verify-artifacts succeed. Codec SHA
2ef9ef908e046ba7fcbe27d07b947a491c4e893e972863a689d1dafd6500fc0b;
package SHA3224baf653f0c9b526aae6b0e341636ff8904c551b1461f888df8ce0d23d7b24.
This92-byte routine is now compiled from C; the package remains hybrid and
hardware-unqualified.
