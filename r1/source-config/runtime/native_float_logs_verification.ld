/* Verification only. Native PC-relative table offsets become named C arrays. */
SECTIONS
{
    .log10f_coeff 0x39830 : { KEEP(*(.r1.math.log10f_coeff)) }
    .log10f_high 0x3983c : { KEEP(*(.r1.math.log10f_high)) }
    .log10f_tail 0x39844 : { KEEP(*(.r1.math.log10f_tail)) }
    .logf_coeff 0x399a4 : { KEEP(*(.r1.math.logf_coeff)) }
    .logf_high 0x399b0 : { KEEP(*(.r1.math.logf_high)) }
    .logf_tail 0x399b8 : { KEEP(*(.r1.math.logf_tail)) }
    .float_log_tables 0xbd848 : { KEEP(*(.r1.math.float_log_tables)) }
}
INCLUDE r1/source-config/runtime/native_expf_tanhf_verification.ld
