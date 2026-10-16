/* Verification placement only; final original-image layout remains open. */
SECTIONS { .atan2f_data 0x3871c : { KEEP(*(.r1.math.atan2f_data)) } }
INCLUDE r1/source-config/runtime/native_atanf_verification.ld
