/* Stock Apollo AsyncRequestDisplayStartUp submitter 0x45a8ee. */
#include <stdint.h>

typedef void (*audio_async_callback)(uint32_t, void *, uint32_t, uint32_t);
extern void audio_system_alert_async_callback_45a80a(uint32_t, void *, uint32_t, uint32_t);
extern void *codec_allocate(uint32_t); /* 0x474cd2 */
extern void audio_file_heap_free(void *); /* 0x474d16 */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* 0x439be4 */
extern uint32_t audio_uart_timeout_submit(audio_async_callback, uint32_t,
                                           void *, uint32_t, uint32_t); /* 0x491184 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module[] = "sync.module.framework";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char function[] = "AsyncRequestDisplayStartUp";
static const char alloc_error[] = "malloc %d bytes user data packet failed";
static const char alloc_compact[] = "[sync.module.framework]malloc %d bytes user data packet failed";
static const char submit_error[] = "submit work failed";
static const char submit_compact[] = "[sync.module.framework]submit work failed";

uint32_t audio_system_alert_command_45a8ee(uint32_t target, uint32_t payload,
                                             uint32_t length, uint32_t value) {
    uint8_t *packet = codec_allocate(length + 4u);
    if(packet == 0) {
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 212u, alloc_error, length);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, alloc_compact, alloc_compact, length);
        return UINT32_MAX;
    }
    for(uint32_t i = 0; i < 4u; ++i) packet[i] = (uint8_t)(value >> (8u * i));
    (void)audio_queue_copy_bytes(packet + 4u, (const void *)(uintptr_t)payload, length);
    if(audio_uart_timeout_submit(audio_system_alert_async_callback_45a80a,
                                  target, packet, length + 4u, 0u) != 0u) {
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 222u, submit_error);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u, submit_compact, submit_compact);
        audio_file_heap_free(packet);
        return UINT32_MAX;
    }
    return 0u;
}
