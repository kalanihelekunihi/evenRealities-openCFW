# Independent review 29973

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-signed-limits-event715-frame40-middle-30372-map/001`. The candidate file hashes match its receipt and its input hash matches the locked Apollo image. Independent reassembly confirms all 110 bytes decode contiguously across `[0x4EAEC6,0x4EAF34)` as 40 Thumb instructions.

The first signed limit sequence clamps negative R7 to zero and values at least 577 to 576; `MOV.W R7,#576` does not change flags. The fresh word at current R5 is loaded before `44E4BC`; the returned R0 is then added to the actual current R6 with wrapping 32-bit ADDS flags and signed-compared against current R7. R7 is replaced only when the signed sum is smaller, so the earlier limit is not claimed to survive this second stage. The bit-1 event715 path and the later bit-0/bit-2 diagnostic path are gated by distinct query calls. Event715 stack arguments and fresh literal reads match the decoded stores/loads. The rotated `MOVS.W R0,#0x10800000` leaves N=Z=C=0 and preserves V. Register mutations after helpers are treated as actual state; no ABI preservation or fixed result contract is inferred. The five PC-relative word references match the locked image.

This remains bounded partial evidence. The continuation at `0x4EAF34` and external destinations are excluded; no helper closure, global coverage, source completeness, freeze, or byte equality is established.
