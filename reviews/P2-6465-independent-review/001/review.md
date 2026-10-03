# Independent review 6465

Disposition: **PASS_SCOPED**; `accepted:false`.

Both source ranges and packet hashes match. GNU Thumb decoding confirms the F38E..F3DA dispatcher saves R4/LR, sets R4=0, and truncates mode to u8. Mode 1 reads descriptor byte0 and calls F2FA when it is zero or F204 otherwise; both child results are ignored. Mode 2 writes two raw literal words to descriptor offsets +4 and +8. Modes 0, 3, 4, 5, 6, and values >=7 reach the zero-return stub without other stores. Descriptor validation is not added by this body.

The frameless F3DA leaf freshly checks its literal-backed byte gate. Zero returns zero without a store. Nonzero freshly reads a saved word and compares the full word unsigned against 7; below 7 it selects zero, otherwise it freshly rereads and subtracts 6 with 32-bit arithmetic. It then freshly reads a different hardware word, BFI-inserts the result into low10, stores, and returns zero. The threshold and subtraction operate on separate fresh reads.

This is scoped static instruction evidence only; no meaning for the mode, descriptor, or hardware field is inferred. No canonical files or gates changed.
