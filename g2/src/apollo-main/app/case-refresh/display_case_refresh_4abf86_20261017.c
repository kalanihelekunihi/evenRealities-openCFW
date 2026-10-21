/* Stock Main BoxDetect graphics refresh 0x4abf86. */
#include <stdint.h>
extern uint32_t audio_log_wake_allowed(void); /* 0x443484 */
extern uint32_t audio_uart_case_status(void); /* 0x4acad0 */
extern uint32_t audio_wear_child_46b0ec(void);
extern uint32_t audio_wear_child_47432c(void);
extern uint32_t audio_wear_child_474100(void);

void audio_uart_case_display_refresh_4abf86(void)
{
    if (audio_log_wake_allowed()==0u)
        return;
    if (audio_uart_case_status()==1u) {
        (void)audio_wear_child_47432c();
    } else if (audio_wear_child_46b0ec()==1u) {
        (void)audio_wear_child_474100();
    }
}
