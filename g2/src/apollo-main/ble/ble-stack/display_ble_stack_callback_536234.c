/* Native BLE stack event callback 0x536234 with WsfMsgDeq 0x4bf9ec and
 * WsfQueueDeq 0x538c4a. The source-owned secCb base is 0x20072cb8. */
#include <stdint.h>

extern uint8_t audio_ble_stack_state_20072cb8[];
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern void WStrReverse(uint8_t *,uint8_t);
extern void WsfMsgFree(void *);
extern void WsfCsEnter(void);
extern void WsfCsExit(void);

void *audio_ble_wsf_queue_dequeue(void *queue)
{
    uint8_t *head;
    WsfCsEnter();
    __builtin_memcpy(&head,queue,4u);
    if (head!=0) {
        uint8_t *next;
        __builtin_memcpy(&next,head,4u);
        __builtin_memcpy(queue,&next,4u);
        if (next==0) {
            uint32_t zero=0u;
            __builtin_memcpy((uint8_t *)queue+4u,&zero,4u);
        }
    }
    WsfCsExit();
    return head;
}

void *audio_ble_wsf_msg_dequeue(void *queue,uint8_t *handler)
{
    uint8_t *node=audio_ble_wsf_queue_dequeue(queue);
    if (node==0) return 0;
    *handler=node[4u];
    return node+8u;
}

void audio_ble_stack_callback_536234(uint8_t *event)
{
    uint8_t *base=audio_ble_stack_state_20072cb8;
    uint8_t handler=0u;
    uint8_t *message=0;
    switch (event[2u]) {
    case 0x1cu: {
        uint8_t index=base[0x39u];
        (void)audio_queue_copy_bytes(base+(uint32_t)index*8u,event+5u,8u);
        base[0x39u]=index>=3u?0u:(uint8_t)(index+1u);
        break;
    }
    case 0x1bu:
        message=audio_ble_wsf_msg_dequeue(base+0x20u,&handler);
        /* Original dereferences a null dequeue result on this event. */
        if (message[0x34u]==3u || message[0x34u]==1u ||
            message[0x34u]==4u)
            WStrReverse(event+5u,16u);
        break;
    case 0x25u:
        message=audio_ble_wsf_msg_dequeue(base+0x28u,&handler);
        break;
    case 0x26u:
        message=audio_ble_wsf_msg_dequeue(base+0x30u,&handler);
        break;
    case 0x14u:
        while ((message=audio_ble_wsf_msg_dequeue(base+0x28u,&handler))!=0)
            WsfMsgFree(message);
        while ((message=audio_ble_wsf_msg_dequeue(base+0x30u,&handler))!=0)
            WsfMsgFree(message);
        while ((message=audio_ble_wsf_msg_dequeue(base+0x20u,&handler))!=0)
            WsfMsgFree(message);
        break;
    default:
        break;
    }
    if (message!=0) {
        uint8_t state=message[0x34u];
        uint32_t callback_word;
        __builtin_memcpy(&callback_word,base+0x3cu+(uint32_t)state*4u,4u);
        ((void (*)(void *,void *,uint8_t))(uintptr_t)callback_word)(message,event,handler);
    }
}
