/* Terminal voice timeout start, stock 0x5e7ed4..0x5e7f25. */
#include <stdint.h>
extern uint8_t audio_terminal_ui_timer_state_20073c38[0x18];
extern uint32_t g2_flashdb_candidate_tick(void); /* osKernelGetTickCount */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="terminal.timer";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_timer.c";
static const char function[]="terminal_timer_voice_timeout_start";
static const char message[]="voice timeout start, due in %d ms";
static const char short_message[]="[terminal.timer]voice timeout start, due in %d ms";

void audio_terminal_voice_timeout_start_5e7ed4(void) {
    uint8_t *s=audio_terminal_ui_timer_state_20073c38;
    const uint32_t interval=60000u;
    s[0]=1u;
    *(uint32_t *)(void *)(s+4u)=g2_flashdb_candidate_tick()+interval;
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x32u,message,interval);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,short_message,
                                    short_message,interval);
}
