# Wave062 independent review: timer callback C types

**Result: the identified incompatible-callable-type defect is resolved within the six registered timer callbacks and their registration declarations.** This conclusion is limited to the checked source contract and pinned source build.

I compared all seven entries in `source-changes.json` against their saved `before/` copies. The six callback definitions now take one `uint32_t argument` and explicitly discard it; the six declarations in `application_boot_transport_start_candidate.c` have the same parameter type. A repository-wide search found no other declaration or definition of these six callback symbols with a conflicting prototype. The trampoline’s indirect type remains `void (*)(uint32_t)`, matching those definitions.

Wave062’s verifier performs `-fsyntax-only -Wall -Wextra -Werror` checks against a forced header that statically asserts each callback pointer’s type. It also compiles the saved original copies as negative controls and requires them to fail with conflicting-type diagnostics. I independently reran the verifier from a disposable `/tmp` copy with the authorized offline Unicorn JIT execution; it passed all seven corrected source checks, all seven original-source negative controls, and the 145 affected comparisons across waves056–058.

The CASE039 and wave062 source ELF files are exactly byte-identical: SHA-256 `13c64ed72bcd95f07a5a34b2315fd249bd80e96c9981d000b6e6570908428853` (121,148 bytes). Wave062’s pinned Clang LTO receipt lists 401 source units; every listed source hash matches the current source tree. Thus the type correction changes the C contract without changing the checked ELF bytes.

This review does not establish callback-body equivalence, asynchronous callback/delete/reuse lifetime, IRQ nesting, a global stack bound, hardware acceptance, native-firmware equality, or a formal G2/G6 gate. Those limits remain as recorded in waves056–058 and wave062.

## Wave060 qualification

The prior site-level qualification is confirmed from wave060’s saved verification data and checker aggregation: 51 unique target keys, 366 sampled operand PCs, 260 PCs with the expected constant on every modeled syntactic predecessor, and 106 unresolved/nonconstant PCs. The checker reports `51/51` because every target key has at least one resolved example. That is a target-level result, not proof that every sampled use is resolved. Examples include `0x20000892` with 11 unresolved PCs of 12 and `0x2000087e` with 6 of 12.

## Reproduction

Command: `/tmp/iar-c-runtime-venv/bin/python g2/analysis/component-goal-20261013/case-wave062-timer-callback-c-type/verify.py`, run with the wave062 tree and its required pinned inputs copied under `/tmp/case-wave062-independent-fixture`. Result: `PASS_SOURCE_CALLBACK_C_TYPE_REPAIR_AND145_AFFECTED_PAIRS 13c64ed72bcd95f07a5a34b2315fd249bd80e96c9981d000b6e6570908428853`.
