/* Native SyncTimeoutDetectionThreadStartup 0x45d34c and timer callback
 * 0x45d302. Timer constructor 0x4493b0 remains a true CMSIS child. */
#include <stdint.h>

extern void *audio_uart_sync_timer_sem; /* *DAT_0045dd38 */
extern void *audio_uart_sync_timer_handle; /* *DAT_0045dd48 */
extern void *audio_uart_sync_timer_event; /* *DAT_0045df14 */
extern void *audio_uart_sync_sem_new(uint32_t,uint32_t,const void *); /* selected 0x44989a */
extern int32_t audio_semaphore_release(void *); /* selected osSemaphoreRelease */
extern uint32_t g2_log_event_set_task(uint32_t,uint32_t); /* selected 0x4495e4 */
extern void *audio_uart_timer_new(void (*)(void *),uint32_t,void *,const void *); /* 0x4493b0 */
extern int32_t audio_timer_start(void *,uint32_t); /* selected 0x449498 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char audio_uart_timer_module[],audio_uart_timer_source[],
                  audio_uart_timer_function[];
extern const char audio_uart_timer_e_sem[],audio_uart_timer_c_sem[];
extern const char audio_uart_timer_e_create[],audio_uart_timer_c_create[];
extern const char audio_uart_timer_e_start[],audio_uart_timer_c_start[];
extern const char audio_uart_timer_e_ok[],audio_uart_timer_c_ok[];

static void log0(uint8_t level,uint32_t line,uint32_t compact,
                 const char *extended,const char *short_text) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,audio_uart_timer_module,audio_uart_timer_source,
                           audio_uart_timer_function,line,extended);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,short_text,short_text);
}

/* Stock 0x45D302 (sync timeout timer callback) */
void audio_uart_sync_timer_callback(void *unused) {
    (void)unused;
    if(audio_uart_sync_timer_sem!=0) {
        (void)audio_semaphore_release(audio_uart_sync_timer_sem);
        (void)g2_log_event_set_task((uint32_t)(uintptr_t)audio_uart_sync_timer_event,
                                    4u);
    }
}

/* Stock 0x45D34C (SyncTimeoutDetectionThreadStartup) */
uint32_t audio_uart_sync_timer_start(void) {
    audio_uart_sync_timer_sem=audio_uart_sync_sem_new(0xffffu,0u,0);
    if(audio_uart_sync_timer_sem==0) {
        log0(1u,0x459u,0x4000000u,audio_uart_timer_e_sem,
             audio_uart_timer_c_sem);
        return UINT32_MAX;
    }
    audio_uart_sync_timer_handle=audio_uart_timer_new(
        audio_uart_sync_timer_callback,1u,0,0);
    if(audio_uart_sync_timer_handle==0) {
        log0(1u,0x45fu,0x4000000u,audio_uart_timer_e_create,
             audio_uart_timer_c_create);
        return UINT32_MAX;
    }
    if(audio_timer_start(audio_uart_sync_timer_handle,100u)!=0) {
        log0(1u,0x465u,0x4000000u,audio_uart_timer_e_start,
             audio_uart_timer_c_start);
        return UINT32_MAX;
    }
    log0(4u,0x468u,0x10000000u,audio_uart_timer_e_ok,
         audio_uart_timer_c_ok);
    return 0u;
}
