/* Native smpScFailWithReattempt 0x56d304 (upstream Cordio smp_sc_main.c).
 * The event is a WSF message header on the stack; SmpScGetCancelMsgWithReattempt
 * defines all four header bytes. The stock 8-byte frame started out holding the
 * caller's R2/R3 words; here the unused tail is zero. */
#include <stdint.h>
extern void SmpScGetCancelMsgWithReattempt(uint8_t,void *,uint8_t);
extern void smpSmExecute(void *,void *);
void smpScFailWithReattempt(void *ccb) {
    uint8_t frame[8] __attribute__((aligned(4))) = {0u};
    SmpScGetCancelMsgWithReattempt(((const uint8_t *)ccb)[0x3du],frame,4u);
    smpSmExecute(ccb,frame);
}
