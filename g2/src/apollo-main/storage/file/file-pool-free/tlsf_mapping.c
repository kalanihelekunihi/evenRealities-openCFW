/* Pinned TLSF size-class mapping, stock 0x4cfd66/0x4cff6c. */
#include <stdint.h>

uint32_t g2_tlsf_fls(uint32_t word) {
    if (!word) return UINT32_MAX;
    return 31u - (uint32_t)__builtin_clz(word);
}

void g2_tlsf_mapping_insert(uint32_t size, uint32_t *fl, uint32_t *sl) {
    if (size < 128u) {
        *fl = 0;
        *sl = size / 4u;
    } else {
        uint32_t msb = g2_tlsf_fls(size);
        *fl = msb - 6u;
        *sl = (size >> (msb - 5u)) ^ 32u;
    }
}
