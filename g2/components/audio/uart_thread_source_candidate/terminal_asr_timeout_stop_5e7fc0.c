/* Stock ASR-result timeout stop, 0x5e7fc0..0x5e8007. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_timer_state_20073c38[0x18];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.timer";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_timer.c";
static const char function[]="terminal_timer_asr_result_timeout_stop";
static const char message[]="asr result timeout stop";
static const char short_message[]="[terminal.timer]asr result timeout stop";

void audio_terminal_asr_timeout_stop_5e7fc0(void) {
    uint8_t *active=audio_terminal_ui_timer_state_20073c38+8u;
    if (*active==0u)return;
    *active=0u;
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x4du,message);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,short_message,short_message);
}
