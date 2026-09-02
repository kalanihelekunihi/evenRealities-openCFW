# G2 bootloader register-helper source closure

Eight post-MSPI leaf functions are now owned by clean-room MIT C in `runtime_register_helpers_42c034.c`: hardware status routing and error classification at `0x0042C034..0x0042C0B2`, interrupt enable/status/clear helpers at `0x0042C63A..0x0042C6E4`, and NVIC/SCB enable/priority helpers at `0x00430240..0x00430280` and `0x00430470..0x0043048E`.

The Arm path is mnemonic-only inline assembly because the recovered functions use address-sensitive PC-relative hardware literals. The non-Arm path is a portable behavioral model covering route selection, error precedence, handle validation, enabled-only status masking, clear publication, signed interrupt rejection, NVIC word/bit selection, and external/system priority-byte selection. No executable raw-encoding directive is present.

Apple clang 21 and Homebrew clang 22 independently reproduce all eight authenticated stock bodies exactly, with no relocations: 66, 60, 56, 68, 46, 28, 36, and 30 bytes respectively. Host behavioral tests exercise the functional contracts without touching live MMIO. Validation against physical Apollo510 interrupt hardware is blocked by unavailable physical evidence.
