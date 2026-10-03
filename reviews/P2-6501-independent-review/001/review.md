# Independent review 6501

Disposition: **PASS_SCOPED**; `accepted:false`.

Both mapped spans match their locked-image hashes. GNU Thumb decoding confirms the FFF2 wrapper creates an 8-byte frame, calls FF00 with (1,1), then `POP {R0,PC}`, so its return value is the wrapper's incoming R7 slot.

The 430000 body saves R3/R4/LR and allocates 68 bytes, for an 80-byte frame. It loads the word through the literal at 430208, stores 1 at SP+20, and calls 41D92C with (16, loaded word). It then calls 42E8D0 with (0, SP+8). If that returns zero it continues directly to 430024; if nonzero it loads the word at 43020C and calls 415FAE before reaching the same continuation. No initialization of SP+8 appears before the 42E8D0 call in this span, so the output-area prior contents are not established here.

This covers only the wrapper and initial body slice. It does not infer purpose or resolve the continuation or child behavior.

No canonical files or gates changed.
