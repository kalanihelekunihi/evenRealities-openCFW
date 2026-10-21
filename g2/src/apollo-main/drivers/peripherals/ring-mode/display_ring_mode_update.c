/* Native 0x472362: forward the low 16 bits to ring task message 0x1000. */
#include <stdint.h>
extern int32_t audio_uart_ring_task_msg_send(uint32_t,const void *,uint32_t); /* selected 0x4c549c */
int32_t audio_uart_ring_mode_update_472362(uint32_t mode) {
    uint16_t value=(uint16_t)mode;
    return (int8_t)audio_uart_ring_task_msg_send(0x1000u,&value,2u);
}
