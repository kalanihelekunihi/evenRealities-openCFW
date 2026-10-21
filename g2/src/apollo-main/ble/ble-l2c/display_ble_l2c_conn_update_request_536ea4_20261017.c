/* Cordio L2cDmConnUpdateReq at stock Main 0x536ea4. */
#include <stdint.h>

extern uint8_t audio_ble_l2c_slave_state[];
extern uint8_t audio_ble_l2c_state[];
extern uint8_t DmConnIdByHandle(uint16_t);
extern void WsfTimerStartSec(void *, uint32_t);
extern uint8_t *audio_ble_l2c_msg_alloc_530b28(uint16_t);
extern void L2cDataReq(uint16_t, uint16_t, uint16_t, uint8_t *);

void audio_ble_l2c_conn_update_request_536ea4(uint16_t handle,
                                                const uint8_t *connection_spec)
{
    uint8_t connection = DmConnIdByHandle(handle);
    if (connection == 0u)
        return;
    audio_ble_l2c_slave_state[0x10u + connection] = 0x12u;
    WsfTimerStartSec(audio_ble_l2c_slave_state, 30u);
    audio_ble_l2c_slave_state[8] = (uint8_t)handle;
    audio_ble_l2c_slave_state[9] = (uint8_t)(handle >> 8);
    uint8_t *packet = audio_ble_l2c_msg_alloc_530b28(20u);
    if (packet == 0)
        return;
    uint8_t identifier = audio_ble_l2c_state[0x24u];
    packet[8] = 0x12u;
    packet[9] = identifier;
    audio_ble_l2c_slave_state[0x13u + connection] = identifier;
    audio_ble_l2c_state[0x24u] = identifier == 0xffu ? 1u :
                                  (uint8_t)(identifier + 1u);
    packet[10] = 8u;
    packet[11] = 0u;
    for (uint32_t i = 0u; i < 8u; ++i)
        packet[12u + i] = connection_spec[i];
    L2cDataReq(5u, handle, 12u, packet);
}
