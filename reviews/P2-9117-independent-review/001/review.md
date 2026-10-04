# P2-9117 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- Fresh isolated audit replay confirms exact 1,898-byte instruction tiling of 0x52AE38..0x52B5A2 across 14 maps, with no overlap or gap. Instruction bytes and packet hashes match the locked image.
- The audit explicitly excludes the external copy/fill helpers at 0x4D293C..0x4D2974 and keeps byte tiling separate from semantics.

Limitations:

- No helper closure, whole-firmware coverage, C completeness, or admission is inferred from this span audit.
