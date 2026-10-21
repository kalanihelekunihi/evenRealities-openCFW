/* Apollo settings_set_terminal_mode, native 0x46c63c. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[]; /* native RAM 0x20072da8 */
extern uint32_t audio_settings_persist_record(void *); /* native 0x4b04c4 */

void audio_settings_terminal_mode_set(uint32_t enabled) {
    audio_settings_config_live[0x1du]=(uint8_t)enabled;
    (void)audio_settings_persist_record(audio_settings_config_live+0x1cu);
}
