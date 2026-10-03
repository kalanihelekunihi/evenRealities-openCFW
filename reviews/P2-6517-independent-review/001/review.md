# Independent review 6517

Disposition: **PASS_SCOPED**; `accepted:false`.

All six input hashes and the three packet-file hashes match. The source interval 430454..430470 has the recorded hash and contains seven aligned words; all seven have consumer evidence. I independently checked the ten observations against their pinned references and source bytes. Nine are 16-bit PC-relative LDR literals; the remaining observation at 43034C is a 32-bit LDR.W literal and resolves to 430468 using aligned PC plus imm12. All ten targets and recorded word values match.

The report correctly excludes the preceding alignment bytes, preserves duplicate consumer observations, and makes no claim about broader interval coverage or data admission.

No canonical files or gates changed.
