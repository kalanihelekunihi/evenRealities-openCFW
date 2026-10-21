/* Hub timer state and authenticated eight-byte timeout template. */
#include <stdint.h>

void *audio_hub_timer_handle __attribute__((section(".g2_ram_20074908")));
uint8_t audio_hub_timer_control_block[44u]
    __attribute__((section(".g2_ram_20073650")));
const uint8_t audio_hub_timeout_message_template[8u]
    __attribute__((section(".g2_rom_0078e47c"))) = {0u};
