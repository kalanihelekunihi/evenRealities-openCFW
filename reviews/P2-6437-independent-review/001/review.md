# Independent review 6437

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and EE70..EF00 source slice match. GNU Thumb decoding confirms the 32-byte frame and two early reads before descriptor validation: capacity from the count pointer, then descriptor+4. Null/magic failures return 2; a null fifth-argument output pointer returns 6. These guards do not protect the earlier reads. The count word is zeroed before the branch on input R5; nonzero R5 exits this packet to EF00, while zero enters the read loop even when captured capacity is zero.

Each iteration freshly reads a hardware word, uses its bits28..30 to select a literal-backed configuration word, tests that word's bits8..11 against 8, inverts the boolean, truncates to u8, and calls EE00. It publishes result bits28..30 at output+4. For the low output word, u8 input R8 nonzero selects result low20; zero selects bits6..19. It writes output, advances the pointer by 8, freshly reads/increments/stores the count with wrapping, and stops if result bits20..27 are zero. Otherwise it compares the fresh count against captured capacity and repeats only while count is unsigned-less-than capacity. Thus the zero-capacity path still emits its first output record.

This packet ends before its alternate path and epilogue. Shared count/descriptor alias effects are preserved; no purpose or validation of those external paths is inferred. No canonical files or gates changed.
