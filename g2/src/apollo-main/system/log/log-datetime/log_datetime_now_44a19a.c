/* Apollo Main 0x44a19a: snapshot -> epoch seconds -> signed quarter-hour
 * timezone adjustment -> calendar record. audio_log_context already owns
 * the selected C snapshot/epoch/timezone path from native 0x44a1c6.
 * The seconds-to-calendar child at 0x449fda remains a source gap. */
#include <stdint.h>

extern uint32_t audio_log_context(void);
extern void audio_time_epoch_to_calendar_449fda(uint32_t seconds, void *record);

void g2_log_datetime_now_44a19a(void *record)
{
    audio_time_epoch_to_calendar_449fda(audio_log_context(), record);
}
