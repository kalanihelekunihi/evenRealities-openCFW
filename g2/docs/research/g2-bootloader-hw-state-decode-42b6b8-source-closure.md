# G2 bootloader hardware-state decoder source closure

The authenticated interval `[0x0042B6B8,0x0042B9BA)` is production-routed
from `runtime_hw_state_decode_42b6b8.c`. Apple clang 21 and Homebrew clang 22
reproduce all 770 stock bytes without relocations. The body and unrelocated
SHA-256 are
`74f4304f6e3aa59022a29eb5e5f5479c77072b33355825b7c9409897001bb9d1`.
Its sole caller is `0x0042BCEC`; no interior or stored-pointer ingress exists.
The Apollo-main analogue at `0x005A13E8` matches 738 of 770 bytes, with all
differences confined to image-local PC-relative literal offsets. Eight literal
cells pin the initial packed state, dynamic mode register, alternate-output
flag, masks, and comparison constants.

The service composes six four-bit state fields from the input record, dynamic
mode, and status bits; classifies 24 primary packed states; applies the
alternate result family where enabled; then classifies 12 secondary packed
states. Unsupported primary or secondary combinations return status five and
do not fabricate downstream output. The portable differential covers 16,384
combinations across all field-eight values, input modes and kinds, word-state
families, dynamic-mode choices, and alternate-output states, including partial
output behavior on secondary rejection.

The 10,192-byte MIT source has SHA-256
`67170ef4a1621e6a6bb564cb963fb981774fca0b906b14263bdeb755cc746ddb`.
Focused tests, strict dual-toolchain compilation, manifest ownership, provider
conservation, and unsigned complete-image assembly are verified offline. Live
flash-literal, retained-SRAM, MMIO, peripheral-state, concurrency, reset, and
cold-boot behavior are blocked by unavailable physical evidence. No signing,
flashing, reset, register access, or other hardware operation occurred;
functional completeness is not claimed.
