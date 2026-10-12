/* Native settings_get_terminal_mode 0x46c630. Literal 0x46c6a8 points
 * to the shared live settings record 0x20072da8. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[];
uint32_t audio_settings_terminal_mode(void) {return audio_settings_config_live[0x1du];}
