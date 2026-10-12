/* Native smpScFailWithReattempt 0x56d304. Its 8-byte WSF event frame begins
 * with the incoming R2/R3 stack words; the child defines only selected bytes.
 * Preserve the actual entry register values instead of inventing C defaults. */
#include <stdint.h>
extern void SmpScGetCancelMsgWithReattempt(uint8_t,void *,uint8_t);
extern void smpSmExecute(void *,void *);
__attribute__((used,noinline))
static void audio_ble_smp_sc_fail_retry_body(void *ccb,uint8_t *frame) {
    SmpScGetCancelMsgWithReattempt(((const uint8_t *)ccb)[0x3du],frame,4u);
    smpSmExecute(ccb,frame);
}
__attribute__((naked)) void smpScFailWithReattempt(void *ccb __attribute__((unused))) {
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "mov r4, r0\n"
        "mov r1, sp\n"
        "bl audio_ble_smp_sc_fail_retry_body\n"
        "pop {r0, r1, r4, pc}\n");
}
