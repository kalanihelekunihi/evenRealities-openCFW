# R1 health event consumers in C, 2026-11-10

`r1/src/application/runtime/native_health_event_consumers.c` now defines six
stock event services (`0x8a7f4`, `0x8a80a`, `0x8a83e`, `0x8a8ae`, `0x8a8d8`,
and `0x8a8fc`) in C. The six handwritten naked assembly bodies are gone.
The existing unit in `r1/src/sources.json` remains the sole owner of their
symbols. The C keeps the stock value gates, existing or newly written
timestamps, packed five/six-byte records, and storage/notification order.
The HRV service retains the stock null-pointer fault path.

An ignored ARM emulator harness in
`build/r1-health-event-consumers-pure-c-20261110/` compares the pinned
official application and the compiled C object. **1,440 paired cases** pass
across six services, threshold edges, empty and populated timestamps, two
clock returns, sample mutation during the clock provider, four caller length
values, and null cases for the five services that accept them. It compares
provider calls and record bytes, payload writes, stack restoration,
callee-saved registers, and interrupt masks. A separate null-HRV check
observes `UC_ERR_READ_UNMAPPED` on both stock and C. The provider bodies are
modeled, so this is not a live storage or hardware test. The normal manifest
object has the same SHA-256 as the tested object, and preserves all six
exported names and kinds.

The stable R1-only source build at
`build/sources-r1-health-event-consumers-stable-20261110/report.json` compiles
886/886 application and 82/82 bootloader units with no known failures or
duplicate strong symbols. The strict bootloader links with a valid vector.
The strict application receipt at
`build/sources-r1-health-event-consumers-stable-20261110/app-link/report.json`
still has 36 undefined symbols and **25,160 bytes** of full flash overflow,
96 bytes more than the preceding C/assembly mix. A complete application
executable, device behavior, and byte identity remain unverified.

A repository-wide `make sources` run compiled every payload with no known
failures or duplicate strong symbols but returned nonzero after a concurrent
G2 manifest edit. The subsequent shared `make sources-check` passed. The
stable R1-only source build above exited successfully.
