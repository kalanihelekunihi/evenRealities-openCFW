# Independent FlashDB blob/build-interface audit

PASS: all six stock/public ARM constructor cases independently replay exactly using the existing Linux Unicorn backend. Fourteen additional checks bind sources, original bytes, layouts, and analysis input. Outputs are replay-results.json, checks.json, and replay.py. Owner inputs were read only; replay wrote private /tmp output and this audit directory. No canonical coverage/admission or Git mutation.

## Supported finite contract

The official header-bearing main payload hash is 36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863; describing this as raw main is imprecise. Address mapping correctly accounts for its 32-byte header. The 132-byte adapter 54116E..5411F2 authenticates to 9e7d9b4f3af470e7f70cf9b1fe8cb304b940af29f6c636f0eea19e38f4a493e1. Stock instructions independently show stack+16 buf, +20 size, +32 saved.len; blob-relative offsets are 0,4,16. UXTH narrows length, UXTB narrows index; database = literal 2005DFFC + (index & 255)*2220. Return passthrough and saved.len branch are separate.

Three retained public files match their recorded hashes and registered pin 714d6159e7e6afb267a3953756abca445c350e61. Extracted constructor body is verbatim fdb_utils.c. This authenticates the acquired candidate source, not the original producer's revision. Its two stores preserve the other twelve blob bytes. Six replay cases compare all twenty bytes, provider arguments, return, unchanged key/output, stack restoration and modeled flag calls. They include high-bit narrowing and independent provider-return/saved-length combinations.

## Layout constraint and limits

Unchanged fdb_def.h plus recovered 64/64 cache configuration produces short-enum ARM32 blob size20, saved.len16, kvdb size2220 (0x8AC). Relevant kvdb offsets: caches168 and680, trailing user_data2216. Default enums produce2744 and fail the stride assertion. This rules out that default-enum candidate configuration. The constructor has no enum-dependent fields itself: six executions validate blob ABI, while compile/layout evidence independently supports the database representation. They do not execute database cache access or identify all stock field offsets.

Apple clang21 with GNU14.2 declaration headers is a comparator build, not original compiler identity. A matching short-enum representation does not uniquely identify -fshort-enums, compiler revision, packing or alternate configuration. The copied fdb_cfg.h statement that the eventual build 'must also use ... short-enum ABI' is stronger than uniquely established evidence; interpret as the current matching candidate requirement, consistent with the owner's report caveat. No byte-identical build follows.

## Tooling and remaining boundaries

The retained REA analysis ELF hash binds exact original function bytes with explicit Thumb entry. Disposable REA/Ghidra recovery is separate from failed shared Ghidra MCP postconditions; HTTP200 was not successful analysis. Tool default language/compiler descriptions do not establish producer identity. Synthetic ELF metadata is not firmware reconstruction. External callee output explains the decompiler's untyped saved.len local; this is not evidence of an uninitialized-use defect.

Provider54454A writes saved.len synthetically; tick4490CC and flag43D0CE are mocked. Flags remain zero, so enabled logger paths are not covered. No provider storage, FAL/flash/filesystem, range-validity, buffer-capacity, cache, mutex, concurrency or hardware behavior follows. Candidate source/build-interface hypothesis is finitely supported; full provider/source identity, original configuration/compiler/link recipe and byte equality remain unresolved static work. No new live hardware or exception-delivery receipt exists.

Owner evidence: ../../flashdb-blob-build-interface-20261010-implementation/REPORT.md (resolve from the audit parent); detailed source bindings and tool receipts remain in that owner directory. Existing sealed tests were replayed solely for independent verification, not counted as new canonical coverage.
