# Flash protection setter candidate

Source: `runtime_gx8002_flash_protection_set.c`. Stock instruction evidence:
package 0x159b8..0x15aa4; interface lock/unlock signatures agree with the
already authenticated NationalChip gx_flash.h. This candidate is not admitted.

The setter initializes a two-byte command buffer, reads selected device and
profile, then zeros the caller's actual-length output. Missing profile or
entry pointer returns zero only for a zero request, otherwise -1. It snapshots
the JEDEC identifier before waiting, then reloads the device/profile and
snapshots the entry pointer and count. The ordered table walk stops at the
first protected length greater than the unsigned request. Each accepted entry
replaces both expected status values and masks; no accepted entries leaves
all four values zero. Entries after the first larger length are not searched.

Only saved JEDEC manufacturer 0x5e or 0x85 proceeds. The setter reads both
status registers and forms each command byte as (old & ~mask) | value. It
waits, enables writes, sends command 1 with two bytes, waits again, then calls
the recovered protection-status query. A return of -1 propagates without
copying the observed length; other returns copy it and return zero. Lock
passes the requested length with a local output; unlock passes zero.

Native macOS C-SKY compilation produces setter204/204 bytes, lock14/16 and
unlock16/16. Unlock is byte-identical. Four explicit volatile LD.B intrinsics
avoid redundant GCC extensions while retaining ordered full-register loads;
the rest is C. No extracted executable bytes are used. The initial all-C
narrow-load version was212 bytes; the final version links with normal overlap
checking enabled. Decoded call/access comparison, alias behavior, frame/ABI
verification and admission remain outstanding. No hardware was accessed.

Initial setter qualification passes 12,960 decoded comparisons. Cases cover
unsigned request boundaries, missing profiles, empty/sorted/unsorted tables,
manufacturer acceptance, helper-driven device/profile replacement, command
contents, and query return propagation with two caller-clobber seeds. The
original and C both use a 40-byte frame (32 saved-register bytes plus eight
local bytes). Private stack initialization differs: two stock byte writes
versus one source halfword write. The checker tracks initialized local bytes,
checks command/query pointers, and rejects uninitialized reads. External
accesses remain ordered and width-checked. Five oracle/rejection tests pass.
Wrapper execution, broader status/mask coverage, aliases and admission remain
pending. Helper contracts are modeled; physical hardware remains unqualified.

Expanded qualification passes 78,496 setter cases, including every independent
status-byte pair with varying masks/values, plus 60 lock/unlock wrapper cases
and 32 output-alias cases. Wrappers use an eight-byte frame, forward the
correct request/local output pointer, and preserve arbitrary setter returns.
Alias locations cover the original profile entry pointer, JEDEC identifier,
scanned entry length, and already-loaded original device profile pointer.
The oracle propagates the initial zero write into subsequent reads: clearing
the identifier prevents the command, while clearing an already-loaded profile
pointer does not retroactively replace the saved pointer. Nine tests pass.
Admission adapter and full package integration remain next; helper contracts
are modeled and protection-profile initialization is still unrecovered.

Setter and wrappers are now integrated through the reviewed admission adapter.
All 155 native macOS codec tests, package assembly and artifact verification
pass. This replaces 236 retained bytes with 234 compiled bytes and two fill
bytes. Protection-profile initialization was located at package0x166d8 and
its three tables inventoried separately; source ownership and startup-path
qualification of that data remain outstanding. No hardware was flashed.
