/* EasyLogger async transport signal, native 0x448f98..0x448fab (literal 0x448fd8).
 * Sibling of audio_log_transport_wake (0x448f7c, flag 2) in
 * system/log/audio-log/audio-log-format/wake.c; this one posts flag 8 and is
 * the fallback taken by 0x47dd62 when log wake-up is not allowed. */
#include <stdint.h>

#define LOG_TRANSPORT_FLAG_FLUSH 8u

extern uint32_t g2_audio_log_event_handle; /* RAM 0x20074570, osEventFlagsId_t */
extern uint32_t osEventFlagsSet(void *ef_id, uint32_t flags); /* 0x4495e4 */

void audio_log_transport_flush_448f98(void)
{
    if (g2_audio_log_event_handle != 0u)
        (void)osEventFlagsSet((void *)(uintptr_t)g2_audio_log_event_handle, LOG_TRANSPORT_FLAG_FLUSH);
}
