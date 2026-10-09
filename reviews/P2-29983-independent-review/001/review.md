# Independent review 29983

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-dispatch68-event760-inputone-helper-frame48-middle-30382-map/001`. Candidate file hashes and locked-image hash match the receipt. Independent reassembly confirms all 72 bytes in `[0x4EB04A,0x4EB092)` decode contiguously as 25 Thumb instructions.

The initial bit-1 query path gates event760; the event arguments use the candidate's fresh literal loads, narrow PC-relative loads at `0x4EB328` and `0x4EB32C`, and the stated current SP slots. Later bit-0 and bit-2 queries are separate calls. `MOVS.W R0,#0x0C000000` produces N=Z=C=0 and preserves V. The input-one path sets R0=1 and passes actual current state to `4EAD10`; its subsequent branch to `0x4EB1AE` is outside this interval. The five literal references agree with the locked bytes, with literal contents kept distinct from pointees.

This is bounded partial evidence only. No helper behavior, global coverage, source completeness, freeze, or byte equality is established.
