# Apollo LZ4 finite source/behavior discriminator

**Completed:12 raw-block fixtures plus12 locked-caller invocations, all guards retained.** Exact signed returns and complete destination-capacity bytes match both official LZ4v1.9.4 andv1.10.0 across all12 cases. This finite discriminator does not choose a unique source revision/compiler or prove whole-library byte/source completeness. No version/compiler sweep followed the nondiscriminating result.

## New useful behavior

Zero compressed input returns-1 in stock safe API but is accepted as empty by emulator Python. Encoded empty token00 returns0 in the safe API. LiteralHELLO returns5 with capacity5 and-2 with capacity4. Truncated literal extension/payload/offset/match extension cases return-2; offset beyond history and one-byte-short overlapping output return-6. The valid overlap fixture returns26. SUMMARY.json contains every branch result.

Zero offset is a deliberate host-policy distinction: Python rejects it, stock and both upstream C versions return26 with outputA +20zero bytes +abcde. Official pinned block-format specification identifies offset0 as corrupted/invalid. Decoder acceptance does not make the block protocol-valid, prove a vulnerability, or justify weakening host validation. Actual public source and original-instruction agreement narrow behavior, not original producer identity.

The locked outer caller4E0C0C..4E0C34 reorders(src,len,dst,cap) then maps negative/zero safe results to0, preserving positive length. The historical emulator navigation callsite56192E does not match locked image bytes and was excluded. New caller/root role remains unbound; direct decoder tests do not certify app navigation lifecycle.

## Execution and input provenance

Three selected decoder extents total1220hash-bound bytes. Five local read/copy helpers and two IAR copy/move bodies execute stock instructions, with allowed-PC guards and return-sentinel interception only. No external-call stubs, register repair, firmware patches or manually continued path. Input/output addresses are20020020/20030020 with16-byte pre and32-byte post sentinels, full source retention and output guards at capacity. SRAM/SP and locked code mapping are explicit in finite_compare.py. Guards are checked before outputs, including decoder errors; complete capacity content is compared, with in-capacity tail writes allowed by the API contract.

Native macOS Unicorn crashes on ARM engine construction. Isolated official PyPI Unicorn2.1.4/Capstone5.0.7/pyelftools0.32 in Linux supports ARM execution. Continuous mode fails the original memmove->memcpy five-byte fixture across default/M4/M33 profiles with an actual guard violation, while direct memcpy tests pass. This is an execution-profile/model finding, not hardware memory corruption. Existing instruction-by-instruction profile completes the same original provider without edits; that is the fixed profile for all finite comparisons. Failed traces remain retained. New successful finite results do not erase failed exploratory execution; the abandoned larger exploratory fixture set adds no passes.

Both authentic BSD2 upstream endpoints were compiled unchanged as Linux semantic comparators with GCC-O2-fPIC-shared; host compiled objects are not stock byte reproduction. Official tags resolve5ff839680134437dbf4678f3d0c7b371d84f4964 /ebb370ca83af193212df4dcbadcc5d87bc0de2f0. Acquisition/license hashes, engine/compiler/comparator identities and original disassembly are retained. Emulator Python function was extracted unchanged by AST from its read-only source; no simulator code or buzzer work occurred.

## Deliverables and stopping boundary

Read pseudocode.md and lz4_stock_contract.h for recovered interface/app implications; finite-results.json preserves source/Python distinctions, raw writes and visited instruction addresses; stock/helper/extra-bound manifests authenticate code. This corpus does not cover all grammar/overflow/dictionary/partial paths, every caller, boot state, physical hardware or whole-image rebuilding. Safe/outer caller behavior is finite software evidence; version interval remains unresolved. Nema comparison remains separate discovery/audit ownership. No additional LZ4 version sweep or old DSP/audio/HCI probe is needed to complete this goal.

No production/registered-pin/Git/Pigweed/canonical/device changes. Existing seals/110inputs/four checkpoints verify in preservation.json; observed index is recorded without claiming historical-index equality.
