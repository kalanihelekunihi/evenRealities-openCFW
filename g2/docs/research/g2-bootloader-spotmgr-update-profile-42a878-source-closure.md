# G2 bootloader SPOT-manager update/profile source closure

The dispatch table at `0x0041D150` and `0x0041D158` proves two live entries
inside the formerly conservative mixed span: the 758-byte power-state stimulus
update at `0x0042A878` and the 54-byte profile register application at
`0x0042AB7C`. The byte ledger is split so neither function remains hidden as
mixed data.

Both production sources use reviewed Thumb-2 mnemonics and portable semantic
paths. Apple clang 21 and Homebrew clang 22 reproduce the exact stock bodies.
The update body has six authenticated call relocations; the profile body has
none. Host tests cover every stimulus class, on/off and required-null behavior,
profile magic gating, and all three bitfield updates.

The hardware-only MMIO, critical-section, temperature-sensor, SIMOBUCK, and
trim-transition behavior is blocked by unavailable physical evidence.
