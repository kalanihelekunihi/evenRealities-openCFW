# Cached health-settings getter in C

The standalone implementation described in this historical receipt was later
consolidated into the existing canonical getter; see
[the consolidation review](record-read-consolidation-c-review.md) for current ownership.

`runtime/native_record_read.c` supplies missing stock 0x735e0, closing
r1_event_service_000735e0 in the normal application composition. Its explicit
four-core-register C entry takes the destination in R0 and three fallback
words in R1/R2/R3. This is the machine call made by the existing assembly
settings callback, not a new one-argument C interface. It initializes a local
three-word record from those arguments, reads twelve bytes through the live
health-settings KV handle and copies three words to the destination in order.
Null output does nothing. The read result does not suppress copying; partial
and nonwriting reads retain the corresponding fallback bytes.

Fresh REA analysis and bytes agree with the locked stock entry. Verification
executes normal source objects against stock: 520 modeled direct-read cases,
80 direct cases with actual cached KV/memcpy and 384 executions through the
existing normal compiled settings callback. Direct cases cover null and
unaligned destinations, all fill lengths from 0 through 12, arbitrary seeded
fallback words, error statuses, matching/mismatching cached sizes and critical
callbacks that mutate cached payload data. Callback cases exercise length
rejection and the getter's record handoff to the update boundary, including
failed reads. KV and memcpy execute in the integrated cases; critical-section
callbacks are modeled. Callback logging mode is zero and its later update
boundary is modeled, so a full settings-update lifecycle is not claimed.

Comparisons include ordered KV access, copied bytes, node/input/output state,
callback update record, guards, final saved registers, SP and interrupt masks.
C execution is prohibited from entering stock instructions. The API is void;
incidental R0-R3 outputs, private frame locations/content, callback live register
allocation, arbitrary private-stack aliases, faults and concurrency are
excluded. The explicit fallback words preserve observed failed-read behavior;
there is no invented default health record. Physical flash persistence is not
verified by this cached getter.

Four compiled defects are detected: zeroed fallback words, short read, short
copy and suppressing copies after read error. A clean final baseline is rerun.
The companion JSON records evidence identifiers, hashes, test results and the
composition audit. All 783 prior nongenerated object hashes are unchanged;
the two generated bootloader objects retain identical allocated bytes and
relocations despite metadata changes. No source-plan qualification is added.

R1 now compiles 786 units (704 application, 82 bootloader) without failures or
duplicate strong symbols. Application imports fall from 107 to 106 with none
added; bootloader linker-metadata imports remain 22. Strict source bootloader
linking succeeds. Global source checking retains the unrelated unlisted G2
resident_rom_thumb_set.S failure. Full application linking remains unfinished.
