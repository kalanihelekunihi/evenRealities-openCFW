/* Native settings_configure_auto_brightness 0x46c158. */
#include <stdint.h>
/* Fix 58: stock 0x46c02a/0x46c164/0x46c17e address these cells as
 * [settings_config_live 0x20072da8, #2] (strb/ldrb) and [#4] (str); they are
 * fields of the live settings config, not separate objects. */
extern uint8_t audio_settings_config_live[]; /* stock RAM 0x20072da8 */
#define audio_uart_auto_brightness_enabled_cell \
    (*(volatile uint8_t *)(void *)(audio_settings_config_live + 2u)) /* RAM 0x20072daa */
#define audio_uart_auto_brightness_profile_cell \
    (*(volatile uint32_t *)(void *)(audio_settings_config_live + 4u)) /* RAM 0x20072dac */
extern uint32_t audio_log_wake_allowed(void); /* selected 0x443484 */
extern uint32_t SVC_Settings_AutoBrightnessOpen(void); /* source 0x46c01c */
extern uint32_t SVC_Settings_AutoBrightnessClose(void); /* source 0x46c0e8 */
uint32_t audio_uart_auto_brightness_configure(uint32_t value) {
    if(value==1u) {
        audio_uart_auto_brightness_enabled_cell=1u;
        if(audio_log_wake_allowed()==1u)
            (void)SVC_Settings_AutoBrightnessOpen();
    } else {
        audio_uart_auto_brightness_enabled_cell=0u;
        audio_uart_auto_brightness_profile_cell=0u;
        (void)SVC_Settings_AutoBrightnessClose();
    }
    return 0;
}
