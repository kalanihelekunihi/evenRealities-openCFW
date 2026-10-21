/* Native SlaveScheduleModuleDataCmd listener 0x45daa0.
 * Message offsets +8/+16/+20 are the authenticated callback ABI. */
#include <stdint.h>

typedef void (*uart_timeout_callback)(uint32_t);
typedef void (*uart_timeout_dispatch)(uint32_t,void *,uint32_t,uint32_t);
extern void audio_uart_timeout_dispatch(uint32_t,void *,uint32_t,uint32_t); /* 0x45ade8 */
extern uint32_t audio_uart_timeout_submit(uart_timeout_dispatch,uint32_t,
                                           void *,uint32_t,
                                           uint32_t); /* selected 0x491184 */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char audio_uart_begin0_module[],audio_uart_begin0_source[],
                  audio_uart_begin0_function[];
extern const char audio_uart_begin_e_null[],audio_uart_begin_c_null[];
extern const char audio_uart_begin_e_event[],audio_uart_begin_c_event[];
extern const char audio_uart_begin_e_userdata[],audio_uart_begin_c_userdata[];
extern const char audio_uart_begin_e_submit[],audio_uart_begin_c_submit[];
extern const char audio_uart_begin0_e_received[],audio_uart_begin0_c_received[];

static uint32_t word(const void *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+offset);
}
static void log0(uint8_t level,uint32_t line,uint32_t compact,
                 const char *extended,const char *short_text) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,audio_uart_begin0_module,
                           audio_uart_begin0_source,audio_uart_begin0_function,
                           line,extended);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,short_text,short_text);
}
static void log_event(uint32_t line,uint32_t event) {
    if(audio_log_flags()&2u)
        audio_log_extended(4u,audio_uart_begin0_module,
                           audio_uart_begin0_source,audio_uart_begin0_function,
                           line,audio_uart_begin_e_event,event);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,audio_uart_begin_c_event,
                                    audio_uart_begin_c_event,event);
}

uint32_t audio_uart_send_begin0(uint32_t unused,void *message,
                                 uint32_t unused2,uint32_t unused3) {
    (void)unused;(void)unused2;(void)unused3;
    uint32_t data_word=word(message,8u);
    if(data_word==0u) {
        log0(4u,0x4f3u,0x10000000u,audio_uart_begin_e_null,
             audio_uart_begin_c_null);
        uint32_t node_word=word(message,16u);
        if(node_word!=0u) {
            void *node=(void *)(uintptr_t)node_word;
            log_event(0x4f6u,*(uint16_t *)(void *)((uint8_t *)node+4u));
            audio_file_heap_free((void *)(uintptr_t)word(node,8u));
            audio_file_heap_free(node);
        }
        return 3u;
    }
    if(*(const uint8_t *)(uintptr_t)data_word!=0x0bu) return 3u;
    uint32_t node_word=word(message,16u);
    if(node_word==0u) {
        log0(2u,0x501u,0x8000000u,audio_uart_begin_e_userdata,
             audio_uart_begin_c_userdata);
        return 3u;
    }
    uint32_t callback_word=word(message,20u);
    if(callback_word!=0u) {
        uart_timeout_callback callback=(uart_timeout_callback)(uintptr_t)callback_word;
        if(audio_uart_timeout_submit(audio_uart_timeout_dispatch,0u,(void *)callback,
                                      0u,0u)!=0u) {
            log0(1u,0x507u,0x4000000u,audio_uart_begin_e_submit,
                 audio_uart_begin_c_submit);
            callback(0u);
        }
    }
    log0(4u,0x50bu,0x10000000u,audio_uart_begin0_e_received,
         audio_uart_begin0_c_received);
    void *node=(void *)(uintptr_t)node_word;
    audio_file_heap_free((void *)(uintptr_t)word(node,8u));
    audio_file_heap_free(node);
    return 3u;
}
