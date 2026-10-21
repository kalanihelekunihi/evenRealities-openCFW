/* Apollo Ambiq Nema mode cache at 0x4b06c0..0x4b072c. */
#include <stdint.h>

extern uint32_t audio_uart_ambiq_default_unit_4c791a(void);
extern void display_driver_nema_mode_513924(uint32_t,uint32_t,uint32_t,
                                             uint32_t);

void audio_uart_ambiq_texture_setup_4b06c0(uint32_t unit,uint32_t mode,
                                              uint32_t target,uint32_t surface,
                                              uint32_t alternate,uint32_t force) {
    if (unit==0u) unit=audio_uart_ambiq_default_unit_4c791a();
    uint8_t *const state=(uint8_t *)(uintptr_t)unit;
    const int32_t target_byte=(int8_t)target;
    const int32_t surface_byte=(int8_t)surface;
    const int32_t alternate_byte=(int8_t)alternate;
    const uint32_t previous_mode=*(uint32_t *)(void *)(state+0x50u);
    if ((force&0xffu)==0u && mode==previous_mode &&
        target_byte==(int8_t)state[0x54u] &&
        surface_byte==(int8_t)state[0x55u] &&
        alternate_byte==(int8_t)state[0x56u]) return;
    display_driver_nema_mode_513924(mode,(uint32_t)target_byte,
                                    (uint32_t)surface_byte,
                                    (uint32_t)alternate_byte);
    *(uint32_t *)(void *)(state+0x50u)=mode;
    state[0x54u]=(uint8_t)target;
    state[0x55u]=(uint8_t)surface;
    state[0x56u]=(uint8_t)alternate;
}
