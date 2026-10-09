# Read-only prepared holdout controls

Await independent review of the completed 14.2 three-function matrix before
broader inference. No holdout compilation has run.

Use unchanged pinned `drivers/source/cy_scb_common.c`, SHA-256
`e0cd9973c871649e30cab5e6f4124f1b5bef696eb693c3a796d2c5f08968d3c1`,
with the same authenticated14.2.1 compiler, recorded flags and header environment.
This tests a separate source translation unit, not another MSCLP peer.

| Holdout | Address | Bytes | Original SHA-256 |
| --- | --- | --- | --- |
| Cy_SCB_ReadArrayNoCheck | 0x9218 | 56 | `07627776d2bc275029e974a40d0944d6b87502cfea118880b8d60d6c3fa97cc7` |
| Cy_SCB_WriteArrayNoCheck | 0x926E | 56 | `ba8eabab79e5f3cf46e4b9b7bd76456a262ed1ff7d3780885a747f9eb6e1b434` |
| Cy_SCB_WriteDefaultArrayNoCheck | 0x92D6 | 16 | `ec65352149705e5d99247c6304f60772bc6feacccd2c020952f45b32e2c531b1` |

All target slices were freshly checked against official touch SHA-256
`0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`,
32-byte payload header, flash base0x3300. Hashes agree with symbol rows;
symbol names remain existing inferred bindings until compiled correspondence.
No recognized campaign contract scope overlaps this selected interval.
ReadArrayNoCheck already matches10.3–13.3 under prior experiments and is a
generalization control, not a release discriminator. The other two no-check
functions supply independent directions/constant-data behavior. Wrapper
functions with external call relocations are excluded from raw-byte equality.

Compare complete sections and report all differences/lengths; require absent
relocations or account for them. Preserve preprocessed/object/dependency hashes.
Do not change inputs or flags after seeing a mismatch. Any matches support
selected generalization, not a unique producing compiler or complete payload.
