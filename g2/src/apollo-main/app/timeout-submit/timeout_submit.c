/* Native timer/work item submit 0x491184. Queue item is 20 bytes;
 * native acquisition/enqueue failures assert and halt after logging. */
#include <stdint.h>

typedef void (*uart_timeout_dispatch)(uint32_t,void *,uint32_t,uint32_t);
extern volatile uint8_t audio_uart_timeout_running_state; /* *DAT_00491630 */
extern void *audio_uart_timeout_queue; /* *DAT_00491618 */
extern void *audio_uart_timeout_mutex; /* *DAT_00491650 */
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* selected 0x4497b6 */
extern int32_t audio_file_mutex_release(void *); /* selected 0x44981c */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* selected 0x449abe */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void audio_delay_scheduler_assert(void); /* authentic 0x5fa0a4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char audio_uart_work_module[],audio_uart_work_source[],
                  audio_uart_work_function[];
extern const char audio_uart_work_e_unready[],audio_uart_work_c_unready[];
extern const char audio_uart_work_e_null[],audio_uart_work_c_null[];
extern const char audio_uart_work_e_submit[],audio_uart_work_c_submit[];
extern const char audio_uart_work_e_lock[],audio_uart_work_c_lock[];
extern const char audio_uart_work_e_queue[],audio_uart_work_c_queue[];

static void log0(uint8_t level,uint32_t line,uint32_t compact,
                 const char *extended,const char *short_text) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,audio_uart_work_module,
                           audio_uart_work_source,audio_uart_work_function,
                           line,extended);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,short_text,short_text);
}
static void log1(uint8_t level,uint32_t line,uint32_t compact,
                 const char *extended,const char *short_text,uint32_t word) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,audio_uart_work_module,
                           audio_uart_work_source,audio_uart_work_function,
                           line,extended,word);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,short_text,short_text,word);
}

uint32_t audio_uart_timeout_submit(uart_timeout_dispatch dispatch,
                                    uint32_t target,
                                    void *payload,
                                    uint32_t argument,uint32_t flags) {
    if(audio_uart_timeout_running_state==0u || audio_uart_timeout_queue==0) {
        log0(1u,0x45u,0x4000000u,audio_uart_work_e_unready,
             audio_uart_work_c_unready);
        return UINT32_MAX;
    }
    if(dispatch==0) {
        log0(1u,0x4bu,0x4000000u,audio_uart_work_e_null,
             audio_uart_work_c_null);
        return UINT32_MAX;
    }
    uint32_t item[5];
    audio_uart_buffer_zero(item,20u,0u);
    item[0]=(uint32_t)(uintptr_t)dispatch;
    item[1]=target;
    *(uint16_t *)(void *)((uint8_t *)item+8u)=(uint16_t)flags;
    item[3]=(uint32_t)(uintptr_t)payload;
    item[4]=argument;
    log1(4u,0x57u,0x10400000u,audio_uart_work_e_submit,
         audio_uart_work_c_submit,target);
    if(audio_file_mutex_acquire(audio_uart_timeout_mutex,3000u)!=0) {
        log0(1u,0x67u,0x4000000u,audio_uart_work_e_lock,
             audio_uart_work_c_lock);
        audio_delay_scheduler_assert();
        for(;;) __asm volatile("nop");
    }
    int32_t status=audio_cmsis_queue_put(audio_uart_timeout_queue,item,0u,3000u);
    (void)audio_file_mutex_release(audio_uart_timeout_mutex);
    if(status!=0) {
        log1(1u,0x5fu,0x4400000u,audio_uart_work_e_queue,
             audio_uart_work_c_queue,(uint32_t)status);
        audio_delay_scheduler_assert();
        for(;;) __asm volatile("nop");
    }
    return 0u;
}
