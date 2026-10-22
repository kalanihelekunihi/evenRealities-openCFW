/* EasyLogger async back end (G2 downstream glue), stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\EasyLogger-master\easylogger\src\elog_async_api.c
 * Native elog_async_handler_thread_handler 0x448e8e..0x448f3c (pool
 * 0x448f40..0x44900b, shared with the rest of the TU). The thread is started
 * by elog_async_thread_init_448f44 (elog_async_api_init.c) and waits on the
 * event flags at RAM 0x20074570:
 *   bit 0  drain the async log queue (0x448dd2)
 *   bit 1  sync the compressed log to files (0x43cf02)
 *   bit 3  re-arm the tracepoint defer timer (0x47ddac)
 *   bit 2  KV_WRITE_EVENT_FLAG: persist the pending settings to flash/KV.
 * Flags are waited with osFlagsNoClear and cleared after each handler. */
#include <stdint.h>

extern uint32_t g2_audio_log_event_handle; /* RAM 0x20074570 osEventFlagsId_t */

extern uint32_t osEventFlagsWait(void *ef, uint32_t flags, uint32_t options, uint32_t timeout); /* 0x44969c */
extern uint32_t osEventFlagsClear(void *ef, uint32_t flags);                                   /* 0x449642 */
extern int32_t g2_log_transport_queue_failure(const char *fmt, ...); /* 0x4733ee raw printf */
extern uint32_t audio_log_flags(void);                               /* 0x43d0ce */
extern void elog_output(uint8_t level, const char *tag, const char *file, const char *func,
                        const long line, const char *format, ...);  /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *message,
                                    const char *message_copy, ...);  /* 0x43ce9e */

extern uint32_t elog_async_drain_448dd2(void);
extern void svc_compress_log_sync_to_files(void);                    /* 0x43cf02 */
extern void tracepoint_defer_rearm_47ddac(void);
extern void system_language_save_to_flash_471554(void);
extern void dashboard_auto_close_value_save_to_flash_471608(void);
extern void OnboardingFlagSaveToFlash(void);                         /* 0x47e3e6 */
extern uint32_t SVC_Settings_SaveSettingConfigToKV(void);            /* 0x46bef8 */
extern uint32_t SVC_Settings_SaveAlsScaleToKV(void);                 /* 0x46bf74 */
extern uint32_t svc_universal_setting_save_to_kv_46607c(void);
extern void menu_configure_value_save_to_flash_460580(void);

#define ELOG_EVENT_DRAIN 0x01u
#define ELOG_EVENT_COMPRESS_SYNC 0x02u
#define ELOG_EVENT_KV_WRITE 0x04u
#define ELOG_EVENT_TRACEPOINT 0x08u
#define ELOG_EVENT_ALL 0x0fu
#define OS_FLAGS_NO_CLEAR 0x02u
#define OS_WAIT_FOREVER 0xffffffffu

static const char module_tag[] = "elog.async"; /* ROM 0x78a994 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\EasyLogger-master\\easylogger\\src\\elog_async_api.c"; /* ROM 0x6da73c */
static const char thread_fn[] = "elog_async_handler_thread_handler"; /* ROM 0x7542cc */
static const char thread_start[] = "elog_async_handler_thread_handler start\n"; /* ROM 0x73ea54 */
static const char kv_write[] = "KV_WRITE_EVENT_FLAG"; /* ROM 0x77f2fc */
static const char kv_write_short[] = "[elog.async]KV_WRITE_EVENT_FLAG"; /* ROM 0x75fd70 */

void elog_async_handler_thread_448e8e(void *argument)
{
    (void)argument;
    (void)g2_log_transport_queue_failure(thread_start);
    for (;;) {
        void *const ef = (void *)(uintptr_t)g2_audio_log_event_handle;
        uint32_t flags = osEventFlagsWait(ef, ELOG_EVENT_ALL, OS_FLAGS_NO_CLEAR, OS_WAIT_FOREVER);

        if (flags & ELOG_EVENT_DRAIN) {
            (void)elog_async_drain_448dd2();
            (void)osEventFlagsClear((void *)(uintptr_t)g2_audio_log_event_handle, ELOG_EVENT_DRAIN);
        }
        if (flags & ELOG_EVENT_COMPRESS_SYNC) {
            svc_compress_log_sync_to_files();
            (void)osEventFlagsClear((void *)(uintptr_t)g2_audio_log_event_handle, ELOG_EVENT_COMPRESS_SYNC);
        }
        if (flags & ELOG_EVENT_TRACEPOINT) {
            tracepoint_defer_rearm_47ddac();
            (void)osEventFlagsClear((void *)(uintptr_t)g2_audio_log_event_handle, ELOG_EVENT_TRACEPOINT);
        }
        if (flags & ELOG_EVENT_KV_WRITE) {
            if (audio_log_flags() & 2u)
                elog_output(3u, module_tag, source_file, thread_fn, 0x410, kv_write);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compress_log_output(0x0c000000u, kv_write_short, kv_write_short);
            system_language_save_to_flash_471554();
            dashboard_auto_close_value_save_to_flash_471608();
            OnboardingFlagSaveToFlash();
            (void)SVC_Settings_SaveSettingConfigToKV();
            (void)SVC_Settings_SaveAlsScaleToKV();
            (void)svc_universal_setting_save_to_kv_46607c();
            menu_configure_value_save_to_flash_460580();
            (void)osEventFlagsClear((void *)(uintptr_t)g2_audio_log_event_handle, ELOG_EVENT_KV_WRITE);
        }
    }
}
