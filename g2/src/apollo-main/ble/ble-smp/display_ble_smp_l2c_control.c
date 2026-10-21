/* Native Cordio smpL2cCtrlCback 0x537444. */
#include <stdint.h>
extern uint8_t *smpCcbByConnId(uint8_t);
extern void smpSendPkt(uint8_t *,void *);
extern uint8_t smpStateIdle(const uint8_t *);
extern void smpSmExecute(uint8_t *,const uint8_t *);
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void wr32(uint8_t *p,uint32_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);}
uint32_t audio_ble_smp_l2c_control_callback_537444(uint8_t *message,
                                                    uint32_t ignored_a,uint32_t ignored_b,
                                                    uint32_t inherited){
    (void)ignored_a;(void)ignored_b;
    uint8_t *ccb=smpCcbByConnId(message[0]);
    if(ccb[0x3du]!=0u){
        ccb[0x3cu]=(message[2]==1u);
        if(ccb[0x3cu]==0u){
            uint32_t pending=rd32(ccb+0x34u);
            if(pending!=0u){
                wr32(ccb+0x34u,0u);
                smpSendPkt(ccb,(void *)(uintptr_t)pending);
            }
            if(smpStateIdle(ccb)==0u){message[2]=0x0cu;smpSmExecute(ccb,message);}
        }
    }
    return inherited;
}
