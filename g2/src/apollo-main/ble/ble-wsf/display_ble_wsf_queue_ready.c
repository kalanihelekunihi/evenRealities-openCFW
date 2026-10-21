/* Native WsfTaskMsgQueue 0x52b97c, WsfMsgEnq 0x4bf9de,
 * WsfTaskSetReady 0x52b95e. Product WSF task RAM remains external. */
#include <stdint.h>
extern uint8_t audio_wsf_task_state[]; /* live task state */
extern void WsfQueueEnq(void *,void *);
extern void WsfCsEnter(void);
extern void WsfCsExit(void);
extern void WsfSetOsSpecificEvent(void);
void *WsfTaskMsgQueue(void) {
    return audio_wsf_task_state+0x34u;
}
void WsfMsgEnq(void *queue,uint8_t handler,void *message) {
    uint8_t *payload=(uint8_t *)message;
    payload[-4]=handler;
    WsfQueueEnq(queue,payload-8);
}
void WsfTaskSetReady(uint8_t handler,uint8_t bit) {
    (void)handler; /* native body uses only the ready-bit argument */
    WsfCsEnter();
    audio_wsf_task_state[0x3cu]|=bit;
    WsfCsExit();
    WsfSetOsSpecificEvent();
}
