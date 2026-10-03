# Independent review 2273

**Result:** PASS_SCOPED.

Isolated replay regenerated all 42 fixtures. Source/body/literal and candidate file hashes match. The decoded chain computes base through context→root+8→table word, sets bit 31 with a fresh read, writes/readbacks both setup constants, and calls original 9178(base,6,source). It then rereads 0x3034 for OR 6, rereads for OR 1, and stores 1 at base+0x3800. The ordered-write and call traces, R0=base, R4 and SP checks pass.

**Limits:** Fixtures use modeled RAM and a bounded set of initial words/last source values. They do not establish hardware MMIO readback behavior, pointer aliasing, physical names, or concurrent mutation. No canonical admission.
