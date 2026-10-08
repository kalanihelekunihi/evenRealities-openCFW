# Independent review — P2-21359

Status: partial; accepted: false.

Fresh replay passed for the 130-byte prefix. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative references.

The flag path sets the observed plus, space, and alternate-form bits while advancing and storing the format cursor. Width parsing calls the decimal helper with the cursor address and stores its full result; star width instead reads a full argument word and advances the vararg cursor by four. Negative star width sets the sign-related flag and negates with 32-bit wrap semantics, so the minimum signed word remains wrapped. The dot path sets the precision flag and advances/re-reads the cursor as represented.

Precision parsing beyond this prefix is unresolved. Review remains partial and does not establish whole-routine coverage or acceptance.
