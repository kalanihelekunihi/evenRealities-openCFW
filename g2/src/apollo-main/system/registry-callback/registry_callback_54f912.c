/* Stock Apollo AUDM_common_data_handler 0x54f912. */
#include <stdint.h>

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_aud_send_message_type8_53cd40(uint8_t); /* 0x53cd40 */

static const char module[] = "service.audio.manager";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_audio_manager.c";
static const char function[] = "AUDM_common_data_handler";
static const char message[] = "invalid audio sync data: raw_data=%p, len=%d";
static const char compact[] = "[service.audio.manager]invalid audio sync data: raw_data=%p, len=%d";

uint32_t audio_uart_registry_callback_54f912(uint32_t unused,
                                               uint32_t payload,
                                               uint32_t length) {
    (void)unused;
    if(payload != 0u && length != 0u) {
        audio_aud_send_message_type8_53cd40(*(const uint8_t *)(uintptr_t)payload);
        return 0u;
    }
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(1u, module, path, function, 0xccu, message,
                           (const void *)(uintptr_t)payload, length);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x04800000u, compact, compact,
                                    (const void *)(uintptr_t)payload, length);
    return UINT32_MAX;
}
