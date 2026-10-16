/* Verification only; the three native PC-relative table offsets are replaced
 * by named C arrays, not imported as executable or opaque configuration. */
SECTIONS
{
    .expf_coeff 0x390b4 : { KEEP(*(.r1.math.expf_coeff)) }
    .expf_scale 0x390e0 : { KEEP(*(.r1.math.expf_scale)) }
    .expf_tables 0xbd7e0 : { KEEP(*(.r1.math.expf_tables)) }
    .tanhf_coeff 0x3b3f8 : { KEEP(*(.r1.math.tanhf_coeff)) }
}
INCLUDE r1/source-config/runtime/native_math_special_verification.ld
