# Experimental Apollo peripheral power C candidate

`power.c` follows the complete branch structure of pinned Ambiq Apollo510
`am_hal_pwrctrl_periph_enable` and `am_hal_pwrctrl_periph_disable` in
`third-party/upstream/ambiqhal-apollo510/mcu/apollo510/hal/am_hal_pwrctrl.c`
(commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`). The repository's
retained source contains the upstream copyright and BSD notice. The two
functions map descriptors, GPU and clock state, Tempco/SPOT, critical MMIO,
readiness timeout, CRYPTO/OTP, DEBUG, shared domains and release paths.

The product configuration, callback table, clock state, register addresses,
status codes and lower routines are external typed contracts in `power.h`.
They require a source-backed binding. This translation unit intentionally
supplies no guessed values and is not selected into the production archive.

The stock ordinary/audio SPOT callback results are ignored on both enable
and disable paths (native 0x47f660, 0x47f67c, 0x47f8e4, 0x47f8fe), and this
candidate now follows those native branches. Other stock differences still
require product-state evidence. Stock domain indices include
CRYPTO low byte 0x17, OTP low byte 0x1d and audio 30; the generic enum is not
assumed here. The stock shared group at domain 3 uses mask 0x1e, but other
shared masks remain unbound. Existing stock/source power fixtures cover 96
bounded cases but use a sentinel for other active branches; they do not
validate this full experimental unit. No elapsed-time or hardware behavior
has been measured.
