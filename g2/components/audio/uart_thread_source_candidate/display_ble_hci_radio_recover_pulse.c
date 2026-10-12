/* Native radio reset 0x52e8a4 and pin pulse loop 0x52e854. */
#include <stdint.h>

extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* 0x480f0c */
extern int32_t g2_gpio_hal_write(uint32_t,uint32_t); /* 0x480fd6 */
extern void audio_ble_hci_radio_reset_4910f4(uint32_t); /* millisecond delay */
extern void audio_ble_hci_boot_delay_491102(uint32_t);

void audio_ble_hci_radio_reset_52e8a4(void) {
    (void)g2_gpio_hal_write(0x5du,0u);
    audio_ble_hci_radio_reset_4910f4(10u);
    (void)g2_gpio_hal_write(0x5du,1u);
}

void audio_ble_radio_wait_pulse_52e854(uint32_t duration) {
    (void)g2_codec_pin_function(15u,0x183u); /* ROM 0x78ee40 */
    (void)g2_gpio_hal_write(15u,0u);
    uint32_t count=0u;
    while(count<((duration*1000u)/33u)) {
        (void)g2_gpio_hal_write(15u,0u);
        audio_ble_hci_boot_delay_491102(16u);
        (void)g2_gpio_hal_write(15u,1u);
        audio_ble_hci_boot_delay_491102(16u);
        ++count;
    }
}
