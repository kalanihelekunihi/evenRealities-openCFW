/* Verification only; original whole-image placement remains unproven. */
SECTIONS
{
    .ceilf_data 0x38a54 : { KEEP(*(.r1.math.ceilf_data)) }
    .floorf_data 0x39284 : { KEEP(*(.r1.math.floorf_data)) }
}
INCLUDE r1/source-config/runtime/native_math_verification.ld
