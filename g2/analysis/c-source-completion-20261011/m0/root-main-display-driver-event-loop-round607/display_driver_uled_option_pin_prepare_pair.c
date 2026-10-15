/* Apollo option pin preparation 0x592c78 and 0x5bc690. The shared
 * 0x78ee40 word is ROM configuration data, not a source-owned constant.
 */
#include <stdint.h>

extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t);
extern uint32_t g2_codec_pin_function(uint32_t,uint32_t);

void display_driver_uled_type0_pin_prepare_592c78(void) {
    const uint8_t *mode = audio_ble_hci_radio_mode_state_50938e(1u);
    uint32_t pin = *(volatile const uint32_t *)(uintptr_t)0x78ee40u;
    if (mode[0] < 3u) (void)g2_codec_pin_function(0x8fu,pin);
    if (mode[0] < 4u) (void)g2_codec_pin_function(0x80u,pin);
    (void)g2_codec_pin_function(0x8eu,pin);
}

void display_driver_uled_type1_pin_prepare_5bc690(void) {
    (void)audio_ble_hci_radio_mode_state_50938e(1u);
    uint32_t pin = *(volatile const uint32_t *)(uintptr_t)0x78ee40u;
    (void)g2_codec_pin_function(0x8eu,pin);
    (void)g2_codec_pin_function(0x80u,pin);
}
