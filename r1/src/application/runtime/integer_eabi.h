#ifndef R1_INTEGER_EABI_H
#define R1_INTEGER_EABI_H

#include <stdint.h>

/* Signed operands and results use their two's-complement bit patterns. */
uint64_t r1_runtime_udivmod(uint64_t numerator, uint64_t denominator,
                           uint64_t *remainder);
uint64_t r1_runtime_sdivmod(uint64_t numerator, uint64_t denominator,
                           uint64_t *remainder);

#endif
