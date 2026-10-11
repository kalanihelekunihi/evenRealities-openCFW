#include <stdint.h>

/* Authenticated stock getter 0x0043d0ce reads one byte at this SRAM address.
 * The initialized RAM allocation and writer lifecycle remain integration work. */
uint32_t g2_flashdb_candidate_flags(void)
{
    return *(volatile const uint8_t *)(uintptr_t)0x20004543u;
}

/* Both incoming values are unused by the original six-byte gate getter. */
uint32_t g2_smp_candidate_log_gate(void *context, uint32_t carry)
{
    (void)context;
    (void)carry;
    return *(volatile const uint8_t *)(uintptr_t)0x2007502fu;
}

uint32_t g2_smp_candidate_log_flags(void *context)
{
    (void)context;
    return g2_flashdb_candidate_flags();
}
