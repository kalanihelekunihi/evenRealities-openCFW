# G2 bootloader SPOT-manager transition source closure

Date: 2026-09-01

## Result

The authenticated 106-byte function at `[0x00428378,0x004283E2)` is now
compilable production C at its original address. The implementation in
`runtime_spotmgr_transition_428378.c` realizes the Apollo510 SPOT-manager
`transition_sequence_2b` register transaction and retains the product-specific
five-microsecond delay and terminal sequence value 26 found in the G2 image.

The implementation is BSD-3-Clause and is grounded in Ambiq's public
`mcu/apollo510/hal/am_hal_spotmgr_pcm2_2.c` at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. That upstream file has Git blob
`4d2ef939de853108e4cb18a55cb2e12be9e5c9a7` and SHA-256
`eac14263dc23ea211b917e9c3feb69695eb511d204961fdf301c1b0fa9abbeb7`.
The G2 timing and terminal-state constants are authenticated product behavior,
not inferred from the current upstream constants.

## Fixed-address and provider evidence

Apple clang 21.0.0 and Homebrew clang 22.1.8 independently emit the same
106-byte unrelocated body, SHA-256
`35a3808a2b454603a347435c52e5e0c1e04e37e6101a6e9948e37fde60242a8f`.
The sole strict relocation is an `R_ARM_THM_CALL` at offset 54 to the retained
delay provider at `0x0041D1C0`. After relocation, both bodies are byte-for-byte
identical to stock, SHA-256
`051e40c208a75b89a9826c46a5fcea7b9933f1de7c90f4acc01777ba1ed16866`.
The authenticated direct caller is the BL at `0x0042A05C`; there is no direct
interior ingress and no stored Thumb entry pointer into the function.

The target body uses reviewable mnemonic Thumb-2, with no raw instruction-byte
directives, and binds the existing authenticated shared literals:

| Literal address | Value | Role |
|---:|---:|---|
| `0x00428A90` | `0x200270B4` | new VDDF trim |
| `0x00428BA8` | `0x4002004C` | VREFGEN4 |
| `0x00428C84` | `0x40020044` | VREFGEN2 |
| `0x00428C88` | `0x2000055A` | ongoing-sequence byte |
| `0x00428C90` | `0x200270B8` | core-LDO active trim |
| `0x00428C94` | `0x200270BC` | core-LDO temperature trim |
| `0x00428C98` | `0x200270B0` | new VDDC trim |
| `0x00428C9C` | `0x4002037C` | PWRSW0 |
| `0x00428CA0` | `0x40020080` | LDOREG1 |

## Behavioral and ownership evidence

The portable host form is checked over 50,000 deterministic randomized
register states. It restores the 7-bit VDDC and VDDF trims, the 4-bit
core-LDO temperature coefficient, and the 10-bit active trim; records one
five-microsecond delay; clears PWRSW0 bits 16 and 25; and stores sequence 26.

The exhaustive 57,153-byte post-MSPI census now has 267 spans: 47 production
source spans / 6,028 bytes, 37 exact candidates / 2,756 bytes, 101 typed
unresolved executable spans / 17,088 bytes, 16 unreachable tails / 284 bytes,
two retained-data spans / 28 bytes, and 64 typed non-entry spans / 30,969
bytes. Zero bytes are unclassified. Apple boot-provider accounting is 38,369
source-owned bytes, 108,625 retained bytes, 16 alignment bytes, and 16,830
generated patch-site bytes; 20,550 source bytes are compiled in place and
2,594 in reviewed caves. The Apple provider remains SHA-256
`94afbc3d7e1aa8d0d21095de081523c2ed9e422287355128eb20d36bf27c88e2`;
the Linux provider remains
`426d77749f96307ae9a45173d20684570d5994d902cf1f1f5cb01f935c6ba7c6`.

The next executable frontier is `0x00428A94`, after the typed non-entry interval
`[0x004283E2,0x00428A94)`.

## Physical evidence boundary

No authorized G2 hardware is available in this workspace. Live SPOT-manager
timer delivery, MMIO ordering, voltage-rail transition, trim effects, power
stability, downstream operation, reset, and cold-boot qualification are
therefore exactly **blocked by unavailable physical evidence**. No signing,
flashing, reset, live register access, or other hardware operation occurred.
Firmware-wide functional completeness is not claimed.
