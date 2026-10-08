# Touch EEPROM initialization and actual configuration

New canonical [initialization source](../../components/touch/eeprom_init_offline/README.md) is additive to the preserved `eeprom_offline` module. `init.c` reconstructs provider creation, geometry/range helpers, library initialization and the application wrapper. Its source-defined twelve-byte factory configuration matches the locked image's reset-copied data. No production payload, accepted checkpoint, index or shared campaign was changed.

## Actual defaults, proven from bytes and reset instructions

The reset loop at0x4692..0x46d6 reads a copy-table record at0xb578: source0xb58c, destination0x200004c0, **241 words /964 bytes**. The following zero table clears428 words/1712 bytes from0x200008a8. Both original instruction slices execute in the fixture; this does not execute hardwareSystemInit or whole reset/boot. The first twelve copied bytes are `00 01 00 00 00 02 01 01 00 00 00 00`.

| Configuration | Actual value |
| --- | --- |
| Logical capacityu32+0 |256 bytes|
| Simple modebyte+4 |0: extended|
| Wear factorbyte+5 |2|
| Redundancybyte+6 |1|
| Blockingbyte+7 |1|
| Initial physical baseu32+8 |0, patched by application initializer to0xe400|

Installed provider getters at0x4784/4788 both return128; initialization therefore produces row128, sector128, historic capacity64, payload capacity48, four logical rows, wear2 and redundancy1. Main plane is0xe400..0xe800; mirror plane0xe800..0xec00; total2048 bytes. This region is **outside the OTA runtime payload**, which ends0xb980. The OTA supplies configuration/code, not a captured persistent storage image.

The library configuration at0x200004c0 is separate from the eight-byte UNVE application record at0x200009d0: magicu32, baselineu16 and parameteru16. Do not confuse the256-byte library allocation with that eight-byte saved record.

## Recovered call flow and contracts

`app_init(0x34d8)` → `Cy_Em_EEPROM_Init adapter(0x8a38)` → provider creator0x486c → `Init_BD(0x898c)` → erase-size/program-size getters → program geometry0x828c → configuration ranges0x8220/physical size0x8200 → last-row scan0x7fa4.

Init_BD rejects null config/context/provider before clearing the context, returning093e0000. With valid pointers it clears32 contextbytes, retains the borrowed provider pointer, copies base/mode/capacity, computes sector/row geometry and logical row count, then validates config/range. Invalid config fields, zero capacity/base or out-of-range geometry return **093e0002**, not the dispatcher's093e0000. Unsupported blocking0 returns093e0000 after geometry validation. Simple mode coerces wear to1 and redundancy to0. No config pointer is retained; the provider must remain valid for the context lifetime. No heap allocation/free or SROM request occurs during initialization.

Initialization calls last-row scan but **discards its status**. The application sets readyflag0x200008c4=1 after library success; any already-nonzero flag makes the wrapper return immediately. It does not read/check the UNVE record. The legacy wrapper's success-on-redundant-status4 case remains present, but the observed Init_BD scan status is discarded. The SDK adapter's provider-create failure branch returns0, but fixed nonnull provideraddress0x20000ed4 makes that failure unreachable through the installed creator; no invented callback failure is claimed as stock reachability. Adapter config pointer validity remains a precondition, unlike the guarded inner Init_BD.

Raw32-bit addition and16-bit row-count truncation are preserved. A constructed capacity0x400000 configuration truncates the row count tozero and can pass initialization with physical range sizezero. The actual application selects256 bytes; this synthetic direct-API case is not an observed application configuration or a recommended API policy.

## Original-instruction validation

Independent source ELF SHA **c473c306afd27bba6bd7e1cc9427f53bedc16bd85c0cb42ebe7341cd4fa0635c** passes **1,402** native/original cases without function-entry cuts. Compared returns, complete context, config/readyflag, provider identities, ordered metadata callback arguments, unchanged storage, SP andPRIMASK. Storage is synthetic; the guest memory/stack are a test fixture, not physical memory or timing validation. All218 instructionbytes in Init_BD and application wrapper execute across this suite; adapter failure outcome is not forced.

There are1,344 direct configurations over zero/erased/valid/corrupt/torn/wrapped rows, capacities0/1/64/128/256/1024, mode0/1, wear1/2/7/10, redundancy0/1 and blocking0/1. Twenty-four app cases cover eight patterns and initializedflags0/1/255;27 additional invalid/truncated configurations andseven null-argument combinations complete the suite. Three negative controls are rejected: wrong configuration errorcode, acceptance of unsupported nonblocking mode, and failure to coerce simple-mode wear. Source-defined factory data is checked against the twelve locked reset-copied bytes.

For actual defaults and fresh readyflag0, all eight synthetic row patterns return application success and set readiness. Selected last-row addresses differ:

| Pattern | Selected pointer |
| --- | --- |
| Zero, erased or all-corrupt |0xe400 fallback|
| Valid equal-sequence main/mirror |0xe780 main|
| Main-corrupt, newer mirror, torn last-main |0xeb80 mirror|
| Wrapped sequence |0xe480, sequenceFFFFFFFF outranks small wrapped values|

These are fixture results, not device storage observations. Initialization success does not establish valid saved configuration or persistence. Actual read/record validation and bootstrap policy remain separate.

## SDK/source inference pursued after initialization

The pinned [EEPROM2.60 source](https://github.com/Infineon/emeeprom/blob/6cacf37b5cfec2dc9acf1a2c222c1e3038d03bd9/source/cy_em_eeprom.c) adds five exact compiled bodies: GetPhysicalSize30,CheckRanges108,ComputeEEPROMProgramSize84,Init_BD172,Init64 — **458 bytes** including literals. GNU13.3.1-Og Cortex-M0+ Thumb, short enums and explicit data placement reproduce all resolved branch/literal bytes; no masking. This builds on the previous13 exact functions/1476 bytes. Exact producing revision remains unresolved; earlier2.70 candidates share the prior selected bytes.

A further finite provider check resolved the remaining creator mismatch. Block-storage1.1/1.2.1 reproduce nine bodies/234 bytes but their108-byte creator installs nonnull nonblocking callbacks. The [1.3.0 PDL backend](https://github.com/Infineon/block-storage/blob/0a9781309e0e1832d12e99cdf1d0f75843396a76/source/mtb_block_storage_pdl.c) instead sets both slotsnull and reproduces **all ten stock provider bodies/330 bytes**, including creator96. Its public header preserves the old CAT2 creator name as an alias. Source/header/license are retained unmodified under [third-party/upstream/infineon-block-storage-1.3.0](../../../third-party/upstream/infineon-block-storage-1.3.0/README.md), Apache-2.0. The flash error-discard behavior is visible in this exact source family; it is not an invented approximation.

Joined EEPROM2.60 + provider1.3 source reproduces28 selected functions/2264 bytes. A separate **1,402-case SDK/original initialization suite passes**, loading selected SDKsections and borrowing actual original memory/division primitives. It has no function-entry cuts but is **not an entirely native-source closure**: those borrowed primitives and uncalled flashdriver remain explicit boundaries. WholeELF segment padding is excluded to preserve the original reset-copy fixture; this is not a loadable production image.

The follow-up also matches EraseRow100,WriteSimpleMode172,Write dispatcher52 andErase API276 — **600 further bytes**. Combined selected attribution is **32 unique functions /2864 bytes**. CRC60,CopyHeaders392,extended write252 andboth124-byte wrappers are not admitted as exact SDKcompiled bytes. Our existing independent history/write source still has its own bounded native validation; matching source family is distinct from matching every implementation byte. The prior515-case CRC semantic comparison remains valid, not a byte-match claim.

## Remaining actionable leads and actual boundaries

| Source/lead | What is established | Next action or boundary |
| --- | --- | --- |
| Infineon EEPROM |Actual config; independent init/read/history/write tests;22 selected SDKfunctions/2534 exact bytes|Source is available. Compare unmatched wrappers/merge/extended-write compiler or revision differences; trace configuration bootstrap0x395c and erase/default-write behavior. Not exhausted.|
| Infineon block-storage PDL |All ten provider bodies/330 exact bytes; pinned Apache source retained|No source acquisition blocker for this installed provider family. Physical flashdriver/SROM behavior remains separate. Unique producing release not proven.|
| PDL/core/CMSIS |Previously sealed six FIFO bodies254 exact bytes and bounded I2C/helper tests; reconstructed flash control flow|Current public flashdriver includes wait behavior absent from stock, and I2C extents differ. Further bounded revision/configuration inference is possible; no global source absence claim.|
| Runtime/configuration glue |Actual reset data selection and complete init contracts recovered|Bootstrap0x395c, record/magic validation and default recovery are actionable. Historical0x3a38 load label is also misleading: its instructions call writeadapter0x3568. Shared catalogues remain untouched.|
| Resident SROM and persistent data |Outside the locked OTA; no captured storage/physical trace|Needed for physical programming, failure/torn-write, durability and timing conclusions. Not a blocker to further offline decompilation.|

Other vendors' prior source-by-source limits remain in [the earlier assessment](../dependency-followup-2026-10-08/REPORT.md); this batch does not pretend to freshly exhaust their sources or other agents' ongoing work. No global source-exhaustion stopping condition is established. No hardware, complete-source, wholeOTAbyte-equality or productionreplacement claim is made.
