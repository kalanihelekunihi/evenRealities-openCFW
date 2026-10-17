/* Stock 0x449ed4 and 0x44a100 use 24-hour calendar fields. The already
 * sourced 0x449fda routine shares the calendar decomposition and only applies
 * the optional 12-hour display conversion after that decomposition. */
#include <stdint.h>

extern void audio_time_epoch_to_calendar_449fda(uint32_t seconds, void *record);
extern uint8_t audio_uart_hand_record[0x30u];

void audio_time_epoch_to_calendar_449ed4(uint32_t seconds, void *record)
{
    audio_time_epoch_to_calendar_449fda(seconds, record);
    uint32_t hour = 0u;
    if (seconds >= 946684800u)
        hour = (seconds % 86400u) / 3600u;
    *(uint32_t *)(void *)((uint8_t *)record + 24u) = hour;
}

void audio_time_epoch_to_calendar_44a100(uint32_t seconds, void *record)
{
    audio_time_epoch_to_calendar_449ed4(seconds, record);
}

uint32_t audio_time_format_mode_46650c(void)
{
    return *(const uint32_t *)(const void *)(audio_uart_hand_record + 24u);
}
