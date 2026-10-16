/* Source core verification; no native core fixture binding. */
SECTIONS {
 .pow_dispatch_prefix 0x39df0 : { KEEP(*(.r1.math.pow_dispatch_prefix)) }
 .pow_dispatch_suffix 0x39e24 : { KEEP(*(.r1.math.pow_dispatch_suffix)) }
 .pow_near 0x39e40 : { KEEP(*(.r1.math.pow_near)) }
 .pow_normal 0x3a288 : { KEEP(*(.r1.math.pow_normal)) }
 .pow_log 0x3a2bc : { KEEP(*(.r1.math.pow_log)) }
 .pow_limits 0x3a5d0 : { KEEP(*(.r1.math.pow_limits)) }
 .pow_scaling 0x3a5f4 : { KEEP(*(.r1.math.pow_scaling)) }
 .pow_tail 0x3a614 : { KEEP(*(.r1.math.pow_tail)) }
 .pow_base 0xbd8c8 : { KEEP(*(.r1.math.pow_base)) }
 .pow_log_high 0xbd8d8 : { KEEP(*(.r1.math.pow_log_high)) }
 .pow_log_low 0xbd8e8 : { KEEP(*(.r1.math.pow_log_low)) }
 .pow_log_poly 0xbd8f8 : { KEEP(*(.r1.math.pow_log_poly)) }
 .pow_exp_poly 0xbd928 : { KEEP(*(.r1.math.pow_exp_poly)) }
}
/* Source core verification: no native-core fixture binding. */
SECTIONS {
 .powf_dispatch_data 0x3ac68 : { KEEP(*(.r1.math.powf_dispatch_data)) }
 .powf_prefix 0x3aa38 : { KEEP(*(.r1.math.powf_prefix)) }
 .powf_exponential 0x3aa5c : { KEEP(*(.r1.math.powf_exponential)) }
 .powf_scaling 0x3aa74 : { KEEP(*(.r1.math.powf_scaling)) }
 .powf_near_one 0x3ac78 : { KEEP(*(.r1.math.powf_near_one)) }
 .powf_log_table 0xbd950 : { KEEP(*(.r1.math.powf_log_table)) }
 .powf_exp_head 0xbda10 : { KEEP(*(.r1.math.powf_exp_head)) }
 .powf_exp_scale 0xbda50 : { KEEP(*(.r1.math.powf_exp_scale)) }
 .powf_exp_tail 0xbd9d0 : { KEEP(*(.r1.math.powf_exp_tail)) }
}
/* Verification only: shared zero data is emitted with source text. */
SECTIONS {
 .log_prefix 0x39688 : { KEEP(*(.r1.math.log_prefix)) }
 .log_suffix 0x396bc : { KEEP(*(.r1.math.log_suffix)) }
 .log_even 0xbd810 : { KEEP(*(.r1.math.log_even)) }
 .log_odd 0xbd828 : { KEEP(*(.r1.math.log_odd)) }
}
/* Verification placement only; final image layout remains gated. */
SECTIONS {
 .exp_prefix 0x38e80 : { KEEP(*(.r1.math.exp_prefix)) }
 .exp_middle 0x38ebc : { KEEP(*(.r1.math.exp_middle)) }
 .exp_reduction 0x38ecc : { KEEP(*(.r1.math.exp_reduction)) }
 .exp_suffix 0x38ef4 : { KEEP(*(.r1.math.exp_suffix)) }
 .exp_high 0xbd798 : { KEEP(*(.r1.math.exp_high)) }
 .exp_low 0xbd7a8 : { KEEP(*(.r1.math.exp_low)) }
 .exp_half 0xbd788 : { KEEP(*(.r1.math.exp_half)) }
 .exp_polynomial 0xbd7b8 : { KEEP(*(.r1.math.exp_polynomial)) }
}
/* Verification only; source expm1 replaces the prior native fixture. */
SECTIONS {
 .expm1_prefix 0x3b9e8 : { KEEP(*(.r1.math.expm1_prefix)) }
 .expm1_suffix 0x3ba5c : { KEEP(*(.r1.math.expm1_suffix)) }
 .tanh_local 0x3b300 : { KEEP(*(.r1.math.tanh_local)) }
}
/* Verification placement only; original image layout remains gated. */
SECTIONS {
 .atan_local 0x38460 : { KEEP(*(.r1.math.atan_local)) }
 .atan_odd 0xbd758 : { KEEP(*(.r1.math.atan_odd)) }
 .atan_even 0xbd730 : { KEEP(*(.r1.math.atan_even)) }
 .atan_low 0xbd710 : { KEEP(*(.r1.math.atan_low)) }
 .atan_high 0xbd6f0 : { KEEP(*(.r1.math.atan_high)) }
}
/* Verification only; full original placement remains gated. */
SECTIONS { .tanf_data 0x3b18c : { KEEP(*(.r1.math.tanf_data)) } }
/* Verification only; final original placement remains gated. */
SECTIONS { .sinf_data 0x3af5c : { KEEP(*(.r1.math.sinf_data)) } }
/* Verification only; original image layout remains gated. */
SECTIONS { .cosf_data 0x38b74 : { KEEP(*(.r1.math.cosf_data)) } }
/* Expanded r1/source-config/runtime/native_trig_reduce_consumers.ld */
/* Verification placement; full image placement remains unproven. */
SECTIONS {
 .trig_reduce_table 0xbdb48 : { KEEP(*(.r1.math.trig_reduce_table)) }
 .trig_reduce_coeff 0x3bc44 : { KEEP(*(.r1.math.trig_reduce_coeff)) }
}
/* Expanded r1/source-config/runtime/native_atan2f_verification.ld */
/* Verification placement only; final original-image layout remains open. */
SECTIONS { .atan2f_data 0x3871c : { KEEP(*(.r1.math.atan2f_data)) } }
/* Expanded r1/source-config/runtime/native_atanf_verification.ld */
/* Verification placement only; final firmware layout remains unproven. */
SECTIONS { .atanf_data 0x3889c : { KEEP(*(.r1.math.atanf_data)) } }
/* Expanded r1/source-config/runtime/native_float_logs_verification.ld */
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
/* Expanded r1/source-config/runtime/native_expf_tanhf_verification.ld */
/* Verification only; the three native PC-relative table offsets are replaced
 * by named C arrays, not imported as executable or opaque configuration. */
SECTIONS
{
    .expf_coeff 0x390b4 : { KEEP(*(.r1.math.expf_coeff)) }
    .expf_scale 0x390e0 : { KEEP(*(.r1.math.expf_scale)) }
    .expf_tables 0xbd7e0 : { KEEP(*(.r1.math.expf_tables)) }
    .tanhf_coeff 0x3b3f8 : { KEEP(*(.r1.math.tanhf_coeff)) }
}
/* Expanded r1/source-config/runtime/native_math_special_verification.ld */
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
/* Expanded r1/source-config/runtime/native_math_round_verification.ld */
/* Verification placement only; full original-image placement remains open. */
SECTIONS { .round_data 0x3ad50 : { KEEP(*(.r1.math.round_data)) } }
/* Expanded r1/source-config/runtime/native_double_directed_verification.ld */
/* Verification only; not a final firmware image linker script. */
SECTIONS
{
    .ceil_data 0x389d8 : { KEEP(*(.r1.math.ceil_data)) }
    .floor_data 0x39208 : { KEEP(*(.r1.math.floor_data)) }
}
/* Expanded r1/source-config/runtime/native_math_selection_verification.ld */
/* Verification only; original whole-image placement remains unproven. */
SECTIONS
{
    .ceilf_data 0x38a54 : { KEEP(*(.r1.math.ceilf_data)) }
    .floorf_data 0x39284 : { KEEP(*(.r1.math.floorf_data)) }
}
/* Expanded r1/source-config/runtime/native_math_verification.ld */
/* Verification placement only. This is not a final firmware linker script. */
SECTIONS
{
    .errno 0x20007dbc (NOLOAD) : { KEEP(*(.r1.runtime.errno)) }
    .round_one 0x28330 : { KEEP(*(.r1.float.round_one)) }
    .decimal_zero 0x3f6a8 : { KEEP(*(.r1.format.decimal_zero)) }
    .text 0x1000000 : { *(.text*) *(.rodata*) *(.r1.math.pow_dispatch_zero) *(.r1.math.log_zero) *(.r1.math.expm1_polynomial) }
    /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}










