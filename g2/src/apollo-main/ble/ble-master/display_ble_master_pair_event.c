/* Apollo master pair event 0x503b24 and WSF messages 0x4b6e14/0x4b6e46. */
#include <stdint.h>

extern volatile uint32_t audio_ble_master_pair_mode_cell_20000444;
extern uint8_t audio_ble_dm_handler_state[];
extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgSend(uint8_t,void *);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);

void audio_ble_master_pair_payload_4b6e14(uint8_t connection,
                                           const void *payload)
{
    uint8_t *message=(uint8_t *)WsfMsgAlloc(16u);
    if (message==0) return;
    message[2]=0x22u;
    message[0]=connection;
    message[1]=0u;
    (void)audio_queue_copy_bytes(message+4u,payload,12u);
    WsfMsgSend(audio_ble_dm_handler_state[0x0cu],message);
}

void audio_ble_master_pair_status_4b6e46(uint8_t connection,uint8_t status)
{
    uint8_t *message=(uint8_t *)WsfMsgAlloc(6u);
    if (message==0) return;
    message[2]=0x23u;
    message[0]=connection;
    message[1]=0u;
    message[4]=status;
    WsfMsgSend(audio_ble_dm_handler_state[0x0cu],message);
}

void audio_ble_master_event_503b24(void *event,void *record)
{
    const uint8_t *source=(const uint8_t *)event;
    const uint8_t *row=(const uint8_t *)record;
    uint32_t mode_pointer=audio_ble_master_pair_mode_cell_20000444;
    uint8_t mode=*(const volatile uint8_t *)(uintptr_t)mode_pointer;
    if (mode==0u) {
        uint8_t payload[12]={0};
        for (unsigned i=0;i<8u;++i) payload[i]=source[i+6u];
        audio_ble_master_pair_payload_4b6e14(row[4],payload);
    } else {
        mode_pointer=audio_ble_master_pair_mode_cell_20000444;
        mode=*(const volatile uint8_t *)(uintptr_t)mode_pointer;
        if (mode==1u)
            audio_ble_master_pair_status_4b6e46(row[4],0x11u);
    }
}
