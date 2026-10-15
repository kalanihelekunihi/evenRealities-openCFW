/* Apollo terminal_action_query, native 0x5e9900. */
#include <stdint.h>

extern uint32_t audio_terminal_display_queue_handle; /* native RAM 0x20074a90 */
extern uint8_t audio_terminal_ui_mode; /* native RAM 0x2006e345 */
extern uint32_t audio_terminal_message_session_matches(uint32_t,const char *);
extern uint32_t audio_td_session_struct_copy_out(const void *);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_query";
static const char ignored[]="ignore terminal query outside main page: ui=%d state=%d session=%lu";
static const char ignored_short[]="[terminal.pb]ignore terminal query outside main page: ui=%d state=%d session=%lu";
static const char query[]="query";
static const char received[]="recv terminal query id=%d: question=%s";
static const char received_short[]="[terminal.pb]recv terminal query id=%d: question=%s";
static const char option[]="option[%d(id=%u)]:%s";
static const char option_short[]="[terminal.pb]option[%d(id=%u)]:%s";

static uint16_t load_u16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_command_5e9900(const void *payload,uint32_t length) {
    (void)length;
    if(payload==0) return UINT32_MAX;
    const uint8_t *p=payload;
    uint32_t session=load_u32(p+0x848u);
    if(audio_terminal_display_queue_handle==0u || audio_terminal_ui_mode!=7u) {
        uint32_t has_queue=audio_terminal_display_queue_handle!=0u;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,628u,ignored,
                               has_queue,audio_terminal_ui_mode,session);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08c00000u,ignored_short,ignored_short,
                                        has_queue,audio_terminal_ui_mode,session);
        return 0u;
    }
    if(audio_terminal_message_session_matches(session,query)==0u) return 0u;
    (void)audio_td_session_struct_copy_out(payload);
    uint32_t query_id=load_u32(p);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,636u,received,query_id,p+6u);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,received_short,received_short,
                                    query_id,p+6u);
    uint32_t count=load_u16(p+0x406u);
    for(uint32_t i=0u;i<count;++i) {
        const uint8_t *row=p+i*0x88u;
        uint32_t option_id=load_u32(row+0x408u);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,638u,option,
                               i,option_id,row+0x40eu);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0cc00000u,option_short,option_short,
                                        i,option_id,row+0x40eu);
    }
    (void)audio_terminal_request_display(21u,0u);
    return 0u;
}
