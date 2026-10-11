/* SlaveInputEventReplyListener, native 0x45b850. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_uart_frame_respond(void *,void *); /* native 0x49225a */
extern uint32_t audio_uart_input_event(uint32_t,uint32_t,uint32_t); /* 0x4445a4 */
static const char module[]="sync.module.framework";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char fn[]="SlaveInputEventReplyListener";
static const char length_text[]="Received input event command,length = %d";
static const char length_short[]="[sync.module.framework]Received input event command,length = %d";
static const char type_text[]="received input event command,input dev type  = %d";
static const char type_short[]="[sync.module.framework]received input event command,input dev type  = %d";
static const char id_text[]="received input event command,input event id  = %d";
static const char id_short[]="[sync.module.framework]received input event command,input event id  = %d";
static const char value_text[]="received input event command,input event value  = %d";
static const char value_short[]="[sync.module.framework]received input event command,input event value  = %d";
static const char unknown_text[]="unknown command,cmd = %d";
static const char unknown_short[]="[sync.module.framework]unknown command,cmd = %d";
typedef struct {uint16_t frame;uint8_t response;uint8_t reserved3;
                uint32_t reserved4;const void *data;uint16_t length;
                uint8_t unused[10];} response_record;
_Static_assert(sizeof(response_record)==24,"TinyFrame response record");
static void log1(uint8_t level,uint32_t line,const char *full,
                 const char *short_text,uint32_t word) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,module,source,fn,line,full,word);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(((uint32_t)level<<26)|0x400000u,
                                    short_text,short_text,word);
}
uint32_t audio_uart_listener_slave3(void *tf,const void *message,
                                    uint32_t unused3,uint32_t unused4) {
    (void)unused3;(void)unused4;
    const uint8_t *msg=(const uint8_t *)message;
    const uint8_t *data=*(const uint8_t *const *)(const void *)(msg+8u);
    uint16_t frame=*(const uint16_t *)(const void *)msg;
    uint16_t count=*(const uint16_t *)(const void *)(msg+12u);
    uint16_t command=*(const uint16_t *)(const void *)data;
    log1(4u,0x245u,length_text,length_short,count);
    if((command>>8u)==7u) {
        uint16_t device=*(const uint16_t *)(const void *)(data+2u);
        uint32_t event=*(const uint32_t *)(const void *)(data+4u);
        uint32_t value=*(const uint32_t *)(const void *)(data+8u);
        log1(4u,0x24bu,type_text,type_short,device);
        log1(4u,0x24cu,id_text,id_short,event);
        log1(4u,0x24du,value_text,value_short,value);
        uint8_t answer=8u;
        response_record response;
        uint8_t *bytes=(uint8_t *)&response;
        for(uint32_t i=0;i<sizeof(response);++i) bytes[i]=0u;
        response.frame=frame;
        response.data=&answer;
        response.length=1u;
        audio_uart_frame_respond(tf,&response);
        (void)audio_uart_input_event(device,event,value);
    } else {
        log1(2u,0x259u,unknown_text,unknown_short,command);
    }
    return 1u;
}
