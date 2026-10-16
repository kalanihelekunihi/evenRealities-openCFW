/* Verification only; shared tails and final firmware placement stay gated. */
SECTIONS
{
    .divzero64_data 0x3b528 : { KEEP(*(.r1.math.divzero64_data)) }
    .invalid64_data 0x3b578 : { KEEP(*(.r1.math.invalid64_data)) }
    .high64_data 0x3b598 : { KEEP(*(.r1.math.high64_data)) }
    .low64_data 0x3b5b8 : { KEEP(*(.r1.math.low64_data)) }
    .divzero32_data 0x3bac4 : { KEEP(*(.r1.math.divzero32_data)) }
    .invalid32_data 0x3bae0 : { KEEP(*(.r1.math.invalid32_data)) }
    .high32_data 0x3baf0 : { KEEP(*(.r1.math.high32_data)) }
    .low32_data 0x3bb00 : { KEEP(*(.r1.math.low32_data)) }
}
INCLUDE r1/source-config/runtime/native_math_round_verification.ld
