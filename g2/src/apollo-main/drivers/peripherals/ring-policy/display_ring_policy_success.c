/* Native RING_ConnectPolicyNotifyConnectSuccessSoon 0x49f646. */
#include <stdint.h>
extern uint8_t audio_ble_ring_policy_pending_2007500b; /* RAM 0x2007500b */
extern void audio_ble_ring_policy_delayed(void); /* selected 0x49f500 */
extern uint32_t audio_ble_master_success_delayed(uint32_t); /* selected 0x4bc418 */
extern uint32_t audio_event_loop_remove_delayed(void (*)(void)); /* selected 0x476ace */
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t); /* selected 0x47697e */
extern uint32_t audio_uart_ring_active(void); /* selected 0x4a2914 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ring.policy";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_connect_policy.c";
static const char function[]="RING_ConnectPolicyNotifyConnectSuccessSoon";
static const char message[]="[RingPolicy] schedule connect success notify in %ums";
static const char compact[]="[ring.policy][RingPolicy] schedule connect success notify in %ums";
void audio_ble_ring_policy_notify_success_49f646(void) {
    void (*const callback)(void)=(void (*)(void))audio_ble_master_success_delayed;
    audio_ble_ring_policy_pending_2007500b=0u;
    (void)audio_event_loop_remove_delayed(audio_ble_ring_policy_delayed);
    (void)audio_event_loop_remove_delayed(callback);
    if(audio_uart_ring_active()!=0u) {
        audio_event_loop_push_delayed(callback,0u,200u);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0xf1u,message,200u);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,compact,compact,200u);
    }
}
