# R1 typed structured logging in C

The locked application routines at `0x915a8` and `0x41d30` route and pack
typed log records. `r1/src/application/board/structured_log.c` now supplies
the variadic entry using the same mode and BASEPRI gate as the existing
`0x91638` format logger. `structured_encode.c` packs the typed payload:
up to eight 32-bit values, two 16-byte strings, or one 16-byte string
followed by four values. It retains stock severity filtering, timestamp,
sequence and 12-byte record header construction, then calls the existing
source-owned cache append provider.

An ignored host fixture at
`build/r1-current-20261110/structured_typed_test.c` passed with AddressSanitizer
and UndefinedBehaviorSanitizer. It checks numeric payloads, short and truncated
strings, mixed payloads, sequence and timestamp fields, and severity rejection.
The fixture uses a host copy with only the ELF section attributes removed;
the ARM source itself is unchanged by that host translation.

The 952-unit R1 build at `build/r1-typed-log-c-20261110/report.json` compiles
both payloads without failures or duplicate strong symbols. The typed logger
import closes without adding a lower import. The strict bootloader link passes.
The strict application receipt at
`build/r1-typed-log-c-20261110/app-link/report.json` has 50 unresolved
references and 219,016 bytes of FLASH overflow. This C source is not yet
byte-qualified against the locked routine, and firmware boot remains untested.
