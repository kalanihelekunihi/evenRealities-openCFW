/* Five native timeout-listener bodies: 0x45d710, 0x45d9cc,
 * 0x45dc84, 0x45df24, and 0x45e5a4. All enqueue the received
 * callback with status -2, then invoke it directly if enqueue fails. */
#include <stdint.h>

typedef void (*uart_timeout_callback)(uint32_t status);
typedef void (*uart_timeout_dispatch)(uint32_t,void *,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_uart_timeout_submit(uart_timeout_dispatch,uint32_t,
                                           void *,uint32_t,
                                           uint32_t); /* 0x491184 */
extern const char audio_uart_timeout_module[],audio_uart_timeout_source[];
extern const char audio_uart_timeout_module_peer[],audio_uart_timeout_source_peer[];
extern const char audio_uart_timeout_module_display[],audio_uart_timeout_source_display[];
extern const char audio_uart_timeout_name_peer[],audio_uart_timeout_name_user[];
extern const char audio_uart_timeout_name_slave[],audio_uart_timeout_name_input[];
extern const char audio_uart_timeout_name_display[];
extern const char audio_uart_timeout_running_text[],audio_uart_timeout_compact[];
extern const char audio_uart_timeout_compact_peer[],audio_uart_timeout_compact_display[];
extern const char audio_uart_timeout_submit_failed[],audio_uart_timeout_submit_compact[];
extern const char audio_uart_timeout_submit_compact_peer[];

/* Native scheduler callback 0x45ade8. Its only defined effect is the
 * callback invocation; decompilation does not establish a return value. */
void audio_uart_timeout_dispatch(uint32_t ignored,void *opaque,
                                  uint32_t status,uint32_t unused) {
    (void)ignored;
    (void)unused;
    uart_timeout_callback callback=(uart_timeout_callback)opaque;
    if(callback!=0) callback(status);
}

static uint32_t timeout_end(const char *module,const char *source,
                            const char *name,const char *compact,
                            const char *submit_compact,uint32_t level,
                            uint32_t line,uart_timeout_callback callback) {
    if(audio_log_flags()&2u)
        audio_log_extended((uint8_t)level,module,source,name,line,
                           audio_uart_timeout_running_text,name);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(level==3u?0xc400000u:0x10400000u,
                                    compact,compact,name);
    if(callback!=0) {
        uint32_t result=audio_uart_timeout_submit(audio_uart_timeout_dispatch,
                                                   0u,(void *)callback,
                                                   UINT32_MAX-1u,0u);
        if(result!=0u) {
            if(audio_log_flags()&2u)
                audio_log_extended(1u,module,source,name,line+3u,
                                   audio_uart_timeout_submit_failed);
            if((audio_log_flags()&1u)||(audio_log_flags()&4u))
                (void)compressed_log_output(0x4000000u,submit_compact,
                                            submit_compact);
            callback(UINT32_MAX-1u);
        }
    }
    return 3u;
}

uint32_t audio_uart_send_end4(uint32_t unused,uart_timeout_callback callback,
                               void *unused2,void *unused3) {
    (void)unused;(void)unused2;(void)unused3;
    return timeout_end(audio_uart_timeout_module_peer,
                       audio_uart_timeout_source_peer,
                       audio_uart_timeout_name_peer,
                       audio_uart_timeout_compact_peer,
                       audio_uart_timeout_submit_compact_peer,
                       4u,0x4acu,callback);
}
uint32_t audio_uart_send_end_type1(uint32_t unused,uart_timeout_callback callback,
                                    void *unused2,void *unused3) {
    (void)unused;(void)unused2;(void)unused3;
    return timeout_end(audio_uart_timeout_module,audio_uart_timeout_source,
                       audio_uart_timeout_name_user,audio_uart_timeout_compact,
                       audio_uart_timeout_submit_compact,4u,0x4e5u,callback);
}
uint32_t audio_uart_send_end0(uint32_t unused,uart_timeout_callback callback,
                               void *unused2,void *unused3) {
    (void)unused;(void)unused2;(void)unused3;
    return timeout_end(audio_uart_timeout_module,audio_uart_timeout_source,
                       audio_uart_timeout_name_slave,audio_uart_timeout_compact,
                       audio_uart_timeout_submit_compact,4u,0x519u,callback);
}
uint32_t audio_uart_send_end3(uint32_t unused,uart_timeout_callback callback,
                               void *unused2,void *unused3) {
    (void)unused;(void)unused2;(void)unused3;
    return timeout_end(audio_uart_timeout_module,audio_uart_timeout_source,
                       audio_uart_timeout_name_input,audio_uart_timeout_compact,
                       audio_uart_timeout_submit_compact,4u,0x551u,callback);
}
uint32_t audio_uart_send_end_type2(uint32_t unused,uart_timeout_callback callback,
                                    void *unused2,void *unused3) {
    (void)unused;(void)unused2;(void)unused3;
    return timeout_end(audio_uart_timeout_module_display,
                       audio_uart_timeout_source_display,
                       audio_uart_timeout_name_display,
                       audio_uart_timeout_compact_display,
                       audio_uart_timeout_submit_compact,3u,0x5d3u,callback);
}
