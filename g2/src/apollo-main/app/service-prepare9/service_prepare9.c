/* Native dashboard slave report0x501066. */
#include <stdint.h>
extern uint32_t audio_uart_service_version(void); /* selected0x45a568 */
extern uint32_t audio_uart_pb_file_exists(void); /* 0x55876a */
extern void audio_uart_task_delay(uint32_t); /* 0x454b4c */
extern uint32_t audio_uart_handshake_send(uint32_t,const void *,uint32_t,
                                          uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                                uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="dashboard.ext";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_ext.c";
static const char function_name[]="dashboard_ext_report_pb_state_to_peer";
static const char message[]=
 "dashboard_ext: slave report pb file state to peer, exists=%d";
static const char short_message[]=
 "[dashboard.ext]dashboard_ext: slave report pb file state to peer, exists=%d";

/* Stock 0x501066 (dashboard_ext_report_pb_state_to_peer) */
void audio_uart_service_prepare9(uint32_t delay_first) {
    if(audio_uart_service_version()!=2u) return;
    uint32_t exists=audio_uart_pb_file_exists();
    uint8_t packet[6]={3u,(uint8_t)(exists!=0u),0u,0u,0u,0u};
    if(delay_first!=0u) audio_uart_task_delay(100u);
    (void)audio_uart_handshake_send(0x1fu,packet,6u,0u,5u);
    if(audio_log_flags()&2u)
        audio_log_extended(3u,module,source_file,function_name,0x1f1u,
                           message,exists);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x0c400000u,short_message,
                                    short_message,exists);
}
