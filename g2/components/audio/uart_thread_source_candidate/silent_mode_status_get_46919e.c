/* Native settings_get_config 0x46b44c and silent_mode_status_get 0x46919e. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[]; /* native RAM 0x20072da8 */

uint8_t *audio_settings_get_config_46b44c(void) {
    return audio_settings_config_live;
}

uint8_t audio_silent_mode_status_get(void) {
    const uint8_t *config=audio_settings_get_config_46b44c();
    return config!=0 && config[0x15u]!=0u;
}
