/* Apollo temporary-session response timer bind, native 0x5978ee. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];
extern uint8_t *audio_td_current_record(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.data";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_data.c";
static const char function[]="terminal_data_bind_temp_session_response_timer";
static const char failed[]="temp session bind failed: session=%lu";
static const char failed_short[]="[terminal.data]temp session bind failed: session=%lu";
static const char bound[]="temp session timer bound: session=%lu";
static const char bound_short[]="[terminal.data]temp session timer bound: session=%lu";

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_u32(uint8_t *p,uint32_t value) {
    for(uint32_t i=0;i<4u;++i) p[i]=(uint8_t)(value>>(8u*i));
}

/* Stock 0x5978EE (terminal_data_bind_temp_session_response_timer) */
uint32_t audio_td_bind_temp_session_response_timer(uint32_t session) {
    if(audio_td_state[0xa1dau]==0u ||
       load_u32(audio_td_state+0x956cu)!=UINT32_MAX ||
       session==0u || session==UINT32_MAX) return 0u;
    uint8_t *record=audio_td_current_record(session);
    if(record==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,538u,failed,session);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,failed_short,failed_short,session);
        return 0u;
    }
    put_u32(record+0x88u,load_u32(audio_td_state+0x95f4u));
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,543u,bound,session);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,bound_short,bound_short,session);
    return 1u;
}
