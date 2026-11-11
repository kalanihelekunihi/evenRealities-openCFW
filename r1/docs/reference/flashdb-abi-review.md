# FlashDB short-enum ABI repair

The R1 FlashDB providers now use one explicit short-enum ABI. This repairs a
real RAM-layout mismatch in the Clang profile, not merely a linker warning.
FlashDB 2.0.0 remains pinned at `4e5677408256f82d47cd56a6b04605dcee35ed9a`;
no vendor source, timestamp width, storage configuration or layout assertion
was changed.

## Native evidence and compiler layouts

REA/Ghidra 12.1.4 checked the locked application
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
mapped at 0x27000. The observed bodies are `fdb_tsdb_control` at 0x63694
(242 instruction bytes), initialization at 0x63814 (360 B), and sector-info
reading at 0x87C24 (360 B). The control body's 12-byte gap at 0x636A2 is
its byte-sized TBB dispatch table; it is data, not missing instructions.

Native control reads `last_time` at +80 and reads/writes rollover at +92.
Initialization writes the get-time callback/max-length pair at +84/+88
and rollover at +92. Sector-info code writes and reads its status as a byte
at +1. These operations agree with the existing recovered layout assertions.

| Field | Old Clang profile | Short-enum profile |
| --- | ---: | ---: |
| Store/TSL enum width | 4 | 1 |
| Sector-info size | 48 | 40 |
| Sector status offset | 4 | 1 |
| TSDB C object size | 108 | 100 |
| Last timestamp offset | 88 | 80 |
| Rollover offset | 100 | 92 |

The pinned ARM GCC 9 profile already defaulted to short enums; its measured
layout was correct before the change. Both Clang profile
`r1-application-16` and GCC profile `r1-application-49` now specify
`-fshort-enums` explicitly. The recovered kernel TU inherits that same flag
instead of carrying a private per-unit override. Its unchanged extent and
offset assertions will fail if the Clang profile drifts again.

All 18 measured serialized-layout fields remain identical across both
compilers and both enum modes, including the 80-byte sector-header and
32-byte log-index geometry. This is a RAM ABI repair; it does not introduce
a storage migration. The GCC layout-probe object is byte-identical with or
without the explicit flag under the pinned compiler's current default.

## Execution and build verification

Each configured compiler passed **52 stock/source control cases**. The old
Clang configuration passed 40/52; its twelve mismatches were rollover
set/get and last-time reads at the wrong offsets. The probes compare the
backing bytes, argument bytes and ordered writes. They use valid database
preconditions and omit assertion, NULL-database and file-mode logging paths.
The preexisting `FDB_PRINT` no-op configuration is unchanged; complete
logging equivalence is not claimed.

The configured-profile probe objects are byte-identical to the short-enum
objects used by the execution comparison. All 486 application and 74
bootloader units compile, with no expected failures or duplicate strong
symbols. Diagnostic GNU `ld -r` compositions of the 436 participating
application objects and 74 bootloader objects succeed with no new undefined
symbols (253 application / 34 bootloader). The later
[composition build update](source-composition-review.md) configures these
same checks in the normal R1 manifest and verifies the identical import sets.

The application still has 34 participating objects marked with the wide-enum
ABI attribute and 402 with the small-enum attribute, versus 40/396 before
this fix. The remaining mixed-ABI warnings are not suppressed. An attribute
alone does not prove an incompatible shared structure; those other interfaces
still need review. Successful relocatable linking does not establish their
compatibility, final linking, original-compiler identity or physical storage
operation.

The first smaller REA import misinterpreted out-of-slice logging calls and
truncated assertion paths. Expanding the analysis wrapper to the unchanged
full application resolved those call-boundary problems. This does not turn
the observations into independently reviewed whole-image coverage.

Raw observations, layout vectors, counterexamples, switch targets and result
identities are retained in [the evidence JSON](flashdb-abi-review.json).
Probes and before/after build artifacts are under
`build/goal-r1-flashdb-abi/`. No qualified source-plan selection, firmware
oracle or workflow gate changed.
