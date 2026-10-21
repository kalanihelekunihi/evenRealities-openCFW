/* Stock 0x44a1c6..0x44a1e9: packet local-time context. */
#include <stdint.h>
extern void audio_time_snapshot(uint8_t out[40]); /* stock 0x47ef10 */
extern uint32_t audio_time_epoch_seconds(const uint8_t in[40]); /* 0x44a108 */
extern const uint8_t *g2_audio_log_timezone; /* pointer cell 0x200036fc */
uint32_t audio_log_context(void)
{
    uint8_t snapshot[40];
    audio_time_snapshot(snapshot);
    uint32_t seconds=audio_time_epoch_seconds(snapshot);
    int32_t zone=(int8_t)g2_audio_log_timezone[8];
    return seconds+(uint32_t)(zone*900);
}
