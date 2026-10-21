#include <stdint.h>

#define LOGGER_STATE 0x20070be8u

/* The normal-level (0..5) branch of 0x43d97c. Levels 6..255 have a
 * fatal callback/nonreturning branch and are deliberately outside this API. */
uint32_t g2_log_candidate_mask_normal(uint32_t level, uint32_t mask)
{
    uint32_t bits = *(volatile uint32_t *)(uintptr_t)
        (LOGGER_STATE + 216u + (uint8_t)level * 4u);
    return (bits & mask) != 0u;
}

/* Normal-level branches of 0x43d9f0 and 0x43da0a. Both have the same
 * observable source contract at this boundary. */
uint32_t g2_log_candidate_optional_128_normal(uint32_t level, uint32_t mask,
                                               uint32_t argument)
{
    return argument != 0u && g2_log_candidate_mask_normal(level, mask) != 0u;
}

uint32_t g2_log_candidate_optional_32_64_normal(uint32_t level, uint32_t mask,
                                                 uint32_t argument)
{
    return argument != 0u && g2_log_candidate_mask_normal(level, mask) != 0u;
}
