#ifndef R1_NATIVE_FLOAT_BITS_H
#define R1_NATIVE_FLOAT_BITS_H
#include <stdint.h>
/* Raw core-register interfaces. Classifier auxiliary arguments explicitly
 * model native r2/r3 or r1/r2/r3 slots; the final incoming word is preserved in
 * r3. These are not generic hard-float double/float public math prototypes. */
uint32_t r1_binary64_classify_bits(uint64_t bits,uint32_t incoming2,uint32_t incoming3);
uint32_t r1_binary32_classify_bits(uint32_t bits,uint32_t incoming1,uint32_t incoming2,uint32_t incoming3);
uint64_t r1_signed32_to_binary64_bits(uint32_t word);
uint64_t r1_unsigned32_to_binary64_bits(uint32_t word);
uint32_t r1_binary64_to_signed32_bits(uint64_t bits);
uint32_t r1_binary64_to_unsigned32_bits(uint64_t bits);
uint64_t r1_binary32_to_binary64_bits(uint32_t bits);
uint64_t r1_binary64_subtract_bits(uint64_t a,uint64_t b);
uint64_t r1_binary64_reverse_subtract_bits(uint64_t a,uint64_t b);
uint64_t r1_binary64_scale_power2_bits(uint64_t bits,uint32_t scale);
uint32_t r1_native_floating_environment_control(void);
#endif
