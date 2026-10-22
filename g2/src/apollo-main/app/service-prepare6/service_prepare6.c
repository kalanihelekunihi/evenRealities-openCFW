/* Native ring-status peer synchronization0x47d818. */
#include <stdint.h>
extern uint32_t audio_uart_ring_mac_ready(void); /* 0x4a2fdc */
extern uint32_t audio_uart_ring_active(void); /* 0x4a2914 */
extern void audio_uart_ring_sync_idle(void); /* 0x47cf28 */
extern void audio_uart_ring_sync_active(void); /* 0x47ced6 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                                uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ux.setting";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\app\\ux\\ux_system\\ux_system.c";
static const char function_name[]="RPC_SyncRingStatusWithPeer";
static const char message[]="RPC_SyncRingStatusWithPeer skip, ring mac not set";
static const char short_message[]=
 "[ux.setting]RPC_SyncRingStatusWithPeer skip, ring mac not set";

/* Stock 0x47D818 (RPC_SyncRingStatusWithPeer) */
void audio_uart_service_prepare6(void) {
    if(audio_uart_ring_mac_ready()==0u) {
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source_file,function_name,0xfdu,
                               message);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10000000u,short_message,
                                        short_message);
    } else if(audio_uart_ring_active()==0u) {
        audio_uart_ring_sync_idle();
    } else {
        audio_uart_ring_sync_active();
    }
}
