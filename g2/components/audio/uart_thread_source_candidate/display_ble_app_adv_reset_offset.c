/* Pinned Cordio app_slave.c appSlaveResetAdvDataOffset, native 0x4b334c. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
static uint16_t get16(const uint8_t *p) { return (uint16_t)p[0]|((uint16_t)p[1]<<8u); }
static void set16(uint8_t *p,uint16_t n) { p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8u); }
void appSlaveResetAdvDataOffset(uint8_t handle)
{
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    uint32_t location=(uint32_t)state[0x5du]*4u;
    uint8_t *const adv=state+0x40u+(uint32_t)handle*8u+location;
    uint8_t *const scan=adv+2u;
    uint8_t sync=0u;
    if (get16(adv)!=0u) { set16(adv,0u);sync=1u; }
    if (get16(scan)!=0u) { set16(scan,0u);sync=1u; }
    if (sync) state[0x55u+handle]=0u;
}
