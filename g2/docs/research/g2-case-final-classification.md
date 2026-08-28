# G2 charging-case final classification frontier

The prior charging-case ownership map left 17,070 application bytes unresolved:
14,886 bytes in 222 authenticated Ghidra function ranges and 2,184 bytes in 229
inter-function spans. The final classifier accounts every one of those bytes.

All 222 evidence-closed frontier functions (14,886 physical bytes) now have
isolated, strict Cortex-M0+ clean-room source: 18 register
primitives/transforms (216 bytes), 189 semantic leaves (14,208 bytes), 7 pure
shift/framing/format helpers (248 bytes), and 8 register/state policy leaves
(214 bytes). The semantic set comprises the originally certified 29 functions /
184 bytes plus 160 post-baseline functions / 14,024 bytes. Its authenticated
evidence includes 11 supplemental decompilation pins / 148 bytes and 15
serial-sequence pins / 642 bytes. Every candidate address, size, instruction
digest, classification, and non-empty decompilation digest is authenticated.
No frontier function remains typed unsupported or unclassified.

Of the 229 gap spans, 31 are exact all-zero alignment/data spans. The remaining
198 are typed unsupported inter-function code/data boundaries: Ghidra proves
they lie outside discovered bodies, while the current evidence cannot safely
distinguish literal/table data from unreachable or undiscovered code. This is
an explicit missing fact, not an invented executable or source claim.

The disjoint whole-blob buckets are 32 generated wrapper bytes, 14,886 candidate
source bytes, and 40,866 typed external/unsupported bytes, totaling 55,784 with
zero unclassified bytes. The physical-bucket digest is
`126efe6801410d0051201a4a0a7f04a3a0ddd917117cb305afad35772e907a89`.
The complete function graph also links into the source-image target as eight
translation units with zero undefined symbols. Classification and software
link completeness do not imply physical board routing or hardware
qualification: production routing remains disabled, hardware validation is
blocked by unavailable physical evidence, and no hardware operation is used by the audit.
