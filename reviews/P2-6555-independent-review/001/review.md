# Independent review 6555/002

Disposition: **PASS_SCOPED**; `accepted:false`. This review is for packet revision 002; revision 001 remains preserved.

The corrected 110-byte span 0x415F40..0x415FAE and packet hashes match. GNU Thumb decoding confirms that a null output skips consuming the float argument and the format count. Otherwise the argument is aligned to eight bytes, loaded as a double, converted to single, and the whole capacity word 20 is stored before calling 415AB6 with the output buffer and precision. Nonnegative child results are used as output length; negative results select one of the three pinned fallback words, store that whole word, and use length 3. Width does not participate. The default-specifier branch writes the current specifier byte only for nonnull output but always increments the count. At the format terminator, a NUL is stored only when output is nonnull; the count is returned after ADD SP #20 and the 56-byte saved-register frame is restored.

I independently checked all three LDR literal effective addresses: 0x415F6C->0x415FE4, 0x415F76->0x415FE8, and 0x415F7A->0x415FEC. This review does not infer the meanings of those fallback strings or the child formatter beyond the local branch behavior. No canonical files or gates changed.
