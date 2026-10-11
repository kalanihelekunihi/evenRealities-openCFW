/* Native WsfMsgEnq 0x4bf9de, WsfTaskMsgQueue 0x52b97c,
 * and WsfTaskSetReady 0x52b95e, using authenticated Cordio RAM layout. */
#include <stdint.h>
extern uint8_t audio_wsf_task_state[]; /* live RAM base 0x20073230; queue +0x34, ready +0x3c */
extern void audio_wsf_queue_enqueue(void *,void *); /* native WsfQueueEnq 0x538c24 */
extern void audio_wsf_cs_enter(void); /* native WsfCsEnter */
extern void audio_wsf_cs_exit(void); /* native WsfCsExit */
extern void audio_wsf_set_os_event(void); /* native WsfSetOsSpecificEvent */
void *audio_wsf_task_msg_queue(uint8_t handler) {
    (void)handler;
    return audio_wsf_task_state+0x34u;
}
void audio_wsf_msg_enqueue(void *queue,uint8_t handler,void *message) {
    uint8_t *header=(uint8_t *)message-8u;
    header[4u]=handler;
    audio_wsf_queue_enqueue(queue,header);
}
void audio_wsf_task_set_ready(uint8_t handler,uint8_t flag) {
    (void)handler;
    audio_wsf_cs_enter();
    audio_wsf_task_state[0x3cu]|=flag;
    audio_wsf_cs_exit();
    audio_wsf_set_os_event();
}
