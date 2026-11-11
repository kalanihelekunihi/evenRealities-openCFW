# R1 health GET encoders in C, 2026-11-11

The three naked assembly wrappers at stock `0x83930`, `0x83972`, and
`0x83c20` are now typed C functions in
`r1/src/application/runtime/native_health_get_encoders.c`. They select HR,
HRV, and SpO2 opcodes `258`, `1026`, and `514` with payload lengths eight,
nine, and eight bytes. A nonnull payload passes the original flags and
sequence to the existing C transport. A null payload sends the no-data flag
with value two and reduces the provider result to Boolean. The existing
`0x82ef4` wire-header implementation remains the owner of the transport
bytes. No executable instruction data or inline assembly remains in this
source file.

The ignored probe at `build/r1-health-get-encoders-c-20261111/probe.c`
checks all three opcodes with payload and no-data paths, success/failure
returns, header fields, sequence narrowing and invalid-handle suppression.
AddressSanitizer and UndefinedBehaviorSanitizer pass. The probe uses mocked
connection and transport providers; board delivery and exact instruction
identity remain unverified.

`build/sources-r1-health-get-encoders-c-20261111/report.json` compiles
938/938 application and 82/82 bootloader units without known failures or
duplicate strong symbols. The strict application receipt at
`build/r1-link-health-get-encoders-c-20261111/report.json` has the same 13
undefined functions and uses 643,952 of 696,320 flash bytes, 64 fewer than
the preceding assembly-backed checkpoint. The strict bootloader receipt at
`build/r1-boot-link-health-get-encoders-c-20261111/report.json` links with a
valid vector. `make sources-check` passes. This is a source-language
conversion, not a byte-identical replacement.
