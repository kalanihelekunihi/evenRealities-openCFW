/* Cordio app_slave.c appAdvStart with product OTA gate, native 0x4b42f0.
 * The slave config pointer at 0x20074350 is live application RAM. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern const uint8_t *audio_ble_slave_profile_slot; /* native pointer cell 0x20074350 */
extern int ble_ota_mode_get(void);
extern uint8_t appSlaveConnectableAdv(uint8_t count,const uint8_t *handles);
extern uint8_t appNumConns(uint8_t role);
extern void DmAdvSetInterval(uint8_t handle,uint16_t minimum,uint16_t maximum);
extern void DmAdvConfig(uint8_t handle,uint8_t type,uint8_t peer_type,const uint8_t *peer);
extern void appSetAdvScanData(uint8_t handle,uint8_t mode);
extern void DmAdvStart(uint8_t count,const uint8_t *handles,const uint16_t *duration,
                       const uint8_t *maximum_events);

void appAdvStart(uint8_t count,const uint8_t *handles,const uint16_t *interval,
                 const uint16_t *duration,const uint8_t *maximum_events,
                 uint8_t configure)
{
    if (ble_ota_mode_get()) return;
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    uint8_t connectable=appSlaveConnectableAdv(count,handles);
    uint8_t active=appNumConns(1u);
    if (!connectable || active<audio_ble_slave_profile_slot[0]) {
        for (uint8_t i=0u;i<count;i++) {
            uint8_t h=handles[i];
            if (configure) {
                DmAdvSetInterval(h,interval[i],interval[i]);
                DmAdvConfig(h,state[0x59u+h],state[0x6au+h],state+0x5eu+(uint32_t)h*6u);
            }
            if (!state[0x55u+h]) appSetAdvScanData(h,state[0x5du]);
        }
        DmAdvStart(count,handles,duration,maximum_events);
    } else {
        for (uint8_t i=0u;i<count;i++) state[0x57u+handles[i]]=3u;
    }
}
