/* Apollo terminal_data_dismiss_query_notification, native 0x5974d4. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];
extern uint32_t audio_td_find_record_index(uint32_t,uint32_t *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.data";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_data.c";
static const char function[]="terminal_data_dismiss_query_notification";
static const char dismissed[]="query notification dismissed: session=%lu";
static const char dismissed_short[]="[terminal.data]query notification dismissed: session=%lu";

void audio_td_dismiss_query_notification(uint32_t session) {
    uint32_t index=0u;
    if(audio_td_find_record_index(session,&index)==0u) return;
    audio_td_state[0x9688u+index*0x90u]=1u;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,320u,dismissed,session);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,dismissed_short,dismissed_short,session);
}
