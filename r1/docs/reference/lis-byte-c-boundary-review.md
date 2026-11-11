# LIS byte setter: direct-C frame probe rejected

The existing LIS byte-setter bridges remain unchanged. A direct-C reset-set
prototype for stock `0x757ec` captures incoming R3 with empty constraints and
uses a C scratch word, but its first transport call has a 24-byte frame and
scratch pointer at caller SP minus 20. Stock uses a 16-byte frame and the
saved-R3 byte at caller SP minus 16. Failed or non-writing reads can observe
that difference, so this probe cannot replace the current boundary.

An executed first-call check confirmed the mismatch for the normal Clang
profile with `minsize`, and additional stack-alignment, omitted-frame-pointer,
Oz and combined Oz/alignment probes. A license-free GCC9 probe also produced
24/20; GCC explicitly ignored the Clang-specific `minsize` attribute. No probe
flags or source entered the production manifest.

This is a first-call counterexample, not a full behavioral comparison. The
[receipt](lis-byte-c-boundary-review.json) includes REA/Ghidra stock bytes and
the probe hash. Ignored inputs and executable checks are under
`build/goal-r1-lis-byte-c/`. A replacement must preserve the scratch position
before proceeding to the full failed-read, alias and callback-mutation matrix.
