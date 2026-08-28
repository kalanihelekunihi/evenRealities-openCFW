# G2 charging-case register primitive admission

This admission converts 13 previously unresolved charging-case functions
(120 authenticated Thumb instruction bytes) into clean-room, compilable C.
The admitted family contains only bounded register-field reads, one selected
register write, and pure status predicates. It contains no calls, loops,
reset, flash programming, interrupt control, or deployment behavior.

The implementation is
`components/shared/case/runtime_case_register_primitives.c`. Stock fixed
addresses are replaced by caller-supplied volatile register views, so the
source cannot access MMIO without an explicit future platform adapter. Null
views fail closed. The analyzer verifies the official case blob identity,
the exact entry size and instruction-byte digest of every admitted function,
the prior unresolved classification, the source hashes, the exact exported
symbol set, and a freestanding Cortex-M0+ build.

Admission artifacts:

- `tools/analyze_g2_case_register_primitives.py`
- `tools/manifests/g2-case-register-primitives-admission.tsv`
- `tools/manifests/g2-case-register-primitives-admission-summary.json`
- `tests/test_analyze_g2_case_register_primitives.py`
- `tests/test_runtime_case_register_primitives.py`

The case software frontier decreases from 17,070 to 16,950 unclassified
bytes. This source remains an isolated candidate: it is not yet routed into a
complete charging-case image and therefore does not establish source or
functional completeness.

This project-authored clean-room source is MIT licensed; no upstream or
copyleft body was copied into it. Hardware validation is deferred by project
direction. No MMIO, erase, program, bank-swap, reset, signing, flashing, or
deployment operation was performed.
