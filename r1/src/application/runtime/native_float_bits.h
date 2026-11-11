#ifndef R1_NATIVE_FLOAT_BITS_H
#define R1_NATIVE_FLOAT_BITS_H
#include <stdint.h>
/* Raw integer classifier result, in native R0..R3 order on ARM:
 * encoded tag, auxiliary word, limit, unchanged incoming3. C callers read
 * lane0. Base AAPCS lowers this container to four core registers. */
typedef uint32_t r1_native_classification __attribute__((vector_size(16)));
#if defined(__arm__) || defined(__thumb__)
#define R1_CLASSIFIER_CORE_ABI __attribute__((pcs("aapcs")))
#else
#define R1_CLASSIFIER_CORE_ABI
#endif
R1_CLASSIFIER_CORE_ABI r1_native_classification r1_binary64_classify_bits(uint64_t bits,uint32_t incoming2,uint32_t incoming3);
R1_CLASSIFIER_CORE_ABI r1_native_classification r1_binary32_classify_bits(uint32_t bits,uint32_t incoming1,uint32_t incoming2,uint32_t incoming3);
uint64_t r1_signed32_to_binary64_bits(uint32_t word);
uint64_t r1_unsigned32_to_binary64_bits(uint32_t word);
uint32_t r1_binary64_to_signed32_bits(uint64_t bits);
uint32_t r1_binary64_to_unsigned32_bits(uint64_t bits);
uint64_t r1_binary32_to_binary64_bits(uint32_t bits);
uint64_t r1_binary64_subtract_bits(uint64_t a,uint64_t b);
uint64_t r1_binary64_reverse_subtract_bits(uint64_t a,uint64_t b);
uint64_t r1_binary64_scale_power2_bits(uint64_t bits,uint32_t scale);
uint32_t r1_native_floating_environment_control(void);
/* The native binary64 comparison helper orders encoded integer keys, not
 * IEEE values. C/Z are the only APSR bits consumed by these C callers. */
static inline uint64_t r1_binary64_order_key(uint64_t bits)
{ return (bits>>63) ? bits : UINT64_C(0x8000000000000000)-bits; }
static inline uint32_t r1_binary64_comparison_cz(uint64_t a,uint64_t b)
{
    a=r1_binary64_order_key(a);b=r1_binary64_order_key(b);
    return (a>=b ? UINT32_C(0x20000000) : 0u) |
           (a==b ? UINT32_C(0x40000000) : 0u);
}
#endif
