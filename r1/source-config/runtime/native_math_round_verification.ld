/* Verification placement only; full original-image placement remains open. */
SECTIONS { .round_data 0x3ad50 : { KEEP(*(.r1.math.round_data)) } }
INCLUDE r1/source-config/runtime/native_double_directed_verification.ld
