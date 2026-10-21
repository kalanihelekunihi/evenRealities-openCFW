/* Native Packetcraft Cordio WsfMsgAlloc 0x4bf99e and WsfMsgSend 0x4bf9ba. */
#include <stdint.h>
extern void *audio_wsf_buffer_alloc(uint16_t); /* native WsfBufAlloc 0x530446 */
extern void *audio_wsf_task_msg_queue(uint8_t); /* native WsfTaskMsgQueue 0x52b97c */
extern void audio_wsf_msg_enqueue(void *,uint8_t,void *); /* native WsfMsgEnq 0x4bf9de */
extern void audio_wsf_task_set_ready(uint8_t,uint8_t); /* native WsfTaskSetReady 0x52b95e */
void *audio_wsf_msg_alloc(uint16_t size) {
    uint8_t *block=(uint8_t *)audio_wsf_buffer_alloc((uint16_t)(size+8u));
    return block==0?0:block+8u;
}
void audio_wsf_msg_send(uint8_t handler,void *message) {
    void *queue=audio_wsf_task_msg_queue(handler);
    audio_wsf_msg_enqueue(queue,handler,message);
    audio_wsf_task_set_ready(handler,1u);
}
