/* Native smpResumeAttemptsState 0x53749c. SC flag comes from the actual SMP
 * handler-state producer at RAM 0x20070aec, not a new product default. */
#include <stdint.h>
extern uint8_t *smpCcbByConnId(uint8_t);
extern uint32_t SmpDbGetPairingDisabledTime(uint8_t);
extern uint8_t audio_dm_conn_role(uint8_t);
extern uint8_t audio_ble_smp_handler_state[];
extern void WsfTimerStartMs(void *,uint32_t);
void smpResumeAttemptsState(uint8_t connection){
    uint8_t *ccb=smpCcbByConnId(connection);
    const uint32_t disabled_time=SmpDbGetPairingDisabledTime(connection);
    if(disabled_time==0u)return;
    const uint8_t role=audio_dm_conn_role(connection);
    ccb[0x3eu]=audio_ble_smp_handler_state[0xf8u]==0u?
               (role==1u?0x0du:0x0cu):(role==1u?0x26u:0x24u);
    ccb[0x1au]=0x10u;
    WsfTimerStartMs(ccb+0x10u,disabled_time);
}
