/* Apollo live settings record at native SRAM 0x20072da8.
 * SVC_Settings_Init clears 0x50 bytes before restoring source records.
 * Final linker address and ownership of adjacent RAM remain gated.
 */
#include <stdint.h>
uint8_t audio_settings_config_live[0x50];
_Static_assert(sizeof audio_settings_config_live==0x50u,"native settings clear extent");
