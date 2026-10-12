/* Native SmpDmMsgSend 0x537bd6: route the prepared packet to the SMP handler. */
#include <stdint.h>
extern uint8_t audio_ble_smp_handler_state[0xfcu]; /* selected RAM 0x20070aec */
extern void WsfMsgSend(uint8_t,void *);
void SmpDmMsgSend(void *message) {
    WsfMsgSend(audio_ble_smp_handler_state[0xecu],message);
}
