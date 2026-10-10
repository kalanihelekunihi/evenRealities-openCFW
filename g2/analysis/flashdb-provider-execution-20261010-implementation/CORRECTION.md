# Correction to sealed predecessor report

The report in ../flashdb-provider-config-20261010-implementation remains sealed. Its sentence “A nonzero status result suppresses that second call” was too broad. At 0x5445D2 stock narrows the status result with UXTB, and at 0x5445D4 compares that low byte to zero. Therefore a **nonzero low byte** suppresses flash-write; raw R0=0x100 proceeds, while 0x101 suppresses it and returns 1. Final flash/status returns also narrow to eight bits. This correction supersedes that sentence and the unqualified wording in the earlier final response. The independent audit and current runtime receipts agree.

No parent init/lock/unlock offset observed here uniquely establishes FAL mode. Those offsets only match the configured candidate; alternative storage configurations were not tested.
