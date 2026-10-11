/* Native radio child bodies 0x52eece, 0x52dd7c, and 0x52df12.
 * Product pin mode and runtime context retain their original ownership. */
#include <stdint.h>

extern int32_t g2_gpio_hal_write(uint32_t pin, uint32_t mode); /* 0x480fd6 */
extern uint32_t g2_codec_pin_function(uint32_t pin, uint32_t mode); /* 0x480f0c */
extern volatile uint32_t audio_ble_hci_radio_pin_mode; /* *DAT_0052e93c */

void audio_ble_hci_radio_switch_52eece(uint8_t enabled) {
    (void)g2_gpio_hal_write(0x88u, enabled == 0u ? 0u : 1u);
}

void audio_ble_hci_radio_pins_52dd7c(void) {
    (void)g2_gpio_hal_write(0x5du, 0u);
    (void)g2_codec_pin_function(0x8au, audio_ble_hci_radio_pin_mode);
}

extern void audio_ble_hci_radio_mask_4c2e30(uint32_t, uint32_t);
extern void audio_ble_hci_radio_stack_stop_55c430(uint32_t);
extern void audio_ble_hci_radio_stack_option_55c7e8(uint32_t, uint32_t, uint32_t);
extern void audio_ble_hci_radio_stack_reset_55c286(uint32_t);

uint32_t audio_ble_hci_radio_reset_52df12(void *context) {
    uint8_t *base=(uint8_t *)context;
    uint32_t selector=*(uint32_t *)(void *)base;
    if(selector>=9u) return 1u;
    uint32_t stack=*(uint32_t *)(void *)(base+4u);
    audio_ble_hci_radio_mask_4c2e30(selector,0u);
    audio_ble_hci_radio_stack_stop_55c430(stack);
    if(base[9u]!=0u) audio_ble_hci_radio_stack_option_55c7e8(stack,2u,1u);
    base[9u]=0u;
    audio_ble_hci_radio_stack_reset_55c286(stack);
    base[8u]=0u;
    return 0u;
}
