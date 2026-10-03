# Independent review 6391

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and source slice match the receipt. GNU Thumb decoding confirms E2F8..E39C: a 16-byte saved-register area plus 80 local bytes; five ordered child calls; and two E224 result branches that stage separate diagnostics and 40-byte clear buffers before calling DCA2. The nonzero-result diagnostic uses SP0=209 and clear-buffer SP40=1; the zero-result path uses SP0=216 and clear-buffer SP0=0. Both enter the loop at E370.

The loop calls 4162C4 with (0x00FFFFFF, 0, 60000) and 4160E8. A result R4 in the unsigned interval [1, 0x80000000) branches through E39A (BX LR) and then resumes the loop. Otherwise it computes wrapped R0-R5 and continues while that value is below 60000; on the other path it copies R0 to R5 and loops. There is no ordinary return path in the mapped body.

This confirms local source control flow, raw call arguments, and stack stores only. Callee behavior and the invalid-address store's runtime outcome remain unverified; no canonical files or gates changed.
