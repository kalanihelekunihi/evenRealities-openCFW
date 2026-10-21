/* Start response timer for a TD session, stock 0x597596..0x597651. */
#include <stdint.h>

extern uint8_t *audio_td_current_record(uint32_t);
extern uint32_t audio_uart_ring_rtc_refresh(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.data";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_data.c";
static const char function[]="terminal_data_start_response_timer";
static const char failed[]="response timer start failed: session=%lu";
static const char failed_short[]="[terminal.data]response timer start failed: session=%lu";
static const char started[]="response timer start: session=%lu utc=%lu";
static const char started_short[]="[terminal.data]response timer start: session=%lu utc=%lu";

void audio_td_session_activate_597596(uint32_t session) {
    uint8_t *record=audio_td_current_record(session);
    if (record==0) {
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x15fu,failed,session);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,failed_short,failed_short,session);
        return;
    }
    uint32_t utc=audio_uart_ring_rtc_refresh();
    record[0x88u]=(uint8_t)utc;
    record[0x89u]=(uint8_t)(utc>>8);
    record[0x8au]=(uint8_t)(utc>>16);
    record[0x8bu]=(uint8_t)(utc>>24);
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x164u,started,session,utc);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,started_short,started_short,session,utc);
}
