/* Stock Main Case in-case input event wrapper, 0x5130a6. */
#include <stdint.h>
extern void audio_input_message_send_record(const void *); /* stock 0x51301c */

void audio_uart_case_in_case_side_effect_5130a6(void)
{
    uint32_t event[3]={3u,0u,0u};
    audio_input_message_send_record(event);
}
