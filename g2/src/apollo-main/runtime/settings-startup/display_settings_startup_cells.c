/* Apollo Main compressed SRAM record 0x75d3f4 initializes display profile
 * and brightness at 0x20000648 and 0x2000064c. The settings path later
 * updates both values; exact native placement remains a linker gate. */
#include <stdint.h>

uint32_t audio_settings_display_profile_cell = 8u;
uint32_t audio_settings_display_brightness_cell = 64u;
