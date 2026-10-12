/* Native 0x52dd24 selects serial-mode pins. ROM 0x78ee40/44 authenticate
 * immutable functions 0x183/0x93; pin ownership remains HAL runtime state. */
#include <stdint.h>
extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* 0x480f0c */
extern int32_t g2_gpio_hal_write(uint32_t,uint32_t); /* 0x480fd6 */
void audio_ble_radio_alt_mode_52dd24(void) {
    (void)g2_codec_pin_function(0x3du,0x183u);
    (void)g2_codec_pin_function(0x3eu,0x93u);
    (void)g2_codec_pin_function(0x3fu,0x183u);
    (void)g2_gpio_hal_write(0x3du,0u);
    (void)g2_gpio_hal_write(0x3fu,0u);
}
