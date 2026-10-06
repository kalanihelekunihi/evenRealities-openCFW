# Independent review P2-18523

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 106-byte span `0x460BD0..0x460C3A`; instruction/reference manifests match. It inherits the 64-byte frame and sets R8=52. Argument setup computes, in order, destination+40 into the caller fifth-argument slot at SP0, destination+36 into R3, destination+4 into R2, destination base into R1, and the source word at source base +44*index +48 into R0. It calls the previously mapped eight-record lookup `0x460450`. A full zero result branches to the alternative key-update entry `0x460A44`.

For nonzero result, a fresh mask read gates diagnostics. The bit-1-set route freshly reloads the source word+48 into SP8, writes literal at SP4 and 433 at SP0 (overwriting the fifth-argument slot after the lookup), then calls `0x43D574`. Local slots are not saved-register slots. The source stride 44 remains live for the child, while the child must preserve R9 for subsequent use. No second lookup or cached key reuse occurs in this block.

Remaining diagnostics/negative exit are outside the span; child contracts remain unresolved. Partial/unaccepted only.
