/* Native SmpScCmac 0x56cec2, pinned Cordio smp_sc_main.c. */
#include <stdint.h>
extern uint8_t audio_ble_smp_handler_state[]; /* selected live SMP state 0x20070aec */
extern uint8_t SecCmac(const uint8_t *key,uint8_t *text,uint16_t length,
                       uint8_t handler,uint16_t connection,uint8_t event);
extern void WsfBufFree(void *block);
extern void smpSmExecute(void *ccb,void *message);
void SmpScCmac(const uint8_t *key,uint8_t *text,uint8_t length,
               void *ccb,uint8_t *message) {
    uint8_t connection=((const uint8_t *)ccb)[0x3du];
    if (SecCmac(key,text,length,audio_ble_smp_handler_state[0xecu],
                connection,0x1cu)==0u) {
        WsfBufFree(text);
        message[3]=8u;
        message[2]=3u;
        smpSmExecute(ccb,message);
    }
}
