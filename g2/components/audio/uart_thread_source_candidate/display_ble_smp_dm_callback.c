/* Native Cordio smpDmConnCback 0x537502. Event offsets are the native
 * dmEvt_t byte layout, including its 16-bit connection and close reason. */
#include <stdint.h>
extern uint8_t *smpCcbByConnId(uint8_t);
extern uint8_t audio_dm_conn_role(uint8_t);
extern uint8_t SmpDbGetFailureCount(uint8_t);
extern void SmpDbSetFailureCount(uint8_t,uint8_t);
extern void smpResumeAttemptsState(uint8_t);
extern void smpSmExecute(uint8_t *,const uint8_t *);
extern void audio_ble_wsf_message_free(void *);
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void wr32(uint8_t *p,uint32_t x){p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);p[2]=(uint8_t)(x>>16);p[3]=(uint8_t)(x>>24);}
uint32_t audio_ble_smp_dm_conn_callback_537502(const uint8_t *event,
                                                uint32_t ignored_a,uint32_t ignored_b,
                                                uint32_t inherited){
    (void)ignored_a;(void)ignored_b;
    const uint8_t connection=event[0];
    uint8_t *ccb=smpCcbByConnId(connection);
    if(event[2]==0x27u){
        if(audio_dm_conn_role(connection)==0u){ccb[0x3au]=1u;ccb[0x3fu]=0x0bu;}
        else{ccb[0x3au]=0u;ccb[0x3fu]=1u;}
        ccb[0x38u]=event[6];ccb[0x39u]=event[7];
        ccb[0x3du]=connection;ccb[0x3bu]=0u;ccb[0x3cu]=0u;
        ccb[0x42u]=SmpDbGetFailureCount(connection);
        ccb[0x43u]=0u;ccb[0x3eu]=0u;ccb[0x44u]=0u;
        smpResumeAttemptsState(connection);
    }else if(ccb[0x3du]!=0u&&event[2]==0x28u){
        SmpDbSetFailureCount(connection,ccb[0x42u]);
        inherited=(uint32_t)event[0]|((uint32_t)event[1]<<8)|
                  (0x0au<<16)|((uint32_t)(uint8_t)(event[8]+0x20u)<<24);
        smpSmExecute(ccb,(const uint8_t *)&inherited);
        ccb[0x3du]=0u;
        const uint32_t queued=rd32(ccb+0x34u);
        if(queued!=0u){audio_ble_wsf_message_free((void *)(uintptr_t)queued);wr32(ccb+0x34u,0u);}
    }
    return inherited;
}
