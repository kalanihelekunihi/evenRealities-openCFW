# Independent review 2575

**Result: PASS_SCOPED.**

Candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-revision-profile-flags-2574/001` binds to the pinned image. Receipt and all artifact hashes, body span `[0x42D6C0,0x42D79E)`, and literal addresses match. The isolated replay passes all 175 original-instruction fixtures.

The independent conditions agree with the leaf’s observed flags: B3 is set for revision `0x21`, secondary 2; B4 for `0x21` with secondary 2/3 or `0x22` with secondary 0; B5 for `0x22`/1, and for `0x23`/0 only when neither packed-word predicate holds. The special predicate uses mask `0x3FE00000`, value `0x31800000`, bits 16–20 at least 20 and low16 zero; the alternate predicate uses bits25–29 at least25 and low16 zero. Tests cover equality boundaries, low16 suppression, revisions with low-byte truncation, ordered flag-byte writes, neighbor sentinels, return 0, SP and high registers.

The source revision, secondary word and packed state are stable fixture values, so this does not test mutations between the original repeated reads. Physical meaning of the fields, concurrent changes, callers and other profile effects remain unresolved. Private evidence only; accepted:false and no canonical admission.
