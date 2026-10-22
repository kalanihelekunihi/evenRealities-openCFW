/* Native SyncScheduleManagerInit 0x45d1ec. Queue and thread attributes
 * are product ROM records, retained as typed contracts. */
#include <stdint.h>

extern void *audio_uart_master_schedule_queue; /* *DAT_0045da98 */
extern const void *audio_uart_master_queue_attrs; /* DAT_0045da9c */
extern const uint8_t audio_uart_master_thread_attrs[36]; /* PTR_DAT_0045dc70 */
extern void audio_uart_master_scheduler_thread(void *); /* 0x45c058 */
extern void *audio_queue_new(uint32_t,uint32_t,const void *); /* selected 0x449a32 */
extern void *audio_thread_new(void (*)(void *),void *,const void *); /* selected 0x4490e2 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439c04 equivalent */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char audio_uart_master_module[],audio_uart_master_source[],
                  audio_uart_master_function[];
extern const char audio_uart_master_e_queue[],audio_uart_master_c_queue[];
extern const char audio_uart_master_e_thread[],audio_uart_master_c_thread[];
extern const char audio_uart_master_e_ready[],audio_uart_master_c_ready[];

static void log0(uint8_t level,uint32_t line,uint32_t compact,
                 const char *extended,const char *short_text) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,audio_uart_master_module,
                           audio_uart_master_source,audio_uart_master_function,
                           line,extended);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,short_text,short_text);
}

/* Stock 0x45D1EC (SyncScheduleManagerInit) */
uint32_t audio_uart_master_prepare(void) {
    audio_uart_master_schedule_queue=audio_queue_new(0x96u,4u,
                                                     audio_uart_master_queue_attrs);
    if(audio_uart_master_schedule_queue==0) {
        log0(1u,0x432u,0x4000000u,audio_uart_master_e_queue,
             audio_uart_master_c_queue);
        return UINT32_MAX;
    }
    uint32_t attrs[9];
    (void)audio_queue_copy_bytes(attrs,audio_uart_master_thread_attrs,36u);
    if(audio_thread_new(audio_uart_master_scheduler_thread,0,attrs)==0) {
        log0(1u,0x440u,0x4000000u,audio_uart_master_e_thread,
             audio_uart_master_c_thread);
        return UINT32_MAX;
    }
    log0(4u,0x444u,0x10000000u,audio_uart_master_e_ready,
         audio_uart_master_c_ready);
    return 0u;
}
