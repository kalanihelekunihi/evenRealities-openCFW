/* Native timer-manager clear 0x5b38cc..0x5b38ed. */
#include <stdint.h>

__attribute__((used, section(".g2_conversate_timer_mgr_ram_20073a3c")))
uint8_t audio_conversate_timer_mgr_ram_20073a3c[0x1c];

static void clear_word(uint32_t offset) {
    *(uint32_t *)(void *)(audio_conversate_timer_mgr_ram_20073a3c + offset) = 0u;
}

void audio_conversate_timer_clear_5b38cc(void) {
    audio_conversate_timer_mgr_ram_20073a3c[0] = 0u;
    clear_word(4u);
    audio_conversate_timer_mgr_ram_20073a3c[8] = 0u;
    clear_word(12u);
    audio_conversate_timer_mgr_ram_20073a3c[16] = 0u;
    clear_word(20u);
    clear_word(24u);
}
