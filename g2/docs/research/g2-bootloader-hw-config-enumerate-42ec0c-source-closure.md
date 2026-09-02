# G2 bootloader hardware configuration and enumeration source closure

The authenticated bodies at `0x0042EC0C..0x0042ED60`,
`0x0042EE00..0x0042EE6C`, and `0x0042EE70..0x0042EFF4` are now generated from
reviewable MIT-licensed C in
`components/bootloader/core_overlay/runtime_hw_config_enumerate_42ec0c.c`.

The services validate the hardware-handle magic, dispatch bounded configuration
operations, normalize packed channel values with the calibrated floating-point
transform, and enumerate either the hardware traversal register or a supplied
channel list into bounded output records. Portable models exercise every
software-visible operation and error return without live MMIO.

Apple clang 21 and Homebrew clang 22 reproduce all three stock bodies exactly
after the two declared sibling-call relocations. Apollo-main analogues at
`0x0055DC88`, `0x0055DE7C`, and `0x0055DEEC` are byte-identical. Live register,
peripheral, and calibration behavior is blocked by unavailable physical
evidence.
