# Independent review 6439

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and EF00..EFF4 source slice match. GNU Thumb decoding confirms eight independent PC-relative word loads; each tests bits8..11 for the value 8 and contributes its corresponding one-hot bit to R9. It then reads the array word at [R5] once to extract bits28..30 into R8 and again to obtain low20 bits, preserving the fresh-read behavior. R9 is shifted right by R8, masked to one bit, inverted, truncated to u8, and passed with the fresh hardware word to EE00.

The result's bits6..19 are stored at output+0, while the earlier array bits28..30 are stored at output+4. The array and output pointers advance by 4 and 8. A fresh count read is incremented and stored with wrapping, then freshly reloaded and compared unsigned against captured capacity. The loop continues only while count is below capacity; the branch preceding the loop enters it even with zero capacity, so at least one record is written on this path. This array path has no terminator test. R8 is overwritten with the extracted field, not restored as the original input flag. The shared EFF0 epilogue restores R1 from saved entry R3 and returns R0=0 on normal completion; earlier errors can reach it with their status still in R0.

This verifies local instructions, read order, and frame effects only. Array meaning and alternate-path/epilogue behavior beyond the mapped extent are not inferred. No canonical files or gates changed.
