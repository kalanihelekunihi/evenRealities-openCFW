# Six-component address accounting extension

Verified selected mapping inventory, existing evidence only. Target s200_v2.2.6.10; exact consumed hashes, half-open payload-coordinate ranges and all complements are in inventory.json. inventory.csv gives module/subcomponent rows with percentage of full stored payload and missing receipt join fields. inventory.py reproduces all results without compilation. Prior sample/measure.py/results.json are preserved.

|Component|Payload bytes|Mapped function envelopes|Unmapped by this inventory|Pseudocode-associated|Validated listing lower bound|Mapped C lower bound|Compile-C lower bound|Bounded behavior-C lower bound|Exact C lower bound|Integrated replacement|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|codec|326092|92560|233532|92560|36484|0|0|0|0|0|
|ble_em9305|211948|15190|196758|0|210072|15190|0|0|0|0|
|touch|34464|27879|6585|27879|15616|632|632|0|632|0|
|case|55784|43072|12712|43072|4320|0|0|0|0|0|
|apollo_bootloader|148599|120432|28167|112506|9594|0|0|0|0|0|
|apollo_main|3523396|1628382|1895014|1555524|17484|376|376|376|0|0|

The stage columns are orthogonal and overlap: never sum them. Mapped-function envelopes include failed pseudocode rows; mapping is not exclusive executable classification. EM has only the selected C envelope inventory rather than a complete discovered-function catalogue, so its mapped/unmapped comparison is especially partial. Codec totals cover five historical program images; parents/decoded aliases are not counted twice. All mapped+unmapped sums equal the corresponding full official payload size. Unmapped means outside this selected inventory, not absent C or proven binary-only.

Zero lower-bound cells mean no joined verified range in this extension, not zero available C. Substantial current candidate graphs exist; a full per-range selected-source/object/receipt join is absent for those cells. Current reference packaging still copies100%original payload; every integrated replacement column is0. Actual binary-only/unrecoverable bytes are unknown.

## Verified C and module boundaries

Main TLSF four entries contribute376mapped/compile/bounded-behavior bytes of matched upstream C; complete entry bodies are all unequal to stock. Touch three upstream PDL MSCLP entries contribute632mapped/compiled/exact bytes; these are not newly recreated C. Source/data declaration and complete production link remain separate. Per-function sample hashes and prior full compile receipts bind these local lower bounds; they do not prove all dependency/runtime or hardware behavior. New recreated C has an EM static15190byte envelope union; the per-range selected object and behavior joins remain missing, so it is not promoted to compile/behavior/equality. Codec1606exactsource-assembly bytes from prior reviewed DSP receipts are an assembly-origin measure, deliberately excluded from C cells pending a complete coordinate/object join here.

CASE CSV module rows are inferred ownership categories: FreeRTOS5814bytes/86positive rows, first-party18330/90, STM32HAL1324/15, CMSISstartup310/15, unresolved14886/222; combined40664unique table-envelope bytes. Seven zero-size task rows remain in sample results as unmapped by that table; they must not be given guessed endpoints. CASE raw function inventory43072bytes differs from its attribution-table40664bytes; these are two cohorts/stages, not inconsistent source totals. EM subcomponents are inferred source-file labels, not physical flash partitions; controller_init10766unique static bytes is the largest sample.

Physical regions and FlashDB kvdb/NVdb partitions describe memory/storage boundaries, not semantic code-module boundaries. Raw ARM catalogue is not partitioned into semantic modules here; its module row explicitly says recognized flash functions. Codec nested-program boundaries have stronger container/image evidence but runtime address/base can be hardware conditional. The script uses authenticated nested content and source-span/package-offset mappings and asserts original byte equality for each codec image before translating intervals. EM listing ranges already use full payload offsets; adding the record1060offset twice would be incorrect. Touch begins at its recorded flash base, not VA0; script uses the authenticated base.

## Classification and incomplete joins

Code/data/padding partition remains unknown for these function envelopes. Container/header/image identities are authenticated structural facts, not exhaustive classification. Lower-bound listing bytes may serialize data/literals; pseudocode intervals likewise do not establish code-only coverage. CSV missing_join_fields names exact blockers: semantic module owner, range endpoints where absent, exclusive instruction/data classification, source kind/path/hash, selected compile object/hash/command and object-to-original range binding, behavior receipt/provider scope, complete-byte/relocation receipt, generated absolute image composition. Name/comment/crosswalk matches cannot supply these fields.

Boot selected source crosswalk identifies header/comment/name/manual/address leads and recognized903functions; it expressly disclaims semantic/placement equivalence. It cannot promote every lead into compiled-C coverage. Similar partial EM label and codec seeded-symbol crosswalks are not complete function or byte maps. Thus this accounts all selected available mapping inventories, not every possible new file or every function in firmware. Newly finished source receipts need the same joins before counters change.

## Validation

Six payload hashes authenticate. ARM metadata spans are checked against authenticated image bytes and RUN identity (10499recognized envelope records); interval union/complement assertions are reproducible. Codec five nested contents authenticate and match their exact official payload slice. Prior exact TLSF/PDL raw-byte hashes are independently checked by sample/inventory scripts. Detailed source-build dependency receipts remain predecessor evidence; this accounting does not execute or recompile them. No firmware/device, denied phase, canonical/index/worktree/branch/commit/push changes.

Reliable full coverage now requires filling the missing joins and reviewed code/data classification, not recovering new code as part of this task. Percentages in CSV use each full stored payload denominator; complement percentages are representation gaps only. This is the documented evidence boundary.
