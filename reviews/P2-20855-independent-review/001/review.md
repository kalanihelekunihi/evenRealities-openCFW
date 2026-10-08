# P2-20855 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 56 bytes at 0x47CF28..0x47CF60; pinned image/source hashes and tiling verified. This distinct template pointer supplies the SP0/SP4 words. Two independent 0x45A568 calls store the first low byte and use a full-width exact-1 comparison for SP5=2/1. No flag-byte read or SP6 write occurs here, so remaining template bytes are left as loaded before the output helper. The helper result is discarded; POP returns template-derived SP0/SP4 values and saved entry R7 from SP8. Callee writes may affect the returned buffer words; no template protocol contract is claimed.
