/* Verification only; not a final firmware image linker script. */
SECTIONS
{
    .ceil_data 0x389d8 : { KEEP(*(.r1.math.ceil_data)) }
    .floor_data 0x39208 : { KEEP(*(.r1.math.floor_data)) }
}
INCLUDE r1/source-config/runtime/native_math_selection_verification.ld
