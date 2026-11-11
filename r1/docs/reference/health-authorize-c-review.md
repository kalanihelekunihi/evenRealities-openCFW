# R1 health authorization coordinator in C

The stock `0x6b27c` coordinator now has an ordinary C implementation in `native_health_authorize.c`, called by lifecycle startup. It clears the 28-byte UUID buffer, all 68 bytes of key scratch, and the 16-byte authorization descriptor. Negative key-read results return minus one; zero and other nonnegative results continue. The descriptor carries key and UUID pointers, the UUID length in its low byte with zero padding, and the timestamp. The engine setter's result is returned without reinterpretation. Logging retains the stock branch order and repeated live mode reads.

REA supplies the authenticated function body and instruction evidence. The [receipt](health-authorize-c-review.json) binds that evidence to compiled objects and replay results:

- 2,268 direct stock/C pairs cover signed key status boundaries, engine success/error, UUID lengths 0/24/27, partial key writes, six log-mode sequences and UUID mutation during timestamp acquisition.
- 689 lifecycle startup/reset/event pairs execute the C coordinator alongside the existing C profile, storage, crash and activation providers. Lower identity, key-read and engine-setter calls remain modeled.
- Four deliberate defects are rejected: treating zero key status as failure, discarding the setter result, using a fixed UUID length and leaving the last four key bytes uncleared.

Comparisons include observable call order, full private buffer contents, descriptor padding, return status, stack balance, callee-saved registers and masks. Private scratch addresses are normalized by contents; this is not proof for lower providers retaining those addresses beyond the synchronous call.

The normal report is `build/sources-goal-r1-health-authorize-c/report.json`: 726 units compile, with no failures or duplicate strong symbols. The coordinator import resolves while `r1_health_authorization_key_read` and `r1_health_auth_parameters_set` become explicit, increasing application imports from 178 to 179. Bootloader imports remain 34. Only the lifecycle object changes from the preceding checkpoint; the new coordinator is added and 724 existing objects remain unchanged. Both manifests pass `make sources-check`.

The key reader, engine parameter setter and engine initialization remain unfinished. Physical hardware startup and complete source-only firmware linkage are not established. No byte identity is required or claimed.
