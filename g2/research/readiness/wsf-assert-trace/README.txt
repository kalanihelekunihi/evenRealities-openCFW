OpenCFW Lorelei Cordio wsf_assert.c/wsf_trace.c readiness and structural matrix

Scope
-----
Scratch-only comparison against authenticated G2 stock firmware. Proprietary AmbiqSuite source, stock firmware, generated objects, raw function bytes, and disassembly are excluded. This artifact contains identities, exact flags, clean-room ABI headers/stubs, closure and comparison ledgers, timings, and checksums.

Bounded stock bodies
--------------------
WsfTrace [0x0052A63C,0x0052A672) is 54 bytes. It has 126 direct BL callers, the retained wsf_trace.c path and line-137 literal, an exact 1024-byte local buffer, and the official source provider order: am_util_stdio_vsprintf, am_util_stdio_printf, conditional WsfAssert, final printf. WsfPacketTrace is compiled by the source but dead-stripped/unbounded in stock.

WsfAssert [0x00569A44,0x00569ADE) is 154 bytes with a sole direct BL from WsfTrace, a clean next-function boundary, retained wsf_assert.c path, and EasyLogger assertion literals/providers. This is a downstream-expanded implementation: the official 2.5.1 source is only a debugger-escape spin loop. Its structural comparison is an implementation-drift baseline, not a plausible compiler identity match.

Configuration and closure
-------------------------
The selected trace configuration pins AM_DEBUG_PRINTF=1, WSF_TRACE_ENABLED=1, WSF_TOKEN_ENABLED=0, WSF_ASSERT_ENABLED=1, and AM_PRINTF_BUFSIZE=1024. Archive-default 256 bytes and tokenized tracing are ruled out by stock. Clean-room Ambiq logger headers preserve the official function ABI without importing SDK utility implementation. Every one of 13 profiles links to zero undefined symbols.

Results
-------
Thirteen compiler profiles x two bounded functions produced 26 comparison rows in 2097948391 ns wall-clock; summed compile 948956896 ns and link 178094949 ns. Raw matches: 0; strict normalized matches: 0. Best aggregate lane is stockabi_1024__O1 with 152 bytes total absolute size delta and 0/2 exact sizes. See best-size-per-function.tsv for the per-function result.

Interpretation
--------------
WsfTrace is a strong exact-source/config mapping even if GCC does not reproduce IAR bytes. WsfAssert proves the same retained translation-unit identity but also a material downstream EasyLogger augmentation. The next productive step is to recover that small downstream WsfAssert source overlay from the already bounded EasyLogger ABI, then run the licensed IAR profile. Do not assign a stock address to WsfPacketTrace without independent caller or stored-pointer evidence.
