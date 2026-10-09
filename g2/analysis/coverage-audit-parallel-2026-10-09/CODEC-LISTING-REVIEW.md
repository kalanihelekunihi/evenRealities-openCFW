# Independent codec and EM9305 artifact representation review

PASS for discovery CODEC-EM9305-COVERAGE-FOLLOWUP.md and corrected JSON. codec_listing_verify.py independently matches929 codec envelope hashes to five canonical terminal images, validates bounds and deduplicated image-local unions, and authenticates actual nonempty successful C exports against research manifest. Raw pseudocode-associated bytes total92,560, **28.384628% of codec payload326,092**. Each image's local ranges are kept separate despite runtime aliases; containers and NPU command/weight data are not added as MCU pseudocode.

Independently parsed all71,167 EM listing lines and14,467 C-SKY XIP lines and compared serialized halfword bytes to authenticated artifacts. Matched unique byte unions exactly equal corrected receipt. C-SKY displayed32-bit tokens must retain ordered16-bit halfwords, each little-endian; treating whole token as little-endian reverses halfword order. Independently reproduced initial3775 mismatching lines; original failed receipt remains preserved. Corrected serialization has zero mismatches.

| Representation | Matched unique bytes | Whole payload denominator | Artifact representation fraction |
|---|---:|---:|---:|
| Codec raw pseudocode spans |92,560|326,092|28.384628%|
| Codec XIP byte-matched listing |36,484|326,092|11.188254%|
| EM9305 byte-matched listing |210,072|211,948|99.114877%|

EM record3 is210,888:210,072 represented+816 unrepresented. Whole payload additionally contains1060metadata/other-record bytes, so total unrepresented payload bytes are1876, not816. Dump generator's packagebase301FDC+recordoffset1060=302400 identifies byte-coordinate convention, not independently proven silicon load behavior. XIP listing represents100% of image36,484, which is only11.188254% of codec payload. Neither fraction is executable/semantic assembly coverage: actual XIP words10203008–1020300C are literal200269A4 and decoded as and/addi in linear listing.

Codec A/B stage1 and other terminal regions are outside this five-export cohort; EM whole-component pseudocode union remains unknown. Reviewed code classification, failed/superseded semantics, data/padding and accepted-review maps are still missing. Do not extrapolate these artifact fractions into correctness, source compilation or whole-code completeness. No new builds, decompilation or canonical changes. Supporting CODEC-LISTING-VERIFICATION.json.
