/* Native manual brightness path 0x46c1c8..0x46c212; ALS getter 0x4ae946. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[]; /* stock RAM 0x20072da8 */
extern uint32_t audio_quicklist_tick_now(void); /* native 0x44a1c6 */
extern uint32_t audio_als_manual_set_brightness_4ae81c(uint32_t);
extern uint32_t audio_als_scale_active; /* stock RAM 0x20000064 */
extern void audio_uart_hand_mismatch_448e34(void);
extern uint32_t audio_setting_brightness_refresh_46c18c(void);
__attribute__((noinline)) uint32_t audio_setting_als_scale_get_4ae946(void) {
    return audio_als_scale_active;
}
uint32_t audio_setting_manual_brightness_46c1c8(uint32_t value) {
    if(value>100u)value=100u;
    else if(value<2u)value=2u;
    value&=~1u;
    if(audio_settings_config_live[2]!=0u) {
        *(uint32_t *)(void *)(audio_settings_config_live+4u)=audio_quicklist_tick_now();
        if(audio_als_manual_set_brightness_4ae81c(value)==0u) {
            *(uint32_t *)(void *)(audio_settings_config_live+0x24u)=
                audio_setting_als_scale_get_4ae946();
            audio_settings_config_live[0x2cu]=1u;
            audio_uart_hand_mismatch_448e34();
        }
    }
    audio_settings_config_live[1]=(uint8_t)value;
    (void)audio_setting_brightness_refresh_46c18c();
    return 0u;
}
