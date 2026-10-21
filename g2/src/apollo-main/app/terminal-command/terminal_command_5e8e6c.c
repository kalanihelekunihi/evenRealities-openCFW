/* Apollo terminal_action_asr_result, native 0x5e8e6c. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_mode; /* native RAM 0x2006e345 */
extern uint32_t audio_td_ring_write(const void *);
extern const uint8_t *audio_td_state_ptr(void);
extern void audio_td_notify_state_clear(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_asr_result";
static const char result_message[]="recv terminal asr result len: %d: sentence_final=%d all_final=%d";
static const char result_short[]="[terminal.pb]recv terminal asr result len: %d: sentence_final=%d all_final=%d";
static const char text_message[]="%s";
static const char text_short[]="[terminal.pb]%s";
static const char invalid_message[]="invalid ASR state: all_final arrived before release/timeout, ignored";
static const char invalid_short[]="[terminal.pb]invalid ASR state: all_final arrived before release/timeout, ignored";
static const char empty_message[]="ASR final with empty cached text after release/timeout, back to idle";
static const char empty_short[]="[terminal.pb]ASR final with empty cached text after release/timeout, back to idle";

uint32_t audio_terminal_command_5e8e6c(const void *payload,uint32_t length) {
    (void)length;
    if(payload==0) return UINT32_MAX;
    const uint8_t *data=payload;
    uint32_t text_length=(uint32_t)data[0]|((uint32_t)data[1]<<8);
    uint32_t sentence_final=data[0x202u];
    uint32_t all_final=data[0x203u];
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,401u,result_message,
                           text_length,sentence_final,all_final);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0cc00000u,result_short,result_short,
                                    text_length,sentence_final,all_final);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,402u,text_message,data+2u);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,text_short,text_short,data+2u);
    if(all_final!=0u && audio_terminal_ui_mode==4u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,405u,invalid_message);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,invalid_short,invalid_short);
        return 0;
    }
    (void)audio_td_ring_write(payload);
    const uint8_t *state=audio_td_state_ptr();
    uint32_t has_cached=all_final!=0u && state!=0 &&
                        ((uint32_t)state[0x802u]|((uint32_t)state[0x803u]<<8))!=0u;
    if(all_final!=0u && has_cached==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,416u,empty_message);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,empty_short,empty_short);
        audio_td_notify_state_clear();
        (void)audio_terminal_request_display(12u,0u);
    } else {
        (void)audio_terminal_request_display(has_cached!=0u?11u:10u,0u);
    }
    return 0;
}
