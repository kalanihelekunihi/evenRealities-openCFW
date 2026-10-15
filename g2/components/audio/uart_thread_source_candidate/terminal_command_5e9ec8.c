/* Apollo terminal_action_new_session_result, native 0x5e9ec8. */
#include <stdint.h>

extern void audio_terminal_reset_output_tracking(void);
extern void audio_td_record_flags_clear_all(void);
extern void audio_td_ring_reset_wrapper(void);
extern void audio_td_notify_state_clear(void);
extern void audio_td_session_struct_clear(void);
extern void audio_td_flag_set_with_reset(uint8_t);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_new_session_result";
static const char message[]="recv terminal new session result=%d";
static const char short_message[]="[terminal.pb]recv terminal new session result=%d";

uint32_t audio_terminal_command_5e9ec8(const void *payload,uint32_t length) {
    (void)length;
    if(payload==0) return UINT32_MAX;
    uint8_t result=*(const uint8_t *)payload;
    if(result==0u) {
        audio_terminal_reset_output_tracking();
        audio_td_record_flags_clear_all();
        audio_td_ring_reset_wrapper();
        audio_td_notify_state_clear();
        audio_td_session_struct_clear();
        audio_td_flag_set_with_reset(1u);
    } else {
        audio_td_flag_set_with_reset(0u);
    }
    (void)audio_terminal_request_display(result==0u?32u:33u,0u);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,778u,message,result);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,short_message,short_message,result);
    return 0;
}
