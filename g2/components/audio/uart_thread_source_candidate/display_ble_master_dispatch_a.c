/* Apollo master communication event dispatcher 0x503b92. */
#include <stdint.h>

extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern volatile uint8_t audio_ble_subsystem_state_20071670[];
extern void audio_ble_master_event_50366e(void *,void *);
extern void audio_ble_master_event_50367c(void *,void *);
extern void audio_ble_master_event_5037bc(void *,void *);
extern void audio_ble_master_event_5037c4(void *,void *);
extern void audio_ble_master_event_5037d0(void *,void *);
extern void audio_ble_master_event_50393e(void *,void *);
extern void audio_ble_master_event_503b24(void *,void *);

void audio_ble_comm_master_dispatch_a(void *message)
{
    const uint8_t *bytes=(const uint8_t *)message;
    uint8_t event=bytes[2];
    uint16_t connection=(uint16_t)bytes[0]|((uint16_t)bytes[1]<<8);
    void *record=0;
    if ((event==0x27u || event==0x28u || event==0x40u) &&
        connection!=0u && connection<4u)
        record=audio_ble_discovery_connection_records_200717b0+
               ((uint32_t)connection-1u)*0x30u;

    switch (event) {
    case 0x20u:audio_ble_subsystem_state_20071670[0x9du]=0xffu;break;
    case 0x24u:case 0x4au:audio_ble_master_event_50366e(message,record);break;
    case 0x25u:case 0x4bu:audio_ble_master_event_50367c(message,record);break;
    case 0x26u:case 0x4cu:audio_ble_master_event_5037bc(message,record);break;
    case 0x27u:audio_ble_master_event_5037c4(message,record);break;
    case 0x28u:audio_ble_master_event_5037d0(message,record);break;
    case 0x37u:audio_ble_master_event_50393e(message,record);break;
    case 0x40u:audio_ble_master_event_503b24(message,record);break;
    default:break;
    }
}
