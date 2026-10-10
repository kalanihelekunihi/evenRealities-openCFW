# FlashDB cache-count discrimination

Four original-byte RAM cache-boundary fixtures pass, plus two independent ARM32 header-layout variants. The complete database stride alone does not establish cache counts; authenticated cache offsets and loop bounds independently constrain the pinned FAL/short-enum candidate to **64 KV entries and64 sector entries**. This is distinct from the implementation's ten write-granularity/enum/provider-offset probes.

## Search and inputs

Read the current implementation/audit configuration reports, consolidated G2 libraries/memory-map/config references, recovered G2 FlashDB header, R1 config, existing source-interface evidence and emulator NOR-profile/external-NOR docs. G2 references already claim64/64, but the historical research-audit path they cite is absent in the current checkout; no missing historical file was recreated. R1 uses a different TSDB/granularity configuration and is not a G2 constraint. Emulator reports genuine FlashDB formatting over modeled NOR; this neither independently identifies cache counts nor validates physical storage in this experiment.

No acquisition was needed. Header/source files are read-only references to existing pinned official FlashDB2.1.1, commit714d6159e7e6afb267a3953756abca445c350e61. fdb_def.h SHA256748d07c650c6c0be98b380af4af43a556791f9a37cc205167176df0c7ec8e10b is backed by the earlier blob-interface official-source receipt. fdb_kvdb.c SHA25696e09b3f7b8b0dc77b51cb387701e4e9ef7a5cbce2eaa606380962aff25582ac is backed by the provider-config source receipt. Apache-2.0 notices remain in their original files. Replay checks both hashes.

## Header-layout inference

Two new header probes use Apple clang ARM32 Thumb Cortex-M4, short enums, FAL/KVDB, write-granularity1 and default name limit64; no compiler-version or producing-flag identity is asserted. Constants are extracted from ARM ELF .rodata, not native host offsets. Exact command/object hashes are in results.json.

| KV/sector counts | Database bytes | KV table offset | Sector table offset | Node bytes KV/sector | Final user_data |
| --- | --- | --- | --- | --- | --- |
|64/64|2220|168|680|8/24|2216|
|61/65|2220|168|656|8/24|2216|

Under these fixed headers/configuration, size is168+8K+24S+4, so a2220-byte object gives K+3S=256. There are85 positive integer count pairs with that size; the explicit61/65 counterexample demonstrates the ambiguity. These formulas do not rule out another header revision/packing/configuration. Within this pinned candidate, authentic sector base680 and KV base168 establish K=(680−168)/8=64; the independently bounded sector loop establishes S=64. Name-limit/alternative parent-layout discrimination remains implementation-owned; this test fixes the already supported candidate and does not infer exact name limit.

## Authenticated source/byte and RAM execution

Locked main hash36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863. Source-correlated candidate sector getter543CC0..543CEC is44bytes, hash0d15a85efe5382c95472f445049055bc2bc4c863c55684c37857445b04581bcc. It compares loop index with64, uses24-byte stride, loads addr atdb+684+24i and returns node atdb+680+24i. No external providers execute. Last-slot hit returns index63; miss with readable matching poison at index64 returnsNULL. Both fixtures perform exactly64 four-byte reads at the independently predicted in-table addr fields, preserve the database and return ABI, and never read the poison.

Candidate update_kv_cache543D1C..543E28 is268bytes, hash401e21dae4030689d43d37aad6726150e094a8d5f2b263dac43d0b1d01b40932. Its source-correlated field accesses are CRC16 at168, active16 at170, addr32 at172, eight-byte stride; loop/count/activity constants are64. Two fixtures execute original bytes: match at index63; full-cache miss with a matching readable poison just beyond index63. Both read slots0..63 only. The latter follows min-activity replacement instead of accidentally selecting poison index64; source and stock produce identical full512-byte cache contents. Database prefix and entire sector/guard region stay unchanged, as do SP/r4-r7.

The complete unchanged pinned update_kv_cache body is extracted into the native C source projection, with64 genuine eight-byte scalar node fields and a deterministic CRC provider stub returning77770000. Stock's sole reached external CRC provider585840 is mocked with exact seed0/name-pointer/length4 argument checks and the same result. This isolates loop/field/count behavior and does not validate CRC implementation or collision handling. Source compilation is native logical-node comparison; ARM pointer/database layout is independently established by the separate target-header probes. No source body edits or relocation masks are used.

The larger neighborhood disassembly contains preceding data/literal bytes; it is not a function inventory. Only the authenticated bounded extents above are executed. Canonical rows currently carry unnamed/low-confidence labels; this receipt does not change those labels or admit implementation code.

## Finite boundary

Header probes establish candidate layout. Guest fixtures establish selected RAM cache access/update behavior with bounded reads/writes. Neither executes find_kv, database initialization, flash read/write/erase, status table providers, FAL, lock callbacks or NOR hardware. These cannot be relabeled as storage success, cache coherence under concurrency, complete database behavior, source identity or byte-identical source build. Cache count64/64 is closed within the pinned layout/source candidate; remaining storage-provider/configuration branches belong to the implementation/audit tracks.

Replay: python3 check.py with the existing Unicorn2.1.4 package and local clang/GNU objcopy paths. Initial isolated header probe lacked standard/config includes and failed; corrected probe and all four fixtures passed. Only this new directory was written; no canonical ledgers, index, pins, production sources/payloads, device state or other track outputs changed.
