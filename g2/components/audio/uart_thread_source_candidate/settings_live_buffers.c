#include <stdint.h>

/* Native init clears 0x50 bytes at 0x20072da8. Exact allocation extent
 * beyond this proven minimum remains a whole-image RAM-layout gate. */
uint8_t audio_settings_config_live[0x50]
    __attribute__((section(".g2.ram.settings_config_live"),used,aligned(4)));

/* Native full-status builder reads through offset 12 at 0x20072608.
 * The complete producer-owned allocation extent is still unknown. */
uint8_t audio_settings_last_message_state[13]
    __attribute__((section(".g2.ram.settings_last_message_state"),used,aligned(4)));
