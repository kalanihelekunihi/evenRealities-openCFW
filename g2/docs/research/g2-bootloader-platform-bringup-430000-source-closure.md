# G2 bootloader platform bring-up source closure

The authenticated interval `[0x00430000,0x004301D6)` is production-routed from
`runtime_platform_bringup_430000.c`. Apple clang 21 and Homebrew clang 22
reproduce all 470 stock bytes after 23 strict provider relocations. Its sole
caller is `0x004301E4`; no interior or stored-pointer ingress exists. Sixteen
literal cells pin callback records, configuration, thresholds, state, and logs.

The service registers its callback, initializes a hardware context, enumerates
calibration, captures the register profile, prepares and applies the hardware
profile and channel, activates and commands the handle, runs three measurement
attempts with the authenticated `0x4A6 >> 12` scale and range classification,
restores the register profile, resets the handle, and tears down the callback.
Portable tests cover attempt gating, third-attempt begin/end, classification,
restoration, reset, and teardown accounting.

Offline compilation, portable behavior, provider identity, manifest ownership,
and unsigned firmware assembly are verified. Live callbacks, calibration,
registers, clocks, channel activation, sample timing/accuracy, interrupts,
reset, and cold boot are blocked by unavailable physical evidence. No signing,
flashing, reset, or hardware access occurred; functional completeness is not
claimed.
