/* Authenticated Apollo appDbHandlerResume 0x4b5a44 and WSF wrapper 0x533ebc. */
#include <stdint.h>

extern volatile uint8_t audio_ble_adv_resume_state_20074f38[];
extern uint32_t audio_ble_adv_route_ready_52c628(uint8_t,uint8_t);
extern uint32_t audio_ble_att_write_request(uint8_t,uint16_t,uint8_t,uint32_t,
                                            uint32_t,uint8_t,uint8_t);

void audio_ble_adv_send_533ebc(uint8_t connection,uint16_t event,
                                uint16_t length,const void *payload)
{
    (void)audio_ble_att_write_request(connection,event,0u,length,
                                       (uint32_t)(uintptr_t)payload,0x1du,0u);
}

uint32_t audio_ble_dm_advertising_resume_4b5a44(uint8_t connection,
                                                  uint16_t value,
                                                  uint16_t reason,
                                                  uint32_t inactive_return)
{
    if (audio_ble_adv_resume_state_20074f38[0] == 0u)
        return inactive_return;

    uint32_t payload=(uint32_t)value | ((uint32_t)reason << 16);
    uint8_t route=audio_ble_adv_resume_state_20074f38[1];
    if (connection == 0u) {
        for (uint8_t index=1u;index<4u;++index) {
            if (audio_ble_adv_route_ready_52c628(index,route)!=0u)
                audio_ble_adv_send_533ebc(index,0x12u,4u,&payload);
        }
    } else if (audio_ble_adv_route_ready_52c628(connection,route)!=0u) {
        audio_ble_adv_send_533ebc(connection,0x12u,4u,&payload);
    }
    return payload;
}
