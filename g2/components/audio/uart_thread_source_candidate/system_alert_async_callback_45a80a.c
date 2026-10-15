/* Stock Apollo _AsyncStartUPApplicationDataHandlerCb 0x45a80a. */
#include <stdint.h>

extern void audio_uart_task_delay(uint32_t); /* selected 0x454b4c */
extern void audio_uart_master_display_start(uint32_t, const void *, uint16_t,
                                             uint32_t); /* selected 0x464b2e */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* selected 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* selected 0x43ce9e */

static const char module[] = "sync.module.framework";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char function[] = "_AsyncStartUPApplicationDataHandlerCb";
static const char null_message[] = "user data packet is null";
static const char null_compact[] = "[sync.module.framework]user data packet is null";
static const char delay_message[] = "delay_time = %d,restart appid = %d";
static const char delay_compact[] = "[sync.module.framework]delay_time = %d,restart appid = %d";

void audio_system_alert_async_callback_45a80a(uint32_t application,
                                                void *packet,
                                                uint32_t length,
                                                uint32_t unused) {
    (void)unused;
    if(packet == 0) {
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 194u, null_message);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u, null_compact, null_compact);
        return;
    }
    const uint8_t *bytes = packet;
    uint32_t delay = (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8u) |
                     ((uint32_t)bytes[2] << 16u) | ((uint32_t)bytes[3] << 24u);
    audio_uart_task_delay(delay);
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 200u,
                           delay_message, delay, application);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, delay_compact, delay_compact,
                                    delay, application);
    if(length == 4u)
        audio_uart_master_display_start((uint16_t)application, 0, 0u, 0u);
    else
        audio_uart_master_display_start((uint16_t)application, bytes + 4u,
                                         (uint16_t)(length - 4u), 0u);
    audio_file_heap_free(packet);
}
