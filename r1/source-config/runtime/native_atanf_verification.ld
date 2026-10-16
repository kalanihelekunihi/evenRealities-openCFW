/* Verification placement only; final firmware layout remains unproven. */
SECTIONS { .atanf_data 0x3889c : { KEEP(*(.r1.math.atanf_data)) } }
INCLUDE r1/source-config/runtime/native_float_logs_verification.ld
