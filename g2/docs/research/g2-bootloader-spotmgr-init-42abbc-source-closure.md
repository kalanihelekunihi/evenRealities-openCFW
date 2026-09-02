# G2 bootloader SPOT-manager initialization source closure

The dispatch pointer at `0x0041D14C` selects the 146-byte initializer at
`0x0042ABBC`. Its production source reproduces the exact body under both
reviewed compilers, including three MRAM-read provider edges and the runtime
initialization edge. Portable tests cover the hardware gate, successful trim
loading/commit, and all three read-error exits. Live MRAM and SPOT hardware
validation is blocked by unavailable physical evidence.
