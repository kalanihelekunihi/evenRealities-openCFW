/* Native 0x46c622/0x46c600 and authenticated ROM tables. */
#include <stdint.h>
extern uint8_t audio_uart_device_role_get(void); /* same cell/instructions as 0x45a570 */
static const uint8_t brightness_table[13]={0xc0,0xb0,0xa0,0x90,0x80,0x70,0x60,
                                           0x50,0x40,0x30,0x20,0x10,0x00}; /* ROM 0x788f00 */
static const uint8_t role_one_profiles[3]={0x18,0x20,0x28}; /* ROM 0x78f3c8 */
static const uint8_t other_profiles[3]={0x28,0x20,0x18}; /* ROM 0x78f3cc */
extern uint32_t audio_settings_display_brightness_cell; /* RAM 0x2000064c */
extern uint32_t audio_settings_display_profile_cell; /* RAM 0x20000648 */
uint32_t audio_settings_brightness_level(uint8_t level) {
    if(level>12u) level=12u;
    return brightness_table[level];
}
uint32_t audio_settings_profile_for_role(uint8_t index) {
    if(index>2u) index=2u;
    return audio_uart_device_role_get()==1u ? role_one_profiles[index]:other_profiles[index];
}
/* Stock 0x46C9D0 (audio_settings_display_apply) */
uint32_t audio_settings_display_apply(uint32_t brightness,uint32_t profile) {
    audio_settings_display_brightness_cell=brightness;
    audio_settings_display_profile_cell=profile;
    return 0u;
}
