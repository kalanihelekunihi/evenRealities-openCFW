# Touch interrupt registration wrapper A2A8

Body A2A8..A2E4 is 60 instruction bytes. Null descriptor returns the null-input literal. Otherwise unsigned priority word at descriptor+4 must be at most three; violations reach BKPT A2B8. Sign-extend descriptor halfword at offset zero and call A214(index,priority). Freshly read literal system base+8 (vector table offset register), compare with RAM vector-base literal; only equality calls A274(index,incoming callback). Return zero regardless of deeper helper returns and restore four-word frame.

Thirty-six original-instruction fixtures cover null/nonnull descriptor, valid/invalid priorities, signed indices and both vector values. Two deeper helpers are controlled with all-ones return. Exact calls/arguments, guard stop, return and restored SP are checked. Deeper priority/vector writes, invalid pointers and physical interrupt dispatch remain unresolved. No canonical admission or C implementation.
