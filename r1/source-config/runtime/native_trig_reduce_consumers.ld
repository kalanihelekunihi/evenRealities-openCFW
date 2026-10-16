/* Verification placement; full image placement remains unproven. */
SECTIONS {
 .trig_reduce_table 0xbdb48 : { KEEP(*(.r1.math.trig_reduce_table)) }
 .trig_reduce_coeff 0x3bc44 : { KEEP(*(.r1.math.trig_reduce_coeff)) }
}
INCLUDE r1/source-config/runtime/native_atan2f_verification.ld
