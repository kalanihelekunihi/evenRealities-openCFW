/* Native pairMgrSecAuthFlagSet/Get 0x4bb9b4/0x4bb9bc and PB time reset 0x4bbf44. */
#include <stdint.h>
extern uint8_t audio_ble_pair_auth_flag_20074ffc; /* live product RAM */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_ble_ring_policy_deadline_200748fc; /* live RAM */
extern uint8_t audio_ble_ring_policy_pending_2007500b; /* live RAM */
extern void audio_ble_ring_policy_enter_state(uint8_t); /* _EnterState 0x49f0da */
extern void audio_ble_ring_policy_delayed(void); /* 0x49f500 */
extern void audio_event_loop_remove_delayed(void (*)(void));
void audio_ble_ring_connect_policy_reset(void);
void pairMgrSecAuthFlagSet(uint8_t value) {audio_ble_pair_auth_flag_20074ffc=value;}
uint8_t pairMgrSecAuthFlagGet(void) {return audio_ble_pair_auth_flag_20074ffc;}
void PB_LastTxEncodeRingConnectInfoTimeSet(uint32_t value) {
    if(value!=0u)return;
    static const char module[]="pb.devc";
    static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_dev_config\\pb_service_pair_mgr.c";
    static const char function[]="PB_LastTxEncodeRingConnectInfoTimeSet";
    static const char message[]="PB_LastTxEncodeRingConnectInfoTimeSet(0): reset ring connect policy";
    static const char compact[]="[pb.devc]PB_LastTxEncodeRingConnectInfoTimeSet(0): reset ring connect policy";
    if(audio_log_flags()&2u)
        audio_log_extended(3u,module,path,function,0x169u,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x0c000000u,compact,compact);
    audio_ble_ring_connect_policy_reset();
}
void audio_ble_ring_connect_policy_reset(void) {
    static const char module[]="ring.policy";
    static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_connect_policy.c";
    static const char function[]="RING_ConnectPolicyReset";
    static const char message[]="[RingPolicy] reset all policy state";
    static const char compact[]="[ring.policy][RingPolicy] reset all policy state";
    if(audio_log_flags()&2u)
        audio_log_extended(2u,module,path,function,0xf6u,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x08000000u,compact,compact);
    audio_ble_ring_policy_enter_state(0u);
    audio_ble_ring_policy_deadline_200748fc=0u;
    audio_ble_ring_policy_pending_2007500b=0u;
    audio_event_loop_remove_delayed(audio_ble_ring_policy_delayed);
}
