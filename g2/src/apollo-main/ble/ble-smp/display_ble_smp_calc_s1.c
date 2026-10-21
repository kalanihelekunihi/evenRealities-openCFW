/* Native smpCalcS1 0x537998, pinned Cordio smp_main.c. */
#include <stdint.h>
extern uint8_t audio_ble_smp_handler_state[];
extern void Calc128Cpy64(uint8_t *destination, const uint8_t *source);
extern uint8_t SecAes(uint8_t *key, uint8_t *plain, uint8_t handler,
                      uint16_t connection, uint8_t event);
extern void smpSmExecute(uint8_t *ccb, void *event);

void smpCalcS1(uint8_t *ccb, uint8_t *key, uint8_t *rand1, uint8_t *rand2)
{
    uint8_t value[16];
    Calc128Cpy64(value,rand2);
    Calc128Cpy64(value+8u,rand1);
    const uint8_t token=SecAes(key,value,audio_ble_smp_handler_state[0xecu],
                               ccb[0x3du],0x0bu);
    ccb[0x41u]=token;
    if (token==0xffu) {
        uint8_t event[4]={0x0bu,0u,3u,8u};
        smpSmExecute(ccb,event);
    }
}
