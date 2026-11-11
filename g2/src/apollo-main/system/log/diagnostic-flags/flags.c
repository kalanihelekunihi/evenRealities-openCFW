#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_ble_trace_level_cell[] __asm__("audio_ble_trace_level_cell");
extern unsigned char g2ref_g2_log_output_flags[] __asm__("g2_log_output_flags");

/* Stock getter 0x0043d0ce: g2_flashdb_candidate_flags is an alias of
 * platform_log_flags in system/glue/simple_ram_getters.c. */
uint32_t g2_flashdb_candidate_flags(void);

/* Both incoming values are unused by the original six-byte gate getter. */
uint32_t g2_smp_candidate_log_gate(void *context, uint32_t carry)
{
    (void)context;
    (void)carry;
    return *(volatile const uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_audio_ble_trace_level_cell);
}

uint32_t g2_smp_candidate_log_flags(void *context)
{
    (void)context;
    return g2_flashdb_candidate_flags();
}
