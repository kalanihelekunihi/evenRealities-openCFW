# Flash word transfer callbacks

The initializer installs program/read callbacks at runtime 0x10023788 and
0x10023cac. Both are reconstructed in `runtime_gx8002_flash_word_io.c` and
compile using the native macOS C-SKY toolchain. With `-Os -fno-shrink-wrap`,
program occupies 140/148 bytes and read 172/172 bytes. The latter option
preserves the original frame placement and avoids an extra early-return path.

Read selects command 0xeb and control 0x40003219 for IDs 0x1c3812/0x1c3813,
otherwise command 0x6b and control 0x40004218. Program uses command 0x32 and
control 0x40000218. Setup, FIFO polling, draining, and controller cleanup
follow the original register sequence. Each transfers floor(length/4) words.
Read length zero returns immediately; program length zero still performs
setup and drain operations. No new timeout or length rejection is introduced.

The comparison executes both original and rebuilt bodies and validates ordered
MMIO, device-state reads, buffer words, helper calls, and frame restoration.
It covers 2522 scenarios: each length 0..65, 255/256/257/1024, 64KiB transfers,
ID branch boundaries, address boundaries, and delayed readiness. The admitted
polling helpers are modeled with their return and caller-clobber contracts;
physical controller readiness and timing are not established. Caller buffers
must be word-aligned, valid and nonwrapping. Counts not divisible by four do
not cause accesses to the trailing bytes.

All initializer service calls and installed callbacks now refer to named C
reconstructions. The initializer remains a separate candidate: its frame is
four bytes larger than stock, state/interface ownership is incomplete, and
end-to-end startup is not yet qualified.
