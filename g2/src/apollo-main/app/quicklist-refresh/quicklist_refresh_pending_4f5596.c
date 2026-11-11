/* Apollo QuickList pending-count update at 0x4f5596..0x4f55df. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_quicklist_ui_data_2012a72c[] __asm__("g2_quicklist_ui_data_2012a72c");

void audio_quicklist_refresh_pending_4f5596(void) {
    const uint8_t state = *(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_ui_data_2012a72c+0x2e4eu);
    volatile uint16_t *const count = (volatile uint16_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_ui_data_2012a72c);
    const volatile uint16_t *const increment =
        (const volatile uint16_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_ui_data_2012a72c+0x2e48u);
    if (state == 1u) {
        *count = *increment;
    } else if (state == 2u || state == 3u) {
        const uint32_t sum = (uint32_t)*count + (uint32_t)*increment;
        *count = (uint16_t)(sum >= 41u ? 40u : sum);
    }
}
