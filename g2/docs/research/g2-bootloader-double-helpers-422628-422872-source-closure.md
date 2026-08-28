# G2 bootloader double-runtime source closure

Thirteen authenticated IAR-compatible double-runtime bodies at
`[0x00422628,0x00422872)` now compile from maintained MIT C at
their exact stock addresses. The executable bodies total 584 bytes with
concatenated SHA-256
`789b0879c8d3070beb7a7fb97ab57cf1bf5c4748401c6dba869dcf774393f6c3`.
The complete 586-byte physical interval, including the two-byte alignment at
`[0x00422712,0x00422714)`, has SHA-256
`b78e28acaa99144bf3f1f5872a4085b0f607264f2fd3914b71cfc48b3785e30d`.

The tranche contains the soft-float `frexp` wrapper and binary64
normalization core, two flag-setting ordered comparators, the soft-float
`ldexp` wrapper and VFP scaling core, signed and unsigned integer conversion
pairs, and binary64 subtraction, division and multiplication leaves. The
scaling core preserves signed zero, infinity and NaN, normal/subnormal
normalization, FPSCR masking/restoration during underflow rounding, and the
retained range-error tail at `0x004275D2`. Eleven bodies are independently
byte-identical to Apollo-main counterparts at `0x0051C170..0x0051C386`; the
240-byte scaling core and reverse comparator remain independently
authenticated bootloader bodies.

`runtime_double_helpers_422628.c` is 8,892 bytes with SHA-256
`86d7a2c00a7c00b6388a4e096c0767d5dfc752470c45dd6f204e3284d9c4515f`.
Three strict relocations bind the two internal wrapper/core edges and retained
range-error tail. Fourteen external direct calls and two internal calls enter
only reviewed starts. Five focused tests pin all bodies, alignment, callers
and Apollo twins; exercise normal, subnormal, zero, nonfinite, signed/unsigned
conversion and arithmetic behavior; and compile both reviewed Cortex-M55
profiles.

Canonical accounting becomes 20,259 source-owned, 16,528 generated patch, 16
alignment, and 127,037 retained official bytes, including 362 cave bytes and
4,672 exact in-place bytes across 254 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,613,691-byte flash plan has SHA-256
`3c5b51bb1895ab421f3fc9117b6ce34be0898b1bb59222b05aff12cee5bec4a6`
with 6,629 placed, two unresolved, five container-only and six protected
regions.

No hardware operation occurred. VFP exception flags, retained range-error
state, caller ABI and boundary behavior require authorized Apollo510 evidence.
That evidence is unavailable because no authorized responsive right temple
exists and the left temple must remain stock. Firmware-wide functional
completeness is not claimed; after the retained two-byte alignment, the next
executable body begins at `0x00422874`.
