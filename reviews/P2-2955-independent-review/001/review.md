# Independent review 2955/001

**PASS_SCOPED**; `accepted` remains false.

I reran the 576 original-instruction fixtures in a fresh destination. The source and body digests for the caller, decoder, and interrupt-save helper match. Operations 3/4/6 with option zero and null input run the original caller→save→decoder chain; each case checks the exact two state-publication words under masked PRIMASK, zero result, R4–R12/SP, and restoration of incoming PRIMASK. Candidate and replay output hashes match their receipts.

The fixture scope seeds stored state to match the independent decoder output. Option-enabled mutation, other snapshot states, transition branches, aliasing/volatile changes, physical hardware, and broader caller behavior remain unproven.

Candidate receipt SHA-256: `7a448dca80b54e476135c8edb3ab674b1f76baa71ae23cac828efb44c4292cbd`.
