/* Pinned Cordio app_slave.c appSetAdvScanData, native Main 0x4b3514. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern void appSetAdvScanDataFrag(uint8_t handle,uint8_t location);
static uint16_t get16(const uint8_t *p) { return (uint16_t)p[0]|((uint16_t)p[1]<<8u); }
/* Stock 0x4B3514 (appSetAdvScanData; upstream third-party/upstream/cordio/ble-profiles/sources/af/app_slave.c) */
void appSetAdvScanData(uint8_t handle,uint8_t mode)
{
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    uint8_t adv=(uint8_t)(mode*2u),scan=(uint8_t)(adv+1u);
    uint8_t *const offsets=state+0x40u+(uint32_t)handle*8u;
    uint8_t *const lengths=state+0x20u+(uint32_t)handle*8u;
    if (get16(offsets+(uint32_t)adv*2u)<get16(lengths+(uint32_t)adv*2u))
        appSetAdvScanDataFrag(handle,adv);
    if (get16(offsets+(uint32_t)scan*2u)<get16(lengths+(uint32_t)scan*2u))
        appSetAdvScanDataFrag(handle,scan);
    if (get16(offsets+(uint32_t)adv*2u)>=get16(lengths+(uint32_t)adv*2u) &&
        get16(offsets+(uint32_t)scan*2u)>=get16(lengths+(uint32_t)scan*2u))
        state[0x55u+handle]=1u;
}
