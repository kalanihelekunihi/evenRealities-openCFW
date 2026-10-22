/* Native ring policy state 0x49f0da and delayed timeout 0x49f500. */
#include <stdint.h>
extern uint8_t audio_ble_ring_policy_state_2007408c[]; /* live RAM: state byte, tick word at +4, retry byte +8 */
extern uint8_t audio_ble_ring_policy_pending_2007500b;
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t g2_flashdb_candidate_tick(void); /* selected osKernelGetTickCount 0x4490cc */
extern uint32_t PB_TxEncodeNotifyRingConnectInfo(uint32_t);
uint32_t audio_ble_ring_policy_tick_now(void);
static const char module[]="ring.policy";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_connect_policy.c";
/* Stock 0x49F0DA (_EnterState) */
void audio_ble_ring_policy_enter_state(uint8_t state) {
    static const char function[]="_EnterState";
    static const char message[]="[RingPolicy] state %d -> %d";
    static const char compact[]="[ring.policy][RingPolicy] state %d -> %d";
    uint8_t previous=audio_ble_ring_policy_state_2007408c[0];
    if(audio_log_flags()&2u)
        audio_log_extended(3u,module,path,function,0x60u,message,previous,state);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x0c800000u,compact,compact,previous,state);
    audio_ble_ring_policy_state_2007408c[0]=state;
    uint32_t tick=state?audio_ble_ring_policy_tick_now():0u;
    for(uint32_t i=0u;i<4u;i++)audio_ble_ring_policy_state_2007408c[4u+i]=(uint8_t)(tick>>(8u*i));
    audio_ble_ring_policy_state_2007408c[8u]=0u;
}
/* Stock 0x49F020 (_ring_policy_tick_now) */
uint32_t audio_ble_ring_policy_tick_now(void) {return g2_flashdb_candidate_tick();}
/* Stock 0x49F500 (_ringReconnectTimeoutFire) */
void audio_ble_ring_policy_delayed(void) {
    static const char function[]="_ringReconnectTimeoutFire";
    static const char message[]="[RingPolicy] reconnect timeout %ums reached, notify app ring connect failed";
    static const char compact[]="[ring.policy][RingPolicy] reconnect timeout %ums reached, notify app ring connect failed";
    audio_ble_ring_policy_pending_2007500b=0u;
    if(audio_log_flags()&2u)
        audio_log_extended(2u,module,path,function,0xcbu,message,20000u);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x08400000u,compact,compact,20000u);
    PB_TxEncodeNotifyRingConnectInfo(0x5au);
}
