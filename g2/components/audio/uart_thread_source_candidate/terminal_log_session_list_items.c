/* Apollo terminal_log_session_list_items, native 0x5e9b84. */
#include <stdint.h>
extern const char *audio_terminal_session_status_name(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_log_session_list_items";
static const char item[]="session[%lu|%lu](status:%d(%s)):%s";
static const char item_short[]="[terminal.pb]session[%lu|%lu](status:%d(%s)):%s";

static uint16_t load_u16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

void audio_terminal_log_session_list_items(const void *payload) {
    if(payload==0) return;
    const uint8_t *p=payload;
    uint32_t count=load_u16(p+8u);
    if(count>10u) count=10u;
    for(uint32_t i=0u;i<count;++i) {
        const uint8_t *row=p+i*0x88u;
        uint32_t session=load_u32(row+0xcu);
        uint8_t status=row[0x92u];
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,687u,item,
                               i,session,status,
                               audio_terminal_session_status_name(status),row+0x12u);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0d400000u,item_short,item_short,
                                        i,session,status,
                                        audio_terminal_session_status_name(status),row+0x12u);
    }
}
