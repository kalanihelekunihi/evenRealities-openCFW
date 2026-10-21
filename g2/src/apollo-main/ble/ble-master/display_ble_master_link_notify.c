/* Apollo DM link notification chain 0x4bb21c, 0x47ae78, 0x47b4ce,
 * 0x4d28f0 and 0x4d293c. */
#include <stdint.h>

extern uint8_t audio_ble_dm_handler_state[];
extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgSend(uint8_t,void *);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);

uint32_t audio_ble_link_mask_select_47ae78(uint32_t address,uint8_t mask,
                                           uint8_t *selected)
{
    uint8_t *record=(uint8_t *)(uintptr_t)address;
    if ((record[0x2eu]&mask)==0u) return 0u;
    switch (mask) {
    case 1u:*selected=record[0x4eu];return address+0x34u;
    case 2u:*selected=record[0x6au];return address+0x50u;
    case 4u:return address+7u;
    case 8u:return address+0x1eu;
    default:return 0u;
    }
}

void audio_ble_connection_state_set_47b4ce(uint32_t address,uint8_t state)
{
    *(volatile uint8_t *)(uintptr_t)(address+0x31u)=state;
}

void audio_ble_copy_address6_4d293c(void *destination,const void *source)
{
    (void)audio_queue_copy_bytes(destination,source,6u);
}

void audio_ble_dm_state_notify_4d28f0(uint8_t connection,
                                        const void *address,uint8_t state)
{
    uint8_t *message=(uint8_t *)WsfMsgAlloc(12u);
    if (message==0) return;
    message[2]=0x35u;
    message[4]=connection;
    audio_ble_copy_address6_4d293c(message+5u,address);
    message[0x0bu]=state;
    WsfMsgSend(audio_ble_dm_handler_state[0x0cu],message);
}

void audio_ble_master_child_4bb21c(uint32_t address)
{
    if (address==0u) return;
    const uint8_t *record=(const uint8_t *)(uintptr_t)address;
    if (record[0x31u]==0u || record[0x32u]!=0u) return;
    uint32_t link=audio_ble_link_mask_select_47ae78(address,4u,0);
    if (link==0u) return;
    const uint8_t *selected=(const uint8_t *)(uintptr_t)link;
    audio_ble_dm_state_notify_4d28f0(selected[0x16u],selected+0x10u,1u);
    audio_ble_connection_state_set_47b4ce(address,0u);
}
