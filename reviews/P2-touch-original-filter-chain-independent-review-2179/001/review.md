# Independent review 2179: original filter chain

**Result: PASS_SCOPED.** Candidate `analysis/touch-original-filter-chain-2176/001` remains unaccepted.

The 288-case composition runs the original dispatcher and median, weighted, and averaging bodies without intercepting their entries. The observed order is median, weighted update, then average; the group cursor’s four-byte and two-byte movements are represented in the expected model. Full sample/history/auxiliary buffers, call order, R4 and SP pass.

The isolated replay matches frozen output exactly, and 130 instructions across six spans independently decode. History bytes are fixed and configurations are bounded, so this does not establish general filtering behavior, aliasing, concurrency, or physical meaning. No canonical records changed.
