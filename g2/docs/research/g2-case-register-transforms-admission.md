# G2 charging-case register transform admission

The second case-source batch converts five additional unresolved functions
(96 authenticated Thumb instruction bytes) into clean-room MIT C.
It implements two masked word updates, two bounded three-bit field updates,
and the stock 16-bit sign-extension primitive. Fixed-address accesses are
again caller-supplied volatile views; no MMIO address is embedded.

The analyzer pins every stock entry, size, and instruction-byte digest; pins
both source files; verifies the exact five-symbol export set; and compiles the
unit for freestanding Cortex-M0+ Thumb. Host tests exercise positive, negative,
boundary, field-selection, and null-view behavior.

Artifacts:

- `components/shared/case/runtime_case_register_transforms.c`
- `tools/analyze_g2_case_register_transforms.py`
- `tools/manifests/g2-case-register-transforms-admission.tsv`
- `tests/test_runtime_case_register_transforms.py`
- `tests/test_analyze_g2_case_register_transforms.py`

Together with the prior leaf batch, 216 bytes across 18 functions now have
compilable source candidates; 16,854 case frontier bytes remain source-
unsupported. Neither batch is production-routed yet.

No upstream or copyleft body was copied into this project-authored clean-room
source. Hardware validation is blocked by unavailable physical evidence. No MMIO, flash,
reset, signing, flashing, or deployment operation was performed.
