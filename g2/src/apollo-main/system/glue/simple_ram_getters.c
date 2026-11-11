#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_log_output_flags[] __asm__("g2_log_output_flags");

/* Original entry 0x43d0ce: LDR literal 0x20004543, LDRB [r0], BX LR. */
uint32_t platform_log_flags(void) {
    return *(volatile const uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_log_output_flags);
}
uint32_t stock_audio_log_mask(void) __attribute__((alias("platform_log_flags")));
uint32_t audio_log_flags(void) __attribute__((alias("platform_log_flags")));
__typeof__(platform_log_flags) g2_flashdb_candidate_flags __attribute__((alias("platform_log_flags")));

/* Original entry 0x4abe60 (productModeGet): audio_role is an alias of
 * audio_uart_command_pending in app/command-mode/command_mode.c. */
