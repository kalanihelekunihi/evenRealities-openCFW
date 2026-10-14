/* Apollo wear-detection gate 0x49eb96, inlined 0x49ead8/0x46b44c accessors. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[0x50]; /* native 0x20072da8 */
uint32_t display_driver_wear_mode_cell; /* BSS 0x20074edc, linker placement gated */
uint32_t display_driver_wear_detect_49eb96(void) {
    if(audio_settings_config_live[0x14u]==0u) return 1u;
    return display_driver_wear_mode_cell==2u ? 1u : 0u;
}
