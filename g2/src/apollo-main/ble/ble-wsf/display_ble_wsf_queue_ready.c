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
void WsfTaskSetReady(uint8_t handler,uint8_t bit) {
    (void)handler; /* native body uses only the ready-bit argument */
    WsfCsEnter();
    audio_wsf_task_state[0x3cu]|=bit;
    WsfCsExit();
    WsfSetOsSpecificEvent();
}

/* Former duplicate bodies (ble/wsf-msg/display_wsf_msg_children.c) now bind here. */
__typeof__(WsfTaskMsgQueue) audio_wsf_task_msg_queue __attribute__((alias("WsfTaskMsgQueue")));
__typeof__(WsfTaskSetReady) audio_wsf_task_set_ready __attribute__((alias("WsfTaskSetReady")));
