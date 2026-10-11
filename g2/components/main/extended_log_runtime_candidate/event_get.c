/* Source-backed stock xEventGroupGetBits entry 0x47ed64. */
#include <stdint.h>
extern uint32_t audio_mask_save(void);
extern void audio_mask_restore(uint32_t saved);
uint32_t g2_log_event_get_bits(uint32_t event_handle) {
    uint32_t saved = audio_mask_save();
    uint32_t bits = *(volatile uint32_t *)(uintptr_t)event_handle;
    audio_mask_restore(saved);
    return bits;
}
