# G2 bootloader hardware clock-encoder source closure

The authenticated Thumb entry `[0x0042C26A,0x0042C3E2)` is a 376-byte
clock-divider search, rounded-rate computation, and register-field encoder.
Its sole direct caller is `0x0042CCB0`; no interior entry or stored function
pointer is present. The Apollo-main analogue begins at `0x0055BF64` and shares
370 of 376 bytes. Its 96,000,000 Hz source-clock and 250,000-unit canonicalization
literals are retained typed data at `0x0042C980..0x0042C988`.

`runtime_hw_clock_encode_42c26a.c` is first-party MIT clean-room source.
Canonical Apple clang 21 and Homebrew clang 22 both emit the stock body exactly
after strict calls at offsets `0x12A`, `0x148`, and `0x15E` to the source-owned
rounded-divider and power-of-two helpers. The relocated body SHA-256 is
`23796b78366978bda2ee2db94e309c4f1cae4e92f5ffbc2072f75becca3ae9e8`;
the unrelocated SHA-256 is
`1a25dd314239f7529ac9e4ea0d6dd690acda443e34cc35eb85fbb223baa349f5`.

The portable model and deterministic tests cover zero and boundary rates,
ceiling division, low-bit exponent selection and capping, phase selection,
quotient rescaling, register-field packing, rounded actual rate, and the
power-of-two canonical form across 10,000 generated cases. The census,
overlay, manifest, ingress topology, literals, main analogue, source review,
and component conservation are pinned by the exhaustive analyzer.

No hardware operation occurred. Live clock, MMIO, peripheral tolerance,
signal integrity, timing, interrupt, reset, and cold-boot qualification is
blocked by unavailable physical evidence. Firmware-wide functional
completeness is not claimed.
