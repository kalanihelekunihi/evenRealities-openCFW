/* Pinned Cordio app_slave.c/app_main.c, native Main 0x4b32e2 and 0x4bacf0. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern uint8_t DmConnRole(uint8_t connection);

uint8_t appSlaveConnectableAdv(uint8_t count,const uint8_t *handles)
{
    for (uint8_t i=0u;i<count;i++) {
        for (uint8_t h=0u;h<2u;h++) {
            uint8_t type=audio_ble_subsystem_link_state_200719c8[0x59u+h];
            if (handles[i]==h && (type==0u || type==4u || type==5u)) return 1u;
        }
    }
    return 0u;
}

uint8_t appNumConns(uint8_t role)
{
    uint8_t count=0u;
    for (uint8_t i=0u;i<3u;i++) {
        uint8_t connection=audio_ble_discovery_connection_records_200717b0[(uint32_t)i*0x30u+4u];
        if (connection && DmConnRole(connection)==role) count++;
    }
    return count;
}
