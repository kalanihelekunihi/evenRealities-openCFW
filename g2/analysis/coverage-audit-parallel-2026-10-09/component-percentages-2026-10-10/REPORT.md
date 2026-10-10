# Current component percentage reconciliation

Read-only canonical/reporting verification; no denied phase resumed. Current reference manifest still has six official_blob providers; each payload size/hash reauthenticates. Current Makefile uses that manifest for reference repacking. Whole component source-build proof remains0/6; integrated C-compilable byte coverage is unknown for every component.100%blob passthrough describes the current reference packaging target, not irreducible future blob necessity. Total4300283payloadbytes plus944containerbytes gives4301227bundlebytes.

| Component | Stored payload denominator | Integrated C byte % | Current blob % | Raw pseudocode function output cohort | Export-associated payload bytes | Validated listing payload-byte lower bound |
|---|---:|---|---:|---|---|---|
| Apollo main |3523396|Unknown|100%|8475/8853=95.73%|1555524=44.15%|17484≥0.50%|
| Apollo bootloader |148599|Unknown|100%|849/903=94.02%|112506=75.71%|9594≥6.46%|
| Touch |34464|Unknown|100%|308/308=100%|27879=80.89%|15616≥45.31%|
| Case |55784|Unknown|100%|435/435=100%|43072=77.21%|4320≥7.74%|
| Codec |326092|Unknown|100%|929/929=100% in five export images|92560=28.38%|36484≥11.19%|
| EM9305 |211948|Unknown|100%|Unknown whole-component denominator|Unknown|210072≥99.11%|

Main correction: legacy7449/7449harvest is still valid for its own cohort, but the larger authenticated raw-export cohort is8475/8853with378failures. Do not call this a drop in coverage: different discovered populations. Boot54failures remain excluded. Codec929counts five historical export images; stage1A/B and other payload contents remain outside that function denominator. EM shard pseudocode does not establish a whole-component count.

Pseudocode byte percentages divide unique successful raw-export intervals by full stored payload, including wrapper/data/padding. They are not reviewed pseudocode or exclusively executable bytes. Whole-executable disassembly percentages remain unknown for all six. Assembly lower bounds are deduplicated byte correspondence from validated selected listing artifacts, not an all-executable denominator or instruction-semantics proof; some listing bytes may decode data/literals. Do not use payload complements as missing-code counts.

Verification: independently replayed partial_union_verify.py (10499Arm envelope hashes, output hashes/nonempty bodies, union/complements) and codec_listing_verify.py (929codec envelopes and two exact listing serializations). Results exactly match existing sealed additive receipts. Rechecked all cited ARM listing input hashes and three corpus listings; ARM counts are unchanged existing bounded unions, not a new wider scan. New local SDK/TLSF/FlashDB leaf experiments do not automatically add canonical union bytes or compilable percentages. Source-build readiness report and canonical state still require G2-G6 gates; none passed by these comparisons.

Evidence paths: g2/Makefile; g2/manifests/g2-2.2.6.10.json; g2/workflow/state.json; ../COMPONENT-COVERAGE-MATRIX.md; ../PARTIAL-UNION-REVIEW.md; ../CODEC-LISTING-REVIEW.md; g2/analysis/dependency-gap-audit-fresh-2026-10-09T192823Z/EXISTING-ASSEMBLY-AND-SOURCE-REVIEW.md and EXISTING-ARM-LISTING-VERIFICATION.json; ../source-build-readiness-2026-10-10/REPORT.md. New metrics.json and two replay-verification JSONs preserve explicit numerators/denominators.
