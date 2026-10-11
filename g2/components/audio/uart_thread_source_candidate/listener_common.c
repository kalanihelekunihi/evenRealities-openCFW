/* Native UserDataReplyListener 0x45b588 and PeerDataReplyListener 0x45b6e4.
 * The 24-byte TinyFrame response record is handed to native 0x49225a. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_uart_frame_respond(void *,void *); /* native 0x49225a */
extern uint32_t audio_uart_user_response(uint32_t,const void *,uint32_t,uint32_t);

static const char module[]="sync.module.framework";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char user[]="UserDataReplyListener";
static const char peer[]="PeerDataReplyListener";
static const char length_text[]="Received user data command,length = %d";
static const char length_short[]="[sync.module.framework]Received user data command,length = %d";
static const char user_text[]="received sync data to peer command,app id  = %d";
static const char user_short[]="[sync.module.framework]received sync data to peer command,app id  = %d";
static const char peer_text[]="received sync data to peer command,app id  = %d,data length = %d";
static const char peer_short[]="[sync.module.framework]received sync data to peer command,app id  = %d";
static const char unknown_text[]="unknown command,cmd = %d";
static const char unknown_short[]="[sync.module.framework]unknown command,cmd = %d";

typedef struct {uint16_t frame;uint8_t response;uint8_t reserved3;
                uint32_t reserved4;const void *data;uint16_t length;
                uint8_t unused[10];} response_record;
_Static_assert(sizeof(response_record)==24,"TinyFrame response record");

static void log_one(uint8_t level,const char *fn,uint32_t line,
                    const char *long_text,const char *short_text,uint32_t value) {
    uint32_t flags=audio_log_flags();
    if(flags&2u) audio_log_extended(level,module,source,fn,line,long_text,value);
    flags=audio_log_flags();
    if((flags&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output((uint32_t)level<<26|0x400000u,
                                    short_text,short_text,value);
}

static uint32_t listener(void *tf,const void *message,uint8_t command,
                         uint8_t answer,const char *fn,uint32_t lines) {
    const uint8_t *msg=(const uint8_t *)message;
    const uint8_t *data=*(const uint8_t *const *)(const void *)(msg+8u);
    uint16_t frame=*(const uint16_t *)(const void *)msg;
    uint16_t count=*(const uint16_t *)(const void *)(msg+12u);
    uint16_t tag=*(const uint16_t *)(const void *)data;
    log_one(4u,fn,lines,length_text,length_short,count);
    if((tag>>8u)==command) {
        uint16_t app=*(const uint16_t *)(const void *)(data+2u);
        uint16_t payload_size=*(const uint16_t *)(const void *)(data+6u);
        if(command==9u) log_one(4u,fn,lines+4u,user_text,user_short,app);
        else {
            if(audio_log_flags()&2u)
                audio_log_extended(4u,module,source,fn,lines+4u,
                                   peer_text,app,payload_size);
            if((audio_log_flags()&1u)||(audio_log_flags()&4u))
                (void)compressed_log_output(0x10800000u,peer_short,
                                            peer_short,app,payload_size);
        }
        uint8_t response_byte=answer;
        response_record response;
        uint8_t *zero=(uint8_t *)&response;
        for(uint32_t i=0;i<sizeof(response);++i) zero[i]=0u;
        response.frame=frame;
        response.data=&response_byte;
        response.length=1u;
        audio_uart_frame_respond(tf,&response);
        uint16_t flags=*(const uint16_t *)(const void *)(data+4u);
        (void)audio_uart_user_response(app,data+8u,payload_size,flags);
    } else {
        log_one(2u,fn,lines+0x13u,unknown_text,unknown_short,tag);
    }
    return 1u;
}

uint32_t audio_uart_listener_common1(void *tf,const void *message,
                                      uint32_t unused3,uint32_t unused4) {
    (void)unused3;(void)unused4;
    return listener(tf,message,9u,10u,user,0x20bu);
}
uint32_t audio_uart_listener_common4(void *tf,const void *message,
                                      uint32_t unused3,uint32_t unused4) {
    (void)unused3;(void)unused4;
    return listener(tf,message,12u,13u,peer,0x228u);
}
