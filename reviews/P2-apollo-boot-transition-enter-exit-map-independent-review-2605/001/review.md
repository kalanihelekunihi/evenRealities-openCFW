# Independent review 2605: transition enter/exit static map

**Result: PASS_SCOPED.** `accepted` remains false.

The source, receipt artifacts, and body hashes match. The two adjacent spans are gap-free: `[0x42D104, 0x42D3BC)` decodes to 250 instructions/696 bytes, and `[0x42D3BC, 0x42D562)` to 162 instructions/422 bytes. Together they account for 412 instructions and 1,118 bytes. The isolated static verifier passes. I also independently recomputed aligned Thumb PC-relative addresses from each literal-load encoding and checked all 45 targets and words against the source image.

I compared the pseudocode with the original Thumb listing. The mode branch, saved/replaced control fields, low-10-bit saturation increment and restoration, timing fields, optional boost operations, field updates, ordered gate-bit writes/clears, and return paths agree. The five direct calls are all to `0x41D1C0`, three in enter and two in exit. I found no material semantic error in the bounded static description.

This packet does not dynamically validate branch outcomes, MMIO effects, arithmetic boundaries, register/stack behavior, or delays. It does not establish enclosing ownership or whole-region coverage; the delay routine is a separate dependency. No canonical admission is claimed.
