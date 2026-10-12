/* Native settings_configure_auto_brightness 0x46c158. */
#include <stdint.h>
extern volatile uint8_t audio_uart_auto_brightness_enabled_cell; /* RAM 0x20072daa */
extern volatile uint32_t audio_uart_auto_brightness_profile_cell; /* RAM 0x20072dac */
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
