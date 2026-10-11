/* Native user-response enqueue 0x45a72c, worker 0x45a6d0, and
 * registered-listener dispatch 0x442524. Queue payload ownership is
 * transferred on success and released on failure or after dispatch. */
#include <stdint.h>

typedef void (*uart_timeout_dispatch)(uint32_t,void *,uint32_t,uint32_t);
typedef void (*uart_user_listener)(uint16_t);
extern void *codec_allocate(uint32_t); /* selected 0x474cd2 */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern uint32_t audio_uart_timeout_submit(uart_timeout_dispatch,uint32_t,
                                           void *,uint32_t,uint32_t); /* 0x491184 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern volatile uint32_t audio_uart_user_registry_count; /* *DAT_00442cd4 */
extern uint8_t audio_uart_user_registry_rows[]; /* RAM0x20066230, DAT_00442cd8 */
extern const char audio_uart_user_module[],audio_uart_user_source[],
                  audio_uart_user_function[];
extern const char audio_uart_user_e_alloc[],audio_uart_user_c_alloc[];
extern const char audio_uart_user_e_enqueue[],audio_uart_user_c_enqueue[];
extern const char audio_uart_user_e_null[],audio_uart_user_c_null[];
extern const char audio_uart_user_e_missing[],audio_uart_user_c_missing[];

static void log0(uint8_t level,uint32_t line,uint32_t compact,
                 const char *extended,const char *short_text) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,audio_uart_user_module,audio_uart_user_source,
                           audio_uart_user_function,line,extended);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,short_text,short_text);
}
static void log1(uint8_t level,uint32_t line,uint32_t compact,
                 const char *extended,const char *short_text,uint32_t word) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,audio_uart_user_module,audio_uart_user_source,
                           audio_uart_user_function,line,extended,word);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,short_text,short_text,word);
}

void audio_uart_user_broadcast(uint32_t id,const void *payload,
                                uint32_t length,uint32_t flags) {
    (void)payload;(void)length;
    for(uint32_t i=0;i<audio_uart_user_registry_count;i++) {
        const uint8_t *row=audio_uart_user_registry_rows+i*16u;
        if(*(const uint32_t *)(const void *)row==id) {
            uint32_t callback_word=*(const uint32_t *)(const void *)(row+4u);
            if(callback_word!=0u) {
                ((uart_user_listener)(uintptr_t)callback_word)((uint16_t)flags);
                return;
            }
        }
    }
    log1(2u,0x97u,0x8400000u,audio_uart_user_e_missing,
         audio_uart_user_c_missing,id);
}

void audio_uart_user_dispatch(uint32_t id,void *payload,uint32_t length,
                               uint32_t flags) {
    if(payload==0) {
        log0(2u,0xa7u,0x8000000u,audio_uart_user_e_null,
             audio_uart_user_c_null);
        return;
    }
    audio_uart_user_broadcast(id,payload,length,flags&0xffffu);
    audio_file_heap_free(payload);
}

uint32_t audio_uart_user_response(uint32_t id,const void *bytes,
                                   uint32_t length,uint32_t flags) {
    void *owned=codec_allocate(length);
    if(owned==0) {
        log1(2u,0xb1u,0x8400000u,audio_uart_user_e_alloc,
             audio_uart_user_c_alloc,length);
        return UINT32_MAX;
    }
    (void)audio_queue_copy_bytes(owned,bytes,length);
    if(audio_uart_timeout_submit(audio_uart_user_dispatch,id,owned,length,
                                  flags&0xffffu)==0u)
        return 0u;
    log0(2u,0xb7u,0x8000000u,audio_uart_user_e_enqueue,
         audio_uart_user_c_enqueue);
    audio_file_heap_free(owned);
    return UINT32_MAX;
}
