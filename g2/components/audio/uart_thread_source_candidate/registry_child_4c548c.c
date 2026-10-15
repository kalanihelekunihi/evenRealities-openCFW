/* Native Thread_SendMsgToRingTaskWithId wrapper at 0x4c548c. */
#include <stdint.h>

extern int32_t audio_uart_ring_task_msg_send(uint32_t id,const void *data,
                                              uint32_t length); /* selected 0x4c549c */

void audio_uart_registry_child_4c548c(uint32_t payload,uint16_t length) {
    (void)audio_uart_ring_task_msg_send(2u,(const void *)(uintptr_t)payload,
                                        (uint32_t)length);
}
