/* Apollo terminal_action_error_msg, native 0x5e9b08. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_td_notify_state_clear(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_error_msg";
static const char message[]="recv terminal error msg: err_code=%d";
static const char short_message[]="[terminal.pb]recv terminal error msg: err_code=%d";

uint32_t audio_terminal_command_5e9b08(const void *payload,uint32_t length) {
    (void)length;
    if(payload==0) return UINT32_MAX;
    uint8_t code=*(const uint8_t *)payload;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,661u,message,code);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04400000u,short_message,short_message,code);
    if(code==2u) {
        audio_td_notify_state_clear();
        (void)audio_terminal_request_display(12u,0u);
    }
    return 0;
}
