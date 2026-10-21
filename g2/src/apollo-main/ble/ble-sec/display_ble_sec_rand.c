/* Native SecRand 0x53634e; pinned Cordio sec_main.c. */
#include <stdint.h>
extern uint8_t audio_ble_stack_state_20072cb8[];
extern void HciLeRandCmd(void);

void SecRand(uint8_t *destination, uint8_t length)
{
    uint8_t *const state=audio_ble_stack_state_20072cb8;
    uint8_t index=(uint8_t)(state[0x3au]<<3u);
    uint8_t count=length;
    while (length--) {
        *destination++=state[index];
        index=(index==31u)?0u:(uint8_t)(index+1u);
    }
    uint8_t requests=(uint8_t)(((uint32_t)count+7u)/8u);
    while (requests--) {
        HciLeRandCmd();
        state[0x3au]=(state[0x3au]>=3u)?0u:(uint8_t)(state[0x3au]+1u);
    }
}
