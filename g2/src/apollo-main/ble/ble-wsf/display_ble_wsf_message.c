/* Native WsfMsgAlloc 0x4bf99e and WsfMsgSend 0x4bf9ba. */
#include <stdint.h>
extern void *WsfBufAlloc(uint16_t); /* native 0x530446, real WSF pool child */
extern void *WsfTaskMsgQueue(void); /* native 0x52b97c */
extern void WsfMsgEnq(void *,uint8_t,void *); /* native 0x4bf9de */
extern void WsfTaskSetReady(uint8_t,uint8_t); /* native 0x52b95e */
void *WsfMsgAlloc(uint16_t size) {
    uint8_t *block=(uint8_t *)WsfBufAlloc((uint16_t)(size+8u));
    return block?block+8u:0;
}
void WsfMsgSend(uint8_t handler,void *message) {
    void *queue=WsfTaskMsgQueue();
    WsfMsgEnq(queue,handler,message);
    WsfTaskSetReady(handler,1u);
}
