/* Native platform/context/dispatch children 0x52dc40/0x52e0a2/0x52edd8.
 * Pin words 0x183/0x93 are authenticated at ROM 0x78ee40/44; the third
 * pin word and dispatch byte are live RAM 0x200001b0/0x20074f51. */
#include <stdint.h>
extern volatile uint32_t audio_ble_hci_radio_platform_pin_200001b0;
extern volatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f51;
extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* selected 0x480f0c */
extern int32_t g2_gpio_hal_write(uint32_t,uint32_t); /* selected 0x480fd6 */
extern void audio_ble_hci_radio_stack_stop_55c430(uint32_t);
extern int32_t audio_ble_radio_stack_option_55c7e8(uint32_t,uint32_t,uint32_t);
static uint32_t get32(const uint8_t *p) {uint32_t x;__builtin_memcpy(&x,p,4u);return x;}

uint32_t audio_ble_radio_platform_init_body(uint32_t a,uint32_t b,
                                             uint32_t c,uint32_t high) {
    (void)a;(void)b;(void)c;
    (void)g2_codec_pin_function(0x95u,0x183u);
    (void)g2_codec_pin_function(0x75u,0x93u);
    (void)g2_codec_pin_function(0x5du,0x183u);
    (void)g2_codec_pin_function(0x0fu,0x93u);
    (void)g2_codec_pin_function(0x88u,0x183u);
    (void)g2_codec_pin_function(0x8au,audio_ble_hci_radio_platform_pin_200001b0);
    (void)g2_gpio_hal_write(0x95u,1u);
    (void)g2_gpio_hal_write(0x5du,0u);
    (void)g2_gpio_hal_write(0x88u,0u);
    return high;
}
__attribute__((naked)) uint32_t audio_ble_radio_platform_init_52dc40(void) {
    __asm volatile("b audio_ble_radio_platform_init_body");
}

uint32_t audio_ble_radio_context_init_52e0a2(void *record) {
    uint8_t *r=(uint8_t *)record;
    if(r[8u]!=1u)return 0x0cu;
    if(r[9u]!=0u) {
        uint32_t stack=get32(r+4u);
        audio_ble_hci_radio_stack_stop_55c430(stack);
        (void)audio_ble_radio_stack_option_55c7e8(stack,2u,1u);
        r[9u]=0u;
    }
    return 0u;
}

void audio_ble_radio_dispatch_set_52edd8(uint32_t value) {
    audio_ble_hci_radio_dispatch_cell_20074f51=(uint8_t)value;
}
