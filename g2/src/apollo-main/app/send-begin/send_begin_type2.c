/* _MasterDisplayCmd_Listener, native 0x45e024. */
#include <stdint.h>
typedef void (*uart_timeout_callback)(uint32_t);
typedef void (*uart_timeout_dispatch)(uint32_t,void *,uint32_t,uint32_t);
extern void audio_uart_timeout_dispatch(uint32_t,void *,uint32_t,uint32_t); /* 0x45ade8 */
extern uint32_t audio_uart_timeout_submit(uart_timeout_dispatch,uint32_t,
                                           void *,uint32_t,uint32_t); /* 0x491184 */
extern int32_t audio_uart_slave_display_start(uint32_t,const void *,uint32_t); /* 0x4441ec */
extern int32_t audio_uart_slave_display_refresh(uint32_t,const void *,uint32_t); /* 0x4442d0 */
extern int32_t audio_uart_slave_display_stop(uint32_t,const void *,uint32_t); /* 0x4443cc */
extern int32_t audio_uart_slave_display_control(const void *,uint32_t); /* 0x4444b8 */
extern void audio_file_heap_free(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="sync.module.framework";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char fn[]="_MasterDisplayCmd_Listener";
static const char e_null[]="msg data is null,timeout resource release";
static const char c_null[]="[sync.module.framework]msg data is null,timeout resource release";
static const char e_event[]="SyncEventType = %d";
static const char c_event[]="[sync.module.framework]SyncEventType = %d";
static const char e_userdata[]="userdata is null";
static const char c_userdata[]="[sync.module.framework]userdata is null";
static const char e_start[]="received display start response";
static const char c_start[]="[sync.module.framework]received display start response";
static const char e_refresh[]="received display refresh response";
static const char c_refresh[]="[sync.module.framework]received display refresh response";
static const char e_stop[]="received display stop response";
static const char c_stop[]="[sync.module.framework]received display stop response";
static const char e_exit[]="received display all page exit response";
static const char c_exit[]="[sync.module.framework]received display all page exit response";
static const char e_submit[]="submit work failed,";
static const char c_submit[]="[sync.module.framework]submit work failed,";
static const char e_unknown[]="unknown command,cmd = %d";
static const char c_unknown[]="[sync.module.framework]unknown command,cmd = %d";
static uint32_t word(const void *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+offset);
}
static void log0(uint8_t level,uint32_t line,const char *e,const char *c) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,module,source,fn,line,e);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output((uint32_t)level<<26,c,c);
}
static void log1(uint8_t level,uint32_t line,const char *e,const char *c,
                 uint32_t value) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,module,source,fn,line,e,value);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(((uint32_t)level<<26)|0x400000u,
                                    c,c,value);
}
static void release_node(void *node) {
    audio_file_heap_free((void *)(uintptr_t)word(node,8u));
    audio_file_heap_free(node);
}
/* Stock 0x45E024 (_MasterDisplayCmd_Listener) */
uint32_t audio_uart_send_begin_type2(uint32_t unused,void *message,
                                      uint32_t unused3,uint32_t unused4) {
    (void)unused;(void)unused3;(void)unused4;
    uint32_t data_word=word(message,8u);
    uint32_t node_word=word(message,16u);
    if(data_word==0u) {
        log0(4u,0x55fu,e_null,c_null);
        if(node_word!=0u) {
            void *node=(void *)(uintptr_t)node_word;
            log1(4u,0x562u,e_event,c_event,
                 *(const uint16_t *)(const void *)((const uint8_t *)node+4u));
            release_node(node);
        }
        return 3u;
    }
    const uint8_t *data=(const uint8_t *)(uintptr_t)data_word;
    uint8_t kind=data[0];
    uint32_t line_missing,line_received,line_failed;
    const char *e_received,*c_received;
    if(kind==2u) {
        line_missing=0x56du;line_received=0x574u;line_failed=0x577u;
        e_received=e_start;c_received=c_start;
    } else if(kind==4u) {
        line_missing=0x582u;line_received=0x589u;line_failed=0x58cu;
        e_received=e_refresh;c_received=c_refresh;
    } else if(kind==6u) {
        line_missing=0x597u;line_received=0x59eu;line_failed=0x5a1u;
        e_received=e_stop;c_received=c_stop;
    } else if(kind==17u) {
        line_missing=0x5acu;line_received=0x5b3u;line_failed=0x5b6u;
        e_received=e_exit;c_received=c_exit;
    } else {
        log1(2u,0x5c0u,e_unknown,c_unknown,kind);
        if(node_word!=0u) release_node((void *)(uintptr_t)node_word);
        return 3u;
    }
    if(node_word==0u) {
        log0(2u,line_missing,e_userdata,c_userdata);
        return 3u;
    }
    void *node=(void *)(uintptr_t)node_word;
    const uint8_t *packet=(const uint8_t *)(uintptr_t)word(node,8u);
    uint16_t id=*(const uint16_t *)(const void *)(packet+2u);
    uint16_t size=*(const uint16_t *)(const void *)(packet+6u);
    if(kind==2u) audio_uart_slave_display_start(id,packet+8u,size);
    else if(kind==4u) audio_uart_slave_display_refresh(id,packet+8u,size);
    else if(kind==6u) audio_uart_slave_display_stop(id,packet+8u,size);
    else audio_uart_slave_display_control(packet+8u,size);
    log0(4u,line_received,e_received,c_received);
    uint32_t callback_word=word(message,20u);
    if(callback_word!=0u) {
        uart_timeout_callback callback=(uart_timeout_callback)(uintptr_t)callback_word;
        if(audio_uart_timeout_submit(audio_uart_timeout_dispatch,0u,
                                      (void *)callback,0u,0u)!=0u) {
            log0(1u,line_failed,e_submit,c_submit);
            callback(0u);
        }
    }
    release_node(node);
    return 3u;
}
