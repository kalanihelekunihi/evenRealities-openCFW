# Independent review 2367

**Result:** PASS_SCOPED.

Receipt bf03d9c66279ea4b8e7dddebd4bed0a2a3af003c4b5bc57599262b60be58cc38 pins the source and complete body [0x4E6C,0x4F54); evidence hashes match. An independent isolated replay passes all 1728 fixtures.

The 232-byte body decodes continuously. Original 4E6C runs one actual outer-index iteration (initial zero; increment to one then exits) and loops over row count. Source addressing reduces to row.word4+10*item index; destination to row.word28+2*item*cachedStride because outer index is zero. Original 4E58/4E36/4E60 helpers execute in the decoded order, including 4E36's fresh row-half116 read after its destination store and optional-pointer retention branch. The oracle's ordered writes and complete memory match across count/index/type/stride/copy-bit/mode combinations.

The replay checks helper-entry ordering, all monitored memory, preserved R4-R11/SP, and the recorded incidental R0. No mismatches occurred.

**Limits:** Flags and count are stable in these fixtures; child-induced flag mutation and resulting optional-pointer retention are not exercised. Source, destination and control regions are distinct. Arbitrary pointer aliasing, concurrent mutation and physical effects remain unresolved. R0 is incidental, not a status contract. Private evidence only; accepted:false.
