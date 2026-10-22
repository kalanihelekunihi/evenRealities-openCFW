/* MasterScheduleModuleDataReplyListener, native 0x45b14c. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_uart_frame_respond(void *,void *); /* 0x49225a */
extern void audio_uart_master_display_start(uint32_t,const void *,uint16_t,uint32_t); /* 0x464b2e */
extern void audio_uart_master_display_refresh(uint32_t,const void *,uint16_t,uint32_t); /* 0x464bb2 */
extern void audio_uart_master_display_stop(uint32_t,const void *,uint16_t,uint32_t); /* 0x464c36 */
extern void audio_uart_master_input_event(uint32_t,uint32_t,uint32_t,uint32_t); /* 0x465748 */
extern void audio_uart_master_control(uint32_t); /* 0x464cba */
static const char module[]="sync.module.framework";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char fn[]="MasterScheduleModuleDataReplyListener";
static const char e_length[]="Received slave send sync  data,length = %d";
static const char c_length[]="[sync.module.framework]Received slave send sync  data,length = %d";
static const char e_byte[]="data[%d] = %d";
static const char c_byte[]="[sync.module.framework]data[%d] = %d";
static const char e_display[]="received slave send display start command,app id  = %d";
static const char c_display[]="[sync.module.framework]received slave send display start command,app id  = %d";
static const char e_input[]="received slave send input event command,input dev type  = %d";
static const char c_input[]="[sync.module.framework]received slave send input event command,input dev type  = %d";
static const char e_unknown[]="unknown command,cmd = %d";
static const char c_unknown[]="[sync.module.framework]unknown command,cmd = %d";
typedef struct {uint16_t frame;uint8_t response;uint8_t reserved3;
                uint32_t reserved4;const void *data;uint16_t length;
                uint8_t unused[10];} response_record;
_Static_assert(sizeof(response_record)==24,"TinyFrame response record");
static void log1(uint8_t level,uint32_t line,const char *e,const char *c,uint32_t n) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,module,source,fn,line,e,n);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(((uint32_t)level<<26)|0x400000u,c,c,n);
}
static void log2(uint32_t line,uint32_t i,uint32_t value) {
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source,fn,line,e_byte,i,value);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10800000u,c_byte,c_byte,i,value);
}
/* Stock 0x45B14C (MasterScheduleModuleDataReplyListener) */
uint32_t audio_uart_listener_master0(void *tf,const void *message,
                                      uint32_t unused3,uint32_t unused4) {
    (void)unused3;(void)unused4;
    const uint8_t *msg=(const uint8_t *)message;
    const uint8_t *data=*(const uint8_t *const *)(const void *)(msg+8u);
    uint16_t frame=*(const uint16_t *)(const void *)msg;
    uint16_t count=*(const uint16_t *)(const void *)(msg+12u);
    uint8_t kind=data[1u];
    log1(4u,0x19fu,e_length,c_length,count);
    for(uint32_t i=0u;i<count;++i) log2(0x1a1u,i,data[i]);
    uint16_t id=*(const uint16_t *)(const void *)(data+2u);
    const void *payload=data+8u;
    uint16_t size=*(const uint16_t *)(const void *)(data+6u);
    uint32_t line;
    if(kind==1u) {
        audio_uart_master_display_start(id,payload,size,0u);line=0x1dcu;
    } else if(kind==3u) {
        audio_uart_master_display_refresh(id,payload,size,0u);line=0x1a9u;
    } else if(kind==5u) {
        audio_uart_master_display_stop(id,payload,size,0u);line=0x1bau;
    } else if(kind==7u) {
        uint32_t event=*(const uint32_t *)(const void *)(data+4u);
        uint32_t value=*(const uint32_t *)(const void *)(data+8u);
        audio_uart_master_input_event(id,event,value,0u);
        line=0x1f0u;
    } else if(kind==16u) {
        audio_uart_master_control(0u);line=0x1cbu;
    } else {
        log1(2u,0x1ffu,e_unknown,c_unknown,
             *(const uint16_t *)(const void *)data);
        return 1u;
    }
    log1(4u,line,kind==7u?e_input:e_display,
         kind==7u?c_input:c_display,id);
    uint8_t ack=11u;
    response_record response;
    uint8_t *zero=(uint8_t *)&response;
    for(uint32_t i=0u;i<sizeof(response);++i) zero[i]=0u;
    response.frame=frame;
    response.data=&ack;
    response.length=1u;
    audio_uart_frame_respond(tf,&response);
    return 1u;
}
