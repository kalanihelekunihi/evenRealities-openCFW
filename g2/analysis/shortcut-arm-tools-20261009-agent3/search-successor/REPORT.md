# TLSF mapping_search successor: finite semantic boundary

Authenticated routine `0x004CFF9A–0x004CFFC2` matches pinned TLSF `mapping_search`; caller/configuration evidence narrows the main allocator to its 32-bit profile with maximum block size `0x40000000`, minimum block size 12, and 24 first-level lists. This closes the bounded mapping/configuration branch from the predecessor report. Whole allocator layout, producing-build identity and global P2 coverage remain separate tasks.

## Instruction-backed result

Body SHA is `28f5a5f4c0ce20ce58272435bbb3791fc904e17324a44792ffd7f127ee9a5ab8`, independently recorded in the historical functions ledger. Full input SHA and six independently hash-checked body extents appear in `results.json`. GNU listings are retained for mapping_search, block_locate_free, adjust_request_size, align_up and the two discovered allocation wrappers. Address mapping and source authentication remain those of the predecessor's private ELF; original bodies are unchanged.

For unsigned 32-bit `size >= 128`, compute `round = (1u << (floor(log2(size))-5)) - 1`, then `rounded = size + round` modulo 2^32. Otherwise rounded=size. Call the predecessor's mapping_insert with rounded and the original output pointers. Ablation reports the two calls at `0x004CFFAA → 0x004CFD66` and `0x004CFFBC → 0x004CFF6C`, agreeing with GNU. Its profile is raw evidence, not a source or completeness oracle.

Instruction `push {r3,r4,r5,r6,r7,lr}` followed by `pop {r0,r4,r5,r6,r7,pc}` incidentally returns original r3 in r0; historical Ghidra calls this a fourth argument/return. Upstream declares this routine void, and its caller ignores r0 after the call. The observed incidental register value does not imply a semantic return or a fourth argument.

Pinned comparator: retained TLSF source `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/tlsf/tlsf.c:532–540` (mapping_search), `:753` onward (block_locate_free), `:492` onward (adjust_request_size), `:1115` onward (malloc/memalign), and constants `:211–250`. Its source SHA remains `2a0f8cfc9cfe6114ccdc6cf22339059440b16f1149b5107bead4ae4c3a0d50e2`; no new dependency acquisition or pin change was needed.

## Rounding and caller preconditions

`block_locate_free` at `0x004D0484` requires nonzero adjusted size, calls mapping_search, and checks resulting fl with signed comparison `<24` before entering search_suitable_block. The current historical call ledger discovers one direct mapping_search caller, this routine, and two direct callers of block_locate_free: `0x004D0722` and `0x004D0744`. GNU corroborates their call sites and preparation paths; this is a discovered caller set, not an exhaustive proof excluding unknown indirect entry.

Both allocation wrappers pass their chosen size through `adjust_request_size` (`0x004CFF42`). Instructions prove it calls align_up, requires aligned size below a loaded maximum, and applies the loaded minimum size. The original flash literal at `0x004D06E8` points to `0x0078F4C8`, whose authenticated value is `0x40000000`. Literal `0x004D0854` points to `0x0078F4C4`, whose value is 12. These are flash constants in the preserved image, requiring no assumed RAM initialization. Their values plus fl<24 agree with `FL_INDEX_MAX=30` and `FL_INDEX_COUNT=30-7+1=24` in the pinned 32-bit source configuration.

Any adjusted value entering the discovered mapping path is zero or less than `0x40000000`. Therefore mapping_search addition cannot wrap modulo 2^32 on these paths. It can round a valid adjusted size above the supported bin domain: `0x3F000000` rounds to `0x3FFFFFFF` (fl23), while `0x3F000001` rounds to `0x40000000` (fl24) and is rejected before the search provider. The highest accepted aligned request in this upper interval is consequently `0x3F000000`.

Direct calls with arbitrary invalid size differ: `0xFC000001 + 0x03FFFFFF` wraps to zero, and UINT32_MAX wraps to `0x03FFFFFE`. Their resulting small fl values would pass the locate gate. The observed wrapper bounds prevent this mapping-rounding case; no new guard should be invented in pseudocode.

There is a separate faithfully observed source edge: align_up itself uses modulo-32-bit addition. For raw size UINT32_MAX and alignment 4, aligned=0, and adjust_request_size returns minimum 12 because original size was nonzero. Thus “all huge original requests are rejected” is false. The memalign wrapper also performs arithmetic before adjustment, so its original untrusted size/alignment contract cannot be inferred from the mapping routine alone. This report records arithmetic behavior rather than broadening into allocator security or hardware claims.

## Executed checks and stopping boundary

`probe.py` runs original mapping_search, mapping_insert and both real bit helpers for 3,560 boundary/seeded cases. All outputs match pinned-source arithmetic, including wrapping invalid direct inputs. It checks stack restoration and the incidental original-r3 return. Thirteen original block_locate prefixes agree with expected search-provider admission; execution stops before that provider, without mocking it or claiming full allocator execution. Thirteen original adjust_request_size/align_up cases corroborate flash constants, upper bounds and raw-request overflow behavior. All passed under Unicorn 2.1.4; independent GNU evidence corroborates ISA and calls.

The finite branch is ready for independent review. Upstream's exact 32-bit configuration explains the observed mapping/guard/constants, but many TLSF revisions may share those bodies. More repeated boundary fixtures or generic source searching cannot identify the producing compiler/version or prove other allocator routines. A next whole-allocator investigation would need a separate bounded P2 ownership contract for control layout, free-list operations, allocation wrappers and actual callers/indirect roots. No gate or canonical record is advanced, and no classifier denial/model switch occurred.

Replay: `/Users/kalani/Repos/ablation/.venv/bin/python g2/analysis/shortcut-arm-tools-20261009-agent3/search-successor/probe.py`.
