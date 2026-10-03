# Independent review 6425

Disposition: **PASS_SCOPED**; `accepted:false`.

All three source ranges, packet files, and receipt digests match. GNU Thumb decoding confirms three frameless leaves, each loading descriptor+4 before checking for a null descriptor pointer. Each then masks the descriptor word with 0x01FFFFFF and compares it with the literal; null or mismatch returns 2. Thus the null test does not guard the earlier read.

In EB74..EBAA, a valid descriptor supplies byte1 low3 into bits16..18 and word+4 low10; the assembled word is stored through a literal-backed address and zero is returned. Descriptor byte0 is not read in this body. In EBAA..EBE2, a valid descriptor leads to a fresh separate global-word bit0 test: clear returns 7; set causes a fresh read, bit31 OR, store, and return zero. In EBE2..EC0C, a valid descriptor causes a fresh word read, bit31 clear, store, and return zero. The validation read and the mutation reads remain distinct.

This verifies raw leaf behavior only. It does not infer shared state purpose, atomicity, or runtime fault behavior. No canonical files or gates changed.
