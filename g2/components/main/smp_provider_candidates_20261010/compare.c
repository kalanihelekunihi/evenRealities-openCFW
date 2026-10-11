#include <stdint.h>

/* Stock 0x44b610..0x44b63a: bounded strcmp/strncmp ordering. */
uint32_t g2_smp_candidate_compare(void *context, uint32_t lhs_word,
                                  uint32_t rhs_word, uint32_t length)
{
    (void)context;
    const uint8_t *lhs = (const uint8_t *)(uintptr_t)lhs_word;
    const uint8_t *rhs = (const uint8_t *)(uintptr_t)rhs_word;
    while (length != 0u) {
        uint8_t a = *lhs;
        uint8_t b = *rhs;
        if (a != b) return a < b ? UINT32_MAX : 1u;
        if (a == 0u) return 0u;
        ++lhs;
        ++rhs;
        --length;
    }
    return 0u;
}
