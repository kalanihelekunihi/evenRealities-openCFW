/* Apollo master pair event 0x503b24 and WSF messages 0x4b6e14/0x4b6e46. */
#include <stdint.h>

extern volatile uint32_t audio_ble_master_pair_mode_cell_20000444;
extern uint8_t audio_ble_dm_handler_state[];
extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgSend(uint8_t,void *);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);

extern void audio_ble_master_pair_payload_4b6e14(uint8_t connection, const void *payload); /* opencfw U5: now provided by the Cordio unit */

extern void audio_ble_master_pair_status_4b6e46(uint8_t connection,uint8_t status); /* opencfw U5: now provided by the Cordio unit */

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
