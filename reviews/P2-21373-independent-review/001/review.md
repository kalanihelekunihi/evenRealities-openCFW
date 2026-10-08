# Independent review — P2-21373

Status: partial; accepted: false.

Fresh replay passed for the 128-byte range. Regenerated instruction and reference files match the candidate exactly, including tiling and PC-relative references.

The aligned wide-pair path retains both loaded words, stages the described width/precision/radix/sign/value fields, and leaves the noted stack gap untouched before invoking the helper. The signed-long path uses a full word, advances the argument cursor by four, stages the sign and magnitude, and calls the output helper. For the remaining integer conversions, bit 6 takes precedence and zero-extends with UXTB; bit 7 uses UXTH; the fallback loads the full word. Each consumes four bytes from the vararg cursor, and neither narrow path sign-extends.

The shared continuation is unresolved, so this review makes no whole-routine coverage or acceptance claim.
