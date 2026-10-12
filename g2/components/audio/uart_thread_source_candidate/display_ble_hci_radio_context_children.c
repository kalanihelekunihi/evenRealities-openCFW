/* Native 0x52e49a/0x4910f4. ROM slot 0x52e6a8 points to
 * 0x78ee44 = 0x93 base pin function. */
#include <stdint.h>

extern uint32_t g2_codec_pin_function(uint32_t,uint32_t);
extern void audio_ble_vendor_yield_4807a0(uint32_t);

void audio_ble_radio_context_setup_52e49a(uint32_t enabled) {
    uint32_t config=0x93u;
    if((uint8_t)enabled!=0u)config=(config&0xffff1fffu)|0x2000u;
    (void)g2_codec_pin_function(0x75u,config);
}

void audio_ble_hci_radio_reset_4910f4(uint32_t milliseconds) {
    audio_ble_vendor_yield_4807a0(milliseconds*1000u);
}
