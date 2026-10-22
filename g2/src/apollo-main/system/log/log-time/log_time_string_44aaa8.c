/* Apollo Main 0x44aaa8 outer logger date/tick formatter. Native calls
 * 0x44a19a into a stack date record, 0x4490cc for the tick, and
 * 0x44b728 with capacity 28 and the seven-field format below.
 * The date provider itself remains an explicit imported source gap. */
#include <stdint.h>

extern void g2_log_datetime_now_44a19a(void *record);
extern uint32_t g2_flashdb_candidate_tick(void);
extern int32_t g2_audio_dump_snprintf(char *, uint32_t, const char *, ...);

static char g2_log_time_buffer[28];
static const char g2_log_time_format[] = "%d/%d/%d %02d:%02d:%02d %d";

/* Stock 0x0044AAA8 (elog_port_get_time) */
const char *g2_log_time_string(void)
{
    /* Native reserves 40 bytes at sp+24 for the date provider. Formatter
     * fields are the six words at provider offsets 12..32. */
    int32_t date[10];
    g2_log_datetime_now_44a19a(date);
    uint32_t tick = g2_flashdb_candidate_tick();
    (void)g2_audio_dump_snprintf(g2_log_time_buffer, sizeof(g2_log_time_buffer),
        g2_log_time_format, date[3], date[4], date[5],
        date[6], date[7], date[8], tick);
    return g2_log_time_buffer;
}
