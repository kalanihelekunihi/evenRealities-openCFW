# G2 bootloader bounded hardware-configuration retry source closure

The authenticated entry `[0x0043048E,0x00430502)` is a 116-byte callback
setup and bounded configuration retry service. Its sole caller is `0x00430576`;
no interior or stored entry exists. The Apollo-main analogue at `0x005041C6`
shares 98 of 116 bytes.

`runtime_hw_config_retry_43048e.c` is first-party MIT clean-room source. Apple
clang 21 and Homebrew clang 22 reproduce every stock byte after four strict
calls: two callback registrations, a 10-microsecond delay, and the source-owned
configuration transaction. The relocated SHA-256 is
`6ba3fb6ddde5fa56fd43fc1f7f717bcc7cf201df2ae6af1b86d20bdde8404dbb`;
the unrelocated SHA-256 is
`d38d571a4434f154b7f72b56d99123af55902ac5105c4202cc13087a0971b418`.
Portable tests cover immediate success, retries then success, the 1,000-attempt
timeout, callback setup for channel four, delay accounting, and null-state
failure.

No hardware operation occurred. Live callback, timing, MMIO, peripheral,
concurrency, reset, and cold-boot qualification is blocked by unavailable
physical evidence. Firmware-wide completeness is not claimed.
