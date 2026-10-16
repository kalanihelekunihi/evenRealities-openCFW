/* Native settings brightness refresh 0x46c18c..0x46c1bc. */
#include <stdint.h>
extern uint32_t audio_log_wake_allowed(void); /* 0x443484 */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern void audio_setting_display_start_466890(void);
extern void *audio_als_callback_context_47394c(void);
extern uint8_t audio_settings_config_live[]; /* stock RAM 0x20072da8 */
uint32_t audio_setting_brightness_refresh_46c18c(void) {
    if(audio_log_wake_allowed()==0u) {
        if(audio_uart_device_role_get()==1u)
            audio_setting_display_start_466890();
        return 0u;
    }
    void *context=audio_als_callback_context_47394c();
    uintptr_t callback=*(const uintptr_t *)((const uint8_t *)context+0x14u);
    ((void (*)(uint32_t))callback)(audio_settings_config_live[1]);
    return 0u;
}
