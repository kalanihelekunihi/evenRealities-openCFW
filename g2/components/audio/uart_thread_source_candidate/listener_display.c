/* SlaveDispalyCommandReplyListener, native 0x45adf4. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_uart_frame_respond(void *,void *); /* native 0x49225a */
extern int32_t audio_uart_slave_display_start(uint32_t,const void *,uint32_t); /* 0x4441ec */
extern int32_t audio_uart_slave_display_refresh(uint32_t,const void *,uint32_t); /* 0x4442d0 */
extern int32_t audio_uart_slave_display_stop(uint32_t,const void *,uint32_t); /* 0x4443cc */
extern int32_t audio_uart_slave_display_control(const void *,uint32_t); /* 0x4444b8 */
static const char module[]="sync.module.framework";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char fn[]="SlaveDispalyCommandReplyListener";
static const char length_text[]="Received display command,length = %d";
static const char length_short[]="[sync.module.framework]Received display command,length = %d";
static const char start_text[]="received display start command,length = %d";
static const char start_short[]="[sync.module.framework]received display start command,length = %d";
static const char refresh_text[]="received display refresh command,length = %d";
static const char refresh_short[]="[sync.module.framework]received display refresh command,length = %d";
static const char stop_text[]="received display stop command,length = %d";
static const char stop_short[]="[sync.module.framework]received display stop command,length = %d";
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
uint32_t audio_uart_listener_slave2(void *tf,const void *message,
                                    uint32_t unused3,uint32_t unused4) {
    (void)unused3;(void)unused4;
    const uint8_t *msg=(const uint8_t *)message;
    const uint8_t *data=*(const uint8_t *const *)(const void *)(msg+8u);
    uint16_t frame=*(const uint16_t *)(const void *)msg;
    uint16_t count=*(const uint16_t *)(const void *)(msg+12u);
    uint16_t command=*(const uint16_t *)(const void *)data;
    uint8_t kind=data[1u];
    log1(4u,0x149u,length_text,length_short,count);
    uint32_t line;
    const char *full,*short_text;
    if(kind==1u) {line=0x14du;full=start_text;short_text=start_short;}
    else if(kind==3u) {line=0x15eu;full=refresh_text;short_text=refresh_short;}
    else if(kind==5u||kind==16u) {
        line=kind==5u?0x16fu:0x181u;
        full=stop_text;short_text=stop_short;
    } else {
        log1(2u,0x193u,unknown_text,unknown_short,command);
        return 1u;
    }
    log1(4u,line,full,short_text,count);
    uint8_t answer=(uint8_t)(kind+1u);
    response_record response;
    uint8_t *zero=(uint8_t *)&response;
    for(uint32_t i=0;i<sizeof(response);++i) zero[i]=0u;
    response.frame=frame;
    response.data=&answer;
    response.length=1u;
    audio_uart_frame_respond(tf,&response);
    const void *payload=data+8u;
    uint16_t payload_size=*(const uint16_t *)(const void *)(data+6u);
    if(kind==1u) audio_uart_slave_display_start(*(const uint16_t *)(const void *)(data+2u),payload,payload_size);
    else if(kind==3u) audio_uart_slave_display_refresh(*(const uint16_t *)(const void *)(data+2u),payload,payload_size);
    else if(kind==5u) audio_uart_slave_display_stop(*(const uint16_t *)(const void *)(data+2u),payload,payload_size);
    else audio_uart_slave_display_control(payload,payload_size);
    return 1u;
}
