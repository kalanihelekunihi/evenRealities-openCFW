# Independent review 6485

Disposition: **PASS_SCOPED**; `accepted:false`.

The receipt files and F430372..F4303BC body hash match the locked image. GNU Thumb decoding confirms the unsigned index/count exit, 12-byte stride, and type-byte gate at record offset 4. On the type-1 path, the code loads a global word through the literal at 43046C, loads its pointee, and calls 41D92C with the record's word-0 value in R0; that child's result is not used. It then freshly reads byte 5, normalizes equality-to-1 to a byte boolean in R1, reloads record word 0, and calls 41D9AA. The stride register is reused for `12*index`; the next loop iteration resets it. At the in-range exit R0 is set to zero, and the common epilogue discards 32 local bytes and restores R4–R8/PC. The non-type-1 branch leaves this span for 4302B8.

This review covers only the supplied continuation. It does not establish the complete record format, other type handlers, or full-table boundaries; behavior of the external callees remains outside scope.

No canonical files or gates changed.
