/* Pinned Cordio dm_adv.c DmAdvStart/DmAdvSetInterval;
 * native Main 0x4b31ea and 0x4b3292. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[]; /* dmCb RAM 0x20073b78 */
extern uint8_t audio_ble_dm_adv_control[]; /* dmAdvCb RAM 0x20073394 */
extern uint8_t *WsfMsgAlloc(uint16_t length);
extern void WsfMsgSend(uint8_t handler,void *message);
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
static void set16(uint8_t *p,uint16_t v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u); }

void DmAdvStart(uint8_t count,const uint8_t *handles,
                const uint16_t *duration,const uint8_t *maximum_events)
{
    uint8_t *message=WsfMsgAlloc(0x0eu);
    if (!message) return;
    message[2u]=2u;
    message[4u]=count;
    for (uint8_t i=0u;i<count;i++) {
        message[5u+i]=handles[i];
        set16(message+8u+(uint32_t)i*2u,duration[i]);
        message[0x0cu+i]=maximum_events[i];
    }
    WsfMsgSend(audio_ble_dm_handler_state[0x0cu],message);
}

void DmAdvSetInterval(uint8_t handle,uint16_t minimum,uint16_t maximum)
{
    WsfTaskLock();
    set16(audio_ble_dm_adv_control+0x10u+(uint32_t)handle*2u,minimum);
    set16(audio_ble_dm_adv_control+0x14u+(uint32_t)handle*2u,maximum);
    WsfTaskUnlock();
}
