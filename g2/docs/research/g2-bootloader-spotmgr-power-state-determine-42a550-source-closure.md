# G2 bootloader SPOT-manager power-state classifier source closure

The bootloader range `[0x0042A550, 0x0042A85E)` is the Apollo510
`spotmgr_power_state_determine` classifier. It converts the requested device,
audio, temperature, CPU, GPU, retained-MCU, and collapse-profile state into
the 20 power-state and eight Ton-state classes used by the surrounding
transition manager.

The production source is
`components/bootloader/core_overlay/runtime_spotmgr_power_state_determine_42a550.c`.
Its ARM path is reviewed Thumb-2 mnemonic assembly, while its portable path
expresses the independently testable classifier semantics. Apple clang 21 and
Homebrew clang 22 both produce the exact 782-byte stock body with SHA-256
`73e2c284f4c3efc45c0cb02ad3d2d5c520c56ce136e4c185a4fbd56b815a0d87`.
The body has no relocations.

The admission authenticates the sole direct caller at `0x0042AB2A`, rejects
interior ingress and stored entry pointers, pins the eight shared literals at
`0x0042ACC0` through `0x0042ACDC`, and compares the body with the Apollo main
analogue at `0x005A45D0` (750 identical bytes and 16 literal-load difference
runs). The host test evaluates 40,960 combinations against an independent
descriptor reference, including invalid descriptors and uint32 shift wrap.

This is software closure only. Execution against SPOT-manager registers and
silicon-specific retained state is blocked by unavailable physical evidence.
