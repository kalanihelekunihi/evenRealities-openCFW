#include <stdint.h>

/* Stock 0x59c7ac ABI: signed 64-bit input and raw IEEE-754 result in r0:r1. */
uint64_t g2_audio_dsp_i64_to_double_bits(int64_t value) {
    union { double floating; uint64_t bits; } converted;
    converted.floating = (double)value;
    return converted.bits;
}
