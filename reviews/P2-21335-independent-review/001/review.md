# P2-21335 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x48348C..0x4834FC (112 bytes); instruction/reference outputs match. The fraction path increments with wrapping arithmetic, converts to double, loads the indexed eight-byte table value, and branches on the observed FP LT condition. The separate 0.5 comparison uses MI and the R4 parity test, followed by common R7/precision handling. At zero precision, d0 is modified before later PL/LT comparisons; R5 parity can increment the integer. I preserved these specific condition branches rather than substituting a conventional rounding rule.
