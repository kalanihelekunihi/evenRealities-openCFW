/* Native setting display-start selector 0x466890..0x4668ae. */
#include <stdint.h>
extern uint32_t audio_settings_terminal_mode(void); /* stock 0x46c630 */
extern void audio_uart_master_display_start(uint32_t,const void *,uint16_t,uint32_t); /* 0x464b2e */
void audio_setting_display_start_466890(void) {
    uint32_t application_id=audio_settings_terminal_mode()!=0u?0x30u:1u;
    audio_uart_master_display_start(application_id,0,0u,0u);
}
